/*
 * SPDX-FileCopyrightText: 2025 Taytech AS
 *
 * SPDX-License-Identifier: MIT
 */

#include "at_mcu_update.h"
#include "esp_log.h"
#include "esp_partition.h"
#include "driver/gpio.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "esp_at.h"
#include "esp_at_core.h"

// User Config
#define STM32_BOOT_PIN          GPIO_NUM_12
#define STM32_RST_PIN           GPIO_NUM_13
#define MCU_PARTITION_LABEL     "mcu_fw"

// UART Config for STM32 Bootloader
#define AT_UART_PORT_NUM        UART_NUM_1
#define AT_TX_PIN               GPIO_NUM_5
#define AT_RX_PIN               GPIO_NUM_16
#define BUF_SIZE                1024
#define STM32_BL_BAUDRATE       115200 // Default for initiation, can be higher

static const char *TAG = "at-mcu-update";

// Progress Tracking
static uint32_t s_mcu_update_total_bytes = 0;
static uint32_t s_mcu_update_written_bytes = 0;
// Status: 0=Idle, 1=Running, 2=Done, -1=Error
static int s_mcu_update_status = 0; 
static char s_mcu_update_msg[64] = "Idle";

void at_mcu_update_get_status(int *status, uint32_t *written, uint32_t *total) {
    *status = s_mcu_update_status;
    *written = s_mcu_update_written_bytes;
    *total = s_mcu_update_total_bytes;
}

// AN3155 Protocol Helpers
static esp_err_t stm32_read_byte_logged(uint8_t *byte, uint32_t timeout_ms, const char* context) {
    int len = uart_read_bytes(AT_UART_PORT_NUM, byte, 1, pdMS_TO_TICKS(timeout_ms));
    if (len == 1) {
        // printf("MCU_UPD: UART RX (%s): 0x%02X\n", context, *byte);
        return ESP_OK;
    }
    printf("MCU_UPD: UART RX Timeout (%s)\n", context);
    return ESP_FAIL;
}

static esp_err_t stm32_wait_ack_logged(uint32_t timeout_ms, const char* cmd_name, bool verbose_success) {
    uint8_t byte = 0;
    if (stm32_read_byte_logged(&byte, timeout_ms, cmd_name) == ESP_OK) {
        if (byte == AN3155_ACK) {
             if (verbose_success) printf("MCU_UPD: UART RX: ACK (for %s)\n", cmd_name);
             return ESP_OK;
        }
        if (byte == AN3155_NACK) {
            printf("MCU_UPD: UART RX: NACK (for %s)\n", cmd_name);
            return ESP_FAIL;
        }
        printf("MCU_UPD: UART RX: 0x%02X (Expected ACK for %s)\n", byte, cmd_name);
    } else {
        printf("MCU_UPD: UART RX: Timeout (Expected ACK for %s)\n", cmd_name);
    }
    return ESP_FAIL;
}

static esp_err_t stm32_send_byte(uint8_t byte) {
    if (uart_write_bytes(AT_UART_PORT_NUM, (const char*)&byte, 1) != 1) {
        return ESP_FAIL;
    }
    return ESP_OK;
}

static esp_err_t stm32_read_byte(uint8_t *byte, uint32_t timeout_ms) {
    int len = uart_read_bytes(AT_UART_PORT_NUM, byte, 1, pdMS_TO_TICKS(timeout_ms));
    if (len == 1) return ESP_OK;
    return ESP_FAIL;
}

static esp_err_t stm32_wait_ack(uint32_t timeout_ms) {
    uint8_t byte = 0;
    if (stm32_read_byte(&byte, timeout_ms) == ESP_OK) {
        if (byte == AN3155_ACK) {
             ESP_LOGI(TAG, "UART RX: ACK");
             return ESP_OK;
        }
        if (byte == AN3155_NACK) {
            ESP_LOGW(TAG, "UART RX: NACK");
            return ESP_FAIL;
        }
        // Verbose log for unexpected
        ESP_LOGW(TAG, "UART RX: 0x%02X (Expected ACK)", byte);
    } else {
        ESP_LOGE(TAG, "UART RX: Timeout (Expected ACK)");
    }
    return ESP_FAIL;
}

static esp_err_t stm32_cmd_no_data(uint8_t cmd) {
    uint8_t xor_cmd = cmd ^ 0xFF;
    printf("MCU_UPD: UART TX: CMD 0x%02X\n", cmd);
    stm32_send_byte(cmd);
    stm32_send_byte(xor_cmd);
    return stm32_wait_ack_logged(200, "CMD", true); // Use logged version
}

static esp_err_t stm32_get_id(void) {
    printf("MCU_UPD: Command: Get ID\n");
    if (stm32_cmd_no_data(AN3155_CMD_GET_ID) != ESP_OK) return ESP_FAIL;
    
    // Read N (number of bytes - 1)
    uint8_t n;
    if (stm32_read_byte_logged(&n, 100, "ID Len") != ESP_OK) return ESP_FAIL;
    
    // Read ID bytes usually 2 bytes for STM32
    for (int i = 0; i <= n; i++) {
        uint8_t id_byte;
        stm32_read_byte_logged(&id_byte, 100, "ID Byte");
        printf("MCU_UPD: Chip ID Byte[%d]: 0x%02X\n", i, id_byte);
    }
    
    return stm32_wait_ack_logged(100, "GetID End", true);
}

static esp_err_t stm32_disable_write_protection(void) {
    printf("MCU_UPD: Command: Disable Write Protection (0x73)\n");
    if (stm32_cmd_no_data(AN3155_CMD_WRITE_UNPROTECT) != ESP_OK) {
        printf("MCU_UPD: Write Unprotect Refused (or already unprotected)\n");
        return ESP_OK; // Proceed anyway, might fail later if critical
    }
    
    // Command 0x73 flow: CMD -> ACK -> ACK (Unprotect done) -> System Reset (on some chips)
    // Actually AN3155 says: "The Write Unprotect command removes the write protection... ACK byte is returned."
    // IMPORTANT: A System Reset is generated automatically by the system!
    // We must expect a lost connection or need to Re-Sync.
    
    printf("MCU_UPD: Write Unprotect command accepted. Waiting for ACK...\n");
    if (stm32_wait_ack_logged(2000, "Write Unprotect", true) != ESP_OK) {
        return ESP_FAIL;
    }
    
    printf("MCU_UPD: Write Protection Disabled. System might reset.\n");
    // We should probably re-sync after this if a reset occurs.
    vTaskDelay(pdMS_TO_TICKS(1000));
    return ESP_OK;
}

// Global Erase (0x44).
// Sequence: Command (0x44) -> ACK -> 0xFF 0xFF (Global) -> Checksum -> ACK
static esp_err_t stm32_erase_all(void) {
    printf("MCU_UPD: Command: Extended Erase (0x44)\n");
    
    // 1. Send Command 0x44
    if (stm32_cmd_no_data(AN3155_CMD_EXT_ERASE) != ESP_OK) {
        printf("MCU_UPD: Extended Erase Refused\n");
        return ESP_FAIL;
    }
    
    // 2. Send Global Erase params (0xFF 0XFF) & Checksum (0x00)
    // 0xFF 0xFF -> Special code for Global Mass Erase
    // Checksum = 0xFF ^ 0xFF = 0x00
    uint8_t params[] = {0xFF, 0xFF}; 
    uint8_t checksum = 0x00;
    
    printf("MCU_UPD: UART TX: Ext Erase Params 0xFF 0xFF + Checksum 0x00\n");
    uart_write_bytes(AT_UART_PORT_NUM, (const char*)params, 2);
    stm32_send_byte(checksum);
    
    // 3. Wait for Erase Complete ACK
    printf("MCU_UPD: Waiting for erase to complete (may take seconds)...\n");
    esp_err_t ret = stm32_wait_ack_logged(30000, "Erase Complete", true); // 30s timeout
    
    if (ret != ESP_OK) {
        printf("MCU_UPD: Erase Operation Failed (No ACK)\n");
    } else {
        printf("MCU_UPD: Erase Successful (ACK Received)\n");
    }
    return ret;
}

static esp_err_t stm32_write_mem(uint32_t address, const uint8_t *data, uint8_t len) {
    for (int retry = 0; retry < 3; retry++) {
        uart_flush_input(AT_UART_PORT_NUM); // Clear any garbage

        // 1. Send Write Memory Command
        if (stm32_cmd_no_data(AN3155_CMD_WRITE_MEM) != ESP_OK) {
            printf("MCU_UPD: WriteMem Cmd Failed (Retry %d)\n", retry);
            continue;
        }
        
        // Brief delay before Address
        vTaskDelay(pdMS_TO_TICKS(10));

        // 2. Send Address
        uint8_t addr_bytes[4];
        addr_bytes[0] = (address >> 24) & 0xFF;
        addr_bytes[1] = (address >> 16) & 0xFF;
        addr_bytes[2] = (address >> 8) & 0xFF;
        addr_bytes[3] = (address >> 0) & 0xFF;
        
        uint8_t xor = addr_bytes[0] ^ addr_bytes[1] ^ addr_bytes[2] ^ addr_bytes[3];
        uart_write_bytes(AT_UART_PORT_NUM, (const char*)addr_bytes, 4);
        stm32_send_byte(xor);
        
        if (stm32_wait_ack_logged(100, "Addr", true) != ESP_OK) {
            printf("MCU_UPD: WriteMem Address 0x%X Failed (Retry %d)\n", address, retry);
            continue;
        }
        
        // 3. Send Data
        uint8_t n = len - 1;
        xor = n;
        stm32_send_byte(n);
        
        for (int i = 0; i < len; i++) {
            stm32_send_byte(data[i]);
            xor ^= data[i];
        }
        stm32_send_byte(xor);
        
        printf("MCU_UPD: Sent Data Block. Len=%d, Checksum=0x%02X. Waiting ACK...\n", len, xor);

        if (stm32_wait_ack_logged(2000, "Data", true) == ESP_OK) {
            return ESP_OK; // Success
        } else {
             printf("MCU_UPD: WriteMem Data Failed (Retry %d) at 0x%X\n", retry, address);
        }
    }
    
    return ESP_FAIL;
}


// --- Modified helper to allow silent/throttled writes ---
static esp_err_t stm32_write_mem_throttled(uint32_t address, const uint8_t *data, uint8_t len, bool log_enable) {
    for (int retry = 0; retry < 3; retry++) {
        uart_flush_input(AT_UART_PORT_NUM); // Clear any garbage

        // 1. Send Write Memory Command
        uint8_t cmd = AN3155_CMD_WRITE_MEM;
        uint8_t xor_cmd = cmd ^ 0xFF;
        
        if (log_enable) printf("MCU_UPD: UART TX: CMD 0x%02X\n", cmd);
        stm32_send_byte(cmd);
        stm32_send_byte(xor_cmd);
        
        if (stm32_wait_ack_logged(200, "CMD", log_enable) != ESP_OK) {
             if (log_enable) printf("MCU_UPD: WriteMem Cmd Failed (Retry %d)\n", retry);
             continue;
        }
        
        // Brief delay before Address
        vTaskDelay(pdMS_TO_TICKS(10));

        // 2. Send Address
        uint8_t addr_bytes[4];
        addr_bytes[0] = (address >> 24) & 0xFF;
        addr_bytes[1] = (address >> 16) & 0xFF;
        addr_bytes[2] = (address >> 8) & 0xFF;
        addr_bytes[3] = (address >> 0) & 0xFF;
        
        uint8_t xor = addr_bytes[0] ^ addr_bytes[1] ^ addr_bytes[2] ^ addr_bytes[3];
        uart_write_bytes(AT_UART_PORT_NUM, (const char*)addr_bytes, 4);
        stm32_send_byte(xor);
        
        if (stm32_wait_ack_logged(100, "Addr", log_enable) != ESP_OK) {
             if (log_enable) printf("MCU_UPD: WriteMem Address 0x%X Failed (Retry %d)\n", address, retry);
             continue;
        }
        
        // 3. Send Data
        uint8_t n = len - 1;
        xor = n;
        stm32_send_byte(n);
        
        for (int i = 0; i < len; i++) {
            stm32_send_byte(data[i]);
            xor ^= data[i];
        }
        stm32_send_byte(xor);
        
        if (log_enable) printf("MCU_UPD: Sent Data Block. Len=%d, Checksum=0x%02X. Waiting ACK...\n", len, xor);

        if (stm32_wait_ack_logged(2000, "Data", log_enable) == ESP_OK) {
            return ESP_OK; // Success
        } else {
             if (log_enable) printf("MCU_UPD: WriteMem Data Failed (Retry %d) at 0x%X\n", retry, address);
        }
    }
    
    return ESP_FAIL;
}


void at_mcu_update_init(void)
{
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_DISABLE,
        .mode = GPIO_MODE_OUTPUT,
        .pin_bit_mask = (1ULL << STM32_BOOT_PIN) | (1ULL << STM32_RST_PIN),
        .pull_down_en = 0,
        .pull_up_en = 0,
    };
    gpio_config(&io_conf);

    // Default: Run mode (BOOT0=0, RST=1)
    gpio_set_level(STM32_BOOT_PIN, 0);
    gpio_set_level(STM32_RST_PIN, 1);
    
    printf("MCU_UPD: MCU Update GPIOs Initialized\n");
}

// Helper to setup UART
static void stm32_setup_uart(void) {
    printf("MCU_UPD: UART: Setup at 115200 8E1\n");
    uart_driver_delete(AT_UART_PORT_NUM); // Force removal
    
    uart_config_t uart_config = {
        .baud_rate = STM32_BL_BAUDRATE,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_EVEN,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB,
    };
    uart_driver_install(AT_UART_PORT_NUM, BUF_SIZE * 2, 0, 0, NULL, 0);
    uart_param_config(AT_UART_PORT_NUM, &uart_config);
    uart_set_pin(AT_UART_PORT_NUM, AT_TX_PIN, AT_RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
}

// Helper to restore GPIOs (UART driver remains hijacked until reset)
static void stm32_cleanup_gpio(void) {
    printf("MCU_UPD: GPIO: Cleaning up sequence...\n");
    // Restore normal boot logic
    printf("MCU_UPD: GPIO: BOOT0 -> 0\n");
    gpio_set_level(STM32_BOOT_PIN, 0);
    
    printf("MCU_UPD: GPIO: NRST -> 0\n");
    gpio_set_level(STM32_RST_PIN, 0);
    vTaskDelay(pdMS_TO_TICKS(50));
    
    printf("MCU_UPD: GPIO: NRST -> 1\n");
    gpio_set_level(STM32_RST_PIN, 1);
}


static esp_err_t stm32_enter_bootloader_sync(void) {
    printf("MCU_UPD: GPIO: Starting Bootloader Sequence\n");
    
    printf("MCU_UPD: GPIO: BOOT0 -> 1\n");
    gpio_set_level(STM32_BOOT_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(50));
    
    printf("MCU_UPD: GPIO: NRST -> 0\n");
    gpio_set_level(STM32_RST_PIN, 0);
    vTaskDelay(pdMS_TO_TICKS(50));
    
    printf("MCU_UPD: GPIO: NRST -> 1 (BOOT0 is still 1)\n");
    gpio_set_level(STM32_RST_PIN, 1);
    
    // Initial wait to ensure bootloader is ready
    vTaskDelay(pdMS_TO_TICKS(500));

    uint8_t sync = 0x7F;
    bool synced = false;
    
    for (int i = 0; i < 5; i++) {
        printf("MCU_UPD: Sync Attempt %d...\n", i+1);
        uart_flush_input(AT_UART_PORT_NUM);
        
        printf("MCU_UPD: UART TX: 0x7F (Sync)\n");
        uart_write_bytes(AT_UART_PORT_NUM, (const char*)&sync, 1);
        
        if (stm32_wait_ack_logged(1000, "Sync", true) == ESP_OK) {
            synced = true;
            break;
        }
        printf("MCU_UPD: Sync attempt %d failed, retrying...\n", i+1);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    
    return synced ? ESP_OK : ESP_FAIL;
}

static void at_mcu_update_task(void *pvParameters)
{
    // Force INFO level logs for this tag to ensure debug visibility
    esp_log_level_set(TAG, ESP_LOG_INFO);
    
    s_mcu_update_status = 1; // Running
    s_mcu_update_written_bytes = 0;
    s_mcu_update_total_bytes = 0;
    snprintf(s_mcu_update_msg, sizeof(s_mcu_update_msg), "Starting...");

    printf("MCU_UPD: Starting MCU Update Sequence...\n");
    
    // 1. Find Partition
    const esp_partition_t *part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, 0x80, MCU_PARTITION_LABEL);
    if (!part) {
        printf("MCU_UPD: Partition '%s' not found!\n", MCU_PARTITION_LABEL);
        s_mcu_update_status = -1;
        goto exit;
    }
    s_mcu_update_total_bytes = part->size;

    // 2. Hijack UART
    stm32_setup_uart();

    // 3 & 4. Enter Bootloader & Sync
    if (stm32_enter_bootloader_sync() != ESP_OK) {
        printf("MCU_UPD: Sync Failed!\n");
        s_mcu_update_status = -1;
        goto exit_restore;
    }
    printf("MCU_UPD: Synced!\n");

    if (stm32_get_id() != ESP_OK) {
        printf("MCU_UPD: Get ID Failed!\n");
        goto exit_restore;
    }

    // 4b. Disable Write Protection (Optional, but safe)
    if (stm32_disable_write_protection() == ESP_OK) {
        printf("MCU_UPD: Write Protection Disabled. Re-syncing just in case...\n");
        // Re-enter/Verify bootloader state in case of auto-reset
        if (stm32_enter_bootloader_sync() != ESP_OK) {
             printf("MCU_UPD: Re-sync after unprotect failed. Continuing anyway...\n");
        }
    }

    // 5. Erase
    if (stm32_erase_all() != ESP_OK) {
        printf("MCU_UPD: Erase Failed!\n");
        s_mcu_update_status = -1;
        goto exit_restore;
    }
    printf("MCU_UPD: Flash Erased.\n");

    // 5b. Pulse Check - Verify connection is still alive after potentially long Erase
    printf("MCU_UPD: Verifying connection after Erase...\n");
    if (stm32_get_id() != ESP_OK) {
        printf("MCU_UPD: Connection lost after Erase! Attempting Re-sync (0x7F)...\n");
        
        bool resynced = false;
        uint8_t sync = 0x7F;
        for (int i = 0; i < 5; i++) {
             uart_flush_input(AT_UART_PORT_NUM);
             uart_write_bytes(AT_UART_PORT_NUM, (const char*)&sync, 1);
             if (stm32_wait_ack_logged(1000, "Re-Sync", true) == ESP_OK) {
                 resynced = true;
                 printf("MCU_UPD: Re-sync Successful!\n");
                 break;
             }
             vTaskDelay(pdMS_TO_TICKS(100));
        }
        
        if (!resynced) {
             printf("MCU_UPD: Critical Failure: Could not re-establish connection after Erase.\n");
             goto exit_restore;
        }
    } else {
        printf("MCU_UPD: Connection verified. Proceeding to Write.\n");
    }

    // 6. Write Loop
    uint8_t buffer[256];
    uint32_t offset = 0;
    uint32_t start_addr = 0x08000000; // STM32 Flash Base
    int block_count = 0;
    
    while (offset < part->size) {
        // Read from partition (Reduce chunk size to 128 for stability, 256 can be flaky)
        size_t read_len = (part->size - offset) > 128 ? 128 : (part->size - offset);
        if (esp_partition_read(part, offset, buffer, read_len) != ESP_OK) {
            printf("MCU_UPD: Partition Read Error at 0x%X\n", offset);
            break;
        }

        // Check if block is empty (0xFF) - optimization
        bool is_empty = true;
        for (int i=0; i<read_len; i++) {
            if (buffer[i] != 0xFF) {
                is_empty = false;
                break;
            }
        }

        if (!is_empty) {
            bool log_this_block = (block_count % 10 == 0);
            if (stm32_write_mem_throttled(start_addr + offset, buffer, read_len, log_this_block) != ESP_OK) {
                printf("MCU_UPD: Write failed at stm_addr 0x%X\n", start_addr + offset);
                s_mcu_update_status = -1;
                break;
            }
        }
        
        offset += read_len;
        s_mcu_update_written_bytes = offset;
        block_count++;
        // if (offset % 4096 == 0) { ... }
    }
    printf("MCU_UPD: Update Complete. Total: %d bytes.\n", offset);
    s_mcu_update_status = 2; // Done

exit_restore:
    stm32_cleanup_gpio();
    
    printf("MCU_UPD: Restarting ESP32 to restore AT functionality...\n");
    vTaskDelay(pdMS_TO_TICKS(1000));
    esp_restart();

exit:
    vTaskDelete(NULL);
}

esp_err_t at_mcu_check_bootloader(void) {
    esp_log_level_set(TAG, ESP_LOG_INFO);
    printf("MCU_UPD: Checking Bootloader Connection...\n");
    stm32_setup_uart();
    esp_err_t ret = stm32_enter_bootloader_sync();
    
    if (ret == ESP_OK) {
       printf("MCU_UPD: BOOTLOADER CHECK SUCCESS!\n");
    } else {
       printf("MCU_UPD: BOOTLOADER CHECK FAILED!\n");
    }
    
    stm32_cleanup_gpio();
    // No esp_restart() here! Caller must handle it or system behaves as is.
    // Note: UART driver is still hijacked, so AT commands won't work until reset.
    // We expect the web handler to trigger reset after responding.
    return ret;
}

void at_mcu_update_start_task(void)
{
    xTaskCreate(at_mcu_update_task, "mcu_upd", 4096, NULL, 5, NULL);
}

uint8_t at_mcu_update_cmd(uint8_t para_num) 
{
    // Simply start the task
    at_mcu_update_start_task();
    return ESP_AT_RESULT_CODE_OK; 
}
