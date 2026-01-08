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

// Defined by User
#define STM32_BOOT_PIN  GPIO_NUM_12
#define STM32_RST_PIN   GPIO_NUM_13
#define MCU_PARTITION_LABEL "mcu_fw"

static const char *TAG = "at-mcu-update";

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

    // Default state: BOOT0 Low (User Flash), RST High (Running)
    gpio_set_level(STM32_BOOT_PIN, 0);
    gpio_set_level(STM32_RST_PIN, 1);
    
    ESP_LOGI(TAG, "MCU Update GPIOs Initialized");
}

esp_err_t at_mcu_fw_write(const void *buffer, uint32_t len, uint32_t offset)
{
    const esp_partition_t *part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, 0x80, MCU_PARTITION_LABEL);
    if (!part) {
        ESP_LOGE(TAG, "MCU Firmware partition not found!");
        return ESP_FAIL;
    }

    // Erase before write if at start of partition
    // Optimize: only erase what is needed. For simplicity, web server usually sends sequential chunks.
    // Ideally, erase should be done when offset == 0 or handled by an abstraction that buffers.
    // CAUTION: esp_partition_write checks if flash is erased.
    // For OTA stream, we usually erase the whole partition at start.
    
    if (offset == 0) {
        ESP_LOGI(TAG, "Erasing MCU partition...");
        esp_partition_erase_range(part, 0, part->size); 
    }

    return esp_partition_write(part, offset, buffer, len);
}

#include "driver/uart.h"

// Defined by Factory Param (WROOM-32 Default)
#define AT_UART_PORT_NUM UART_NUM_1
#define AT_TX_PIN       GPIO_NUM_5
#define AT_RX_PIN       GPIO_NUM_16
#define BUF_SIZE        (1024)

void at_mcu_update_start(void *pvParameters)
{
    ESP_LOGI(TAG, "Starting MCU Update Task (Phase 2)...");

    // 1. Hijack UART from AT Core
    // We force delete the driver installed by AT core.
    // This will cause AT core to log errors if it tries to access UART, but we need exclusive control.
    ESP_LOGW(TAG, "Hijacking UART%d from AT Core...", AT_UART_PORT_NUM);
    uart_driver_delete(AT_UART_PORT_NUM);

    // 2. Re-initialize UART for STM32 Bootloader (115200, 8, E, 1)
    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_EVEN, // AN3155 requires Even Parity
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB,
    };
    
    // Install driver with buffer
    if (uart_driver_install(AT_UART_PORT_NUM, BUF_SIZE * 2, 0, 0, NULL, 0) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to install UART driver");
        vTaskDelete(NULL);
        return;
    }
    if (uart_param_config(AT_UART_PORT_NUM, &uart_config) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to configure UART param");
        vTaskDelete(NULL);
        return;
    }
    if (uart_set_pin(AT_UART_PORT_NUM, AT_TX_PIN, AT_RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set UART pins");
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG, "UART initialized for AN3155 protocol. Entering Bootloader...");

    // 3. Toggle Pins to Enter Bootloader
    gpio_set_level(STM32_BOOT_PIN, 1); // BOOT0 = High
    vTaskDelay(pdMS_TO_TICKS(50));
    gpio_set_level(STM32_RST_PIN, 0);  // Assert Reset
    vTaskDelay(pdMS_TO_TICKS(50));
    gpio_set_level(STM32_RST_PIN, 1);  // Release Reset
    vTaskDelay(pdMS_TO_TICKS(100));     // Wait for Bootloader Init

    // 4. Send Sync (0x7F)
    uint8_t sync_byte = 0x7F;
    uart_write_bytes(AT_UART_PORT_NUM, (const char*)&sync_byte, 1);
    
    // 5. Wait for ACK (0x79)
    uint8_t rx_data[16];
    int len = uart_read_bytes(AT_UART_PORT_NUM, rx_data, 1, pdMS_TO_TICKS(1000));
    
    if (len > 0 && rx_data[0] == 0x79) {
        ESP_LOGI(TAG, "STM32 Bootloader Synced (ACK Received)!");
        
        // TODO: Implement Full Erase/Write Loop here using Partitions
        // For now, we demonstrated control.
        // Reading from 'mcu_fw' partition -> sending blocks to UART.
        
        /* 
           Example Flow:
           1. Get ID (0x02, 0xFD) -> Expect ACK, N, ID, ACK
           2. Read Partition Header to verify? (Raw bin usually has no header)
           3. Global Erase (0x44) -> Send 0x44 0xBB -> Wait ACK -> Send 0xFF 0xFF 0x00 -> Wait ACK
           4. Write Memory (0x31) loops...
        */

    } else {
        ESP_LOGE(TAG, "Failed to Sync with STM32. RX: 0x%02x (Len: %d)", (len > 0 ? rx_data[0] : 0), len);
    }

    // 6. Restore / Cleanup
    // Since we messed up the AT Core's UART handle, the safest way to restore 
    // full functionality (and restart STM32 in App mode) is a System Reset.
    
    ESP_LOGW(TAG, "Update sequence finished. Restarting ESP32 to restore AT services...");
    vTaskDelay(pdMS_TO_TICKS(1000));
    
    // De-assert BOOT0 so MCU boots to app on power cycle/reset (if controlled by ESP EN?)
    // Actually, we should toggle RST pin again with BOOT0=0
    gpio_set_level(STM32_BOOT_PIN, 0);
    gpio_set_level(STM32_RST_PIN, 0);
    vTaskDelay(pdMS_TO_TICKS(20));
    gpio_set_level(STM32_RST_PIN, 1);
    
    esp_restart();
    
    // Should not reach here
    vTaskDelete(NULL);
}
