/*
 * SPDX-FileCopyrightText: 2024-2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * at_modbus_tcp_cmd.c - Modbus TCP to UART Bridge
 * 
 * This module implements a transparent TCP-UART bridge for Modbus TCP.
 * TCP data received on the configured port is forwarded to UART,
 * and UART responses are sent back to the TCP client.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#include <unistd.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "esp_at_core.h"
#include "esp_at.h"

#ifdef CONFIG_AT_MODBUSTCP_COMMAND_SUPPORT

#define MODBUS_TCP_PORT_DEFAULT         502
#define MODBUS_TCP_TIMEOUT_DEFAULT      60
#define MODBUS_TCP_BUFFER_SIZE          260     // Max Modbus TCP frame size (MBAP header 7 + PDU max 253)
#define MODBUS_TCP_TASK_STACK_SIZE      4096
#define MODBUS_TCP_TASK_PRIORITY        5
#define MODBUS_TCP_RECV_TIMEOUT_MS      100     // Socket receive timeout for polling

static const char *TAG = "at-modbustcp";

typedef enum {
    MODBUS_BRIDGE_STATE_STOPPED = 0,
    MODBUS_BRIDGE_STATE_LISTENING,
    MODBUS_BRIDGE_STATE_CONNECTED,
} modbus_bridge_state_t;

typedef struct {
    bool enabled;
    modbus_bridge_state_t state;
    int server_socket;
    int client_socket;
    uint16_t port;
    uint32_t timeout_sec;
    SemaphoreHandle_t uart_rx_sem;
    volatile bool stop_requested;
} modbus_tcp_bridge_t;

static modbus_tcp_bridge_t s_bridge = {
    .enabled = false,
    .state = MODBUS_BRIDGE_STATE_STOPPED,
    .server_socket = -1,
    .client_socket = -1,
    .port = MODBUS_TCP_PORT_DEFAULT,
    .timeout_sec = MODBUS_TCP_TIMEOUT_DEFAULT,
    .uart_rx_sem = NULL,
    .stop_requested = false,
};

// Forward declarations
static esp_err_t modbus_tcp_bridge_stop(void);

/**
 * @brief Send URC (Unsolicited Result Code) to AT port
 */
static void modbus_tcp_send_urc(const char *urc_msg)
{
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "+MODBUSTCP:%s\r\n", urc_msg);
    esp_at_port_active_write_data((uint8_t *)buffer, strlen(buffer));
}

/**
 * @brief Callback for UART data in specific mode
 */
static void modbus_uart_callback(void)
{
    // The explicit specific mode callback might be called from ISR.
    // Use FromISR variant to be safe.
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    if (s_bridge.uart_rx_sem) {
        xSemaphoreGiveFromISR(s_bridge.uart_rx_sem, &xHigherPriorityTaskWoken);
        if (xHigherPriorityTaskWoken == pdTRUE) {
            portYIELD_FROM_ISR();
        }
    }
}

/**
 * @brief Helper to log data in hex format
 */
static void log_hex(const char *direction, uint8_t *data, int len)
{
    if (len <= 0) return;
    
    // Allocate a buffer for the hex string (3 chars per byte + null terminator)
    // 0x00_ (5 chars) or 00_(3 chars). User asked for "0x00 0x03"
    // that is 5 chars per byte.
    // For large buffers this might be too big for stack, better print in chunks.
    
    char hex_buf[64]; 
    int pos = 0;
    
    printf("%s: ", direction);
    for (int i = 0; i < len; i++) {
        pos += snprintf(hex_buf + pos, sizeof(hex_buf) - pos, "0x%02X ", data[i]);
        if (pos >= sizeof(hex_buf) - 6 || i == len - 1) { // flush if full or done
            printf("%s", hex_buf);
            pos = 0;
        }
    }
    printf("\r\n");
}

/**
 * @brief Run Modbus TCP Bridge (Blocking)
 */
static void modbus_tcp_bridge_run(uint16_t port, uint32_t timeout_val)
{
    int server_fd = -1;
    int client_fd = -1;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    uint8_t *rx_buffer = NULL;
    int recv_len;
    struct timeval timeout;
    fd_set read_fds;
    uint8_t plus_count = 0;
    bool exit_sequence_detected = false;
    
    // Initialize bridge state
    s_bridge.enabled = true;
    s_bridge.port = port;
    s_bridge.timeout_sec = timeout_val;
    s_bridge.stop_requested = false;
    
    // Create semaphore
    if (s_bridge.uart_rx_sem == NULL) {
        s_bridge.uart_rx_sem = xSemaphoreCreateBinary();
    }
    
    ESP_LOGI(TAG, "Bridge starting on port %d...", s_bridge.port);
    
    // Allocate receive buffer
    rx_buffer = (uint8_t *)malloc(MODBUS_TCP_BUFFER_SIZE);
    if (rx_buffer == NULL) {
        ESP_LOGE(TAG, "Failed to allocate buffer");
        goto task_exit;
    }
    
    // Create server socket
    server_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_fd < 0) {
        ESP_LOGE(TAG, "Failed to create socket: errno %d", errno);
        goto task_exit;
    }
    
    // Set socket options
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // Bind socket
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(s_bridge.port);
    
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        ESP_LOGE(TAG, "Failed to bind socket: errno %d", errno);
        goto task_exit;
    }
    
    // Listen for connections (max 1 client)
    if (listen(server_fd, 1) < 0) {
        ESP_LOGE(TAG, "Failed to listen: errno %d", errno);
        goto task_exit;
    }
    
    s_bridge.server_socket = server_fd;
    s_bridge.state = MODBUS_BRIDGE_STATE_LISTENING;
    ESP_LOGI(TAG, "Listening on port %d", s_bridge.port);
    modbus_tcp_send_urc("LISTENING");
    
    // Set server socket to non-blocking for accept
    timeout.tv_sec = 1;
    timeout.tv_usec = 0;
    
    // Check for "+++" sequence (variables declared at top)

    while (!s_bridge.stop_requested && !exit_sequence_detected) {
        // Wait for client connection
        if (s_bridge.state == MODBUS_BRIDGE_STATE_LISTENING) {
            FD_ZERO(&read_fds);
            FD_SET(server_fd, &read_fds);
            timeout.tv_sec = 0;
            timeout.tv_usec = 100000; // 100ms
            
            int sel_ret = select(server_fd + 1, &read_fds, NULL, NULL, &timeout);
            if (sel_ret > 0 && FD_ISSET(server_fd, &read_fds)) {
                client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len);
                if (client_fd >= 0) {
                    s_bridge.client_socket = client_fd;
                    s_bridge.state = MODBUS_BRIDGE_STATE_CONNECTED;
                    ESP_LOGI(TAG, "Client connected");
                    modbus_tcp_send_urc("CONNECTED");
                    
                    // Set receive timeout for client socket
                    timeout.tv_sec = 0;
                    timeout.tv_usec = MODBUS_TCP_RECV_TIMEOUT_MS * 1000;
                    setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
                }
            }
        }
        
        // Handle connected client - TCP to UART
        if (s_bridge.state == MODBUS_BRIDGE_STATE_CONNECTED) {
            // Receive data from TCP client
            recv_len = recv(client_fd, rx_buffer, MODBUS_TCP_BUFFER_SIZE, 0);
            
            if (recv_len > 0) {
                // Forward data to UART (AT port)
                ESP_LOGD(TAG, "TCP->UART: %d bytes", recv_len);
                log_hex("TCP->UART", rx_buffer, recv_len);
                esp_at_port_write_data(rx_buffer, recv_len);
            } else if (recv_len == 0) {
                // Client disconnected
                ESP_LOGI(TAG, "Client disconnected");
                modbus_tcp_send_urc("DISCONNECTED");
                close(client_fd);
                s_bridge.client_socket = -1;
                s_bridge.state = MODBUS_BRIDGE_STATE_LISTENING;
            } else {
                // Check if it's just a timeout (no data available)
                if (errno != EAGAIN && errno != EWOULDBLOCK) {
                    ESP_LOGW(TAG, "Recv error: errno %d", errno);
                    modbus_tcp_send_urc("DISCONNECTED");
                    close(client_fd);
                    s_bridge.client_socket = -1;
                    s_bridge.state = MODBUS_BRIDGE_STATE_LISTENING;
                }
            }
        }

        // Check for UART data (triggered by callback via semaphore)
        // We use a non-blocking check or short wait
        if (xSemaphoreTake(s_bridge.uart_rx_sem, pdMS_TO_TICKS(10)) == pdTRUE) {
            ESP_LOGI(TAG, "Semaphore taken, checking UART data");
            int32_t uart_data_len = esp_at_port_get_data_length();
            ESP_LOGI(TAG, "UART data len: %d", uart_data_len);
            
            if (uart_data_len > 0) {
                // Limit read to buffer size
                int32_t to_read = (uart_data_len > MODBUS_TCP_BUFFER_SIZE) ? MODBUS_TCP_BUFFER_SIZE : uart_data_len;
                int32_t read_len = esp_at_port_read_data(rx_buffer, to_read);
                ESP_LOGI(TAG, "Read len: %d", read_len);
                
                if (read_len > 0) {
                    // Check for exit sequence "+++"
                    for (int i = 0; i < read_len; i++) {
                        if (rx_buffer[i] == '+') {
                            plus_count++;
                            if (plus_count >= 3) {
                                exit_sequence_detected = true;
                                break;
                            }
                        } else {
                            plus_count = 0;
                        }
                    }

                    if (exit_sequence_detected) {
                        break;
                    }

                    // Forward to TCP if connected
                    if (s_bridge.state == MODBUS_BRIDGE_STATE_CONNECTED && client_fd >= 0) {
                        ESP_LOGD(TAG, "UART->TCP: %ld bytes", read_len);
                        log_hex("UART->TCP", rx_buffer, read_len);
                        int sent = send(client_fd, rx_buffer, read_len, 0);
                        if (sent < 0) {
                            ESP_LOGW(TAG, "Send error: errno %d", errno);
                            modbus_tcp_send_urc("DISCONNECTED");
                            close(client_fd);
                            s_bridge.client_socket = -1;
                            s_bridge.state = MODBUS_BRIDGE_STATE_LISTENING;
                        }
                    }
                }
            }
        }
    }
    
    
task_exit:
    ESP_LOGI(TAG, "Bridge stopping");
    
    // Exit transparent mode
    esp_at_port_exit_specific();

    if (client_fd >= 0) close(client_fd);
    if (server_fd >= 0) close(server_fd);
    if (rx_buffer) free(rx_buffer);
    
    s_bridge.server_socket = -1;
    s_bridge.client_socket = -1;
    s_bridge.state = MODBUS_BRIDGE_STATE_STOPPED;
    s_bridge.enabled = false;
    
    if (s_bridge.uart_rx_sem) {
        vSemaphoreDelete(s_bridge.uart_rx_sem);
        s_bridge.uart_rx_sem = NULL;
    }
    
    // Send final result code if we are returning to AT mode explicitly
    // Note: The calling function will also return AT result
}

/**
 * @brief Helper to stop bridge (from other context if needed)
 */
static esp_err_t modbus_tcp_bridge_stop(void)
{
    s_bridge.stop_requested = true;
    return ESP_OK;
}

/**
 * @brief AT+MODBUSTCP=<enable>[,<port>,<timeout>]
 */
static uint8_t at_setup_cmd_modbustcp(uint8_t para_num)
{
    int32_t cnt = 0;
    int32_t enable = 0;
    int32_t port = MODBUS_TCP_PORT_DEFAULT;
    int32_t timeout = MODBUS_TCP_TIMEOUT_DEFAULT;
    
    // Parse enable parameter (required)
    if (esp_at_get_para_as_digit(cnt++, &enable) != ESP_AT_PARA_PARSE_RESULT_OK) {
        return ESP_AT_RESULT_CODE_ERROR;
    }
    
    if (enable < 0 || enable > 1) {
        return ESP_AT_RESULT_CODE_ERROR;
    }
    
    // Disable bridge
    if (enable == 0) {
        if (para_num != 1) {
            return ESP_AT_RESULT_CODE_ERROR;
        }
        if (modbus_tcp_bridge_stop() == ESP_OK) {
            return ESP_AT_RESULT_CODE_OK;
        }
        return ESP_AT_RESULT_CODE_ERROR;
    }
    
    // Enable bridge - parse optional parameters
    if (cnt < para_num) {
        if (esp_at_get_para_as_digit(cnt++, &port) != ESP_AT_PARA_PARSE_RESULT_OK) {
            return ESP_AT_RESULT_CODE_ERROR;
        }
        if (port < 1 || port > 65535) {
            return ESP_AT_RESULT_CODE_ERROR;
        }
    }
    
    if (cnt < para_num) {
        if (esp_at_get_para_as_digit(cnt++, &timeout) != ESP_AT_PARA_PARSE_RESULT_OK) {
            return ESP_AT_RESULT_CODE_ERROR;
        }
        if (timeout < 1 || timeout > 3600) {
            return ESP_AT_RESULT_CODE_ERROR;
        }
    }
    
    // Check for extra parameters
    if (cnt != para_num) {
        return ESP_AT_RESULT_CODE_ERROR;
    }

    // Send OK to indicate readiness (Optional, but good practice for transparent mode)
    // esp_at_response_result(ESP_AT_RESULT_CODE_OK); 
    // Wait, if we send result here, returning from function might double-send?
    // Usually transparent command sends "\r\nOK\r\n" then enters mode.
    // If we return PROCESS_DONE, AT Core won't send anything.
    
    // Enter specific mode NOW
    esp_at_port_enter_specific(modbus_uart_callback);
    
    // Explicitly send "OK" to tell client we are ready
    esp_at_port_write_data((uint8_t *)"\r\nOK\r\n", 6);
    
    // Run bridge (BLOCKING)
    modbus_tcp_bridge_run((uint16_t)port, (uint32_t)timeout);
    
    // When run returns, we have exited.
    // Return OK (or ERROR) to AT Core to clean up state
    return ESP_AT_RESULT_CODE_OK;
}

/**
 * @brief AT+MODBUSTCP?
 */
static uint8_t at_query_cmd_modbustcp(uint8_t *cmd_name)
{
    char buffer[64];
    const char *state_str;
    
    switch (s_bridge.state) {
        case MODBUS_BRIDGE_STATE_LISTENING:
            state_str = "LISTENING";
            break;
        case MODBUS_BRIDGE_STATE_CONNECTED:
            state_str = "CONNECTED";
            break;
        default:
            state_str = "STOPPED";
            break;
    }
    
    snprintf(buffer, sizeof(buffer), "%s:%d,%d,%lu,%s\r\n", 
             cmd_name, 
             s_bridge.enabled ? 1 : 0, 
             s_bridge.port, 
             (unsigned long)s_bridge.timeout_sec,
             state_str);
    esp_at_port_write_data((uint8_t *)buffer, strlen(buffer));
    return ESP_AT_RESULT_CODE_OK;
}

static const esp_at_cmd_struct s_at_modbus_tcp_cmd[] = {
    {"+MODBUSTCP", NULL, at_query_cmd_modbustcp, at_setup_cmd_modbustcp, NULL},
};

bool esp_at_modbus_tcp_cmd_regist(void)
{
    return esp_at_custom_cmd_array_regist(s_at_modbus_tcp_cmd, 
        sizeof(s_at_modbus_tcp_cmd) / sizeof(s_at_modbus_tcp_cmd[0]));
}

ESP_AT_CMD_SET_FIRST_INIT_FN(esp_at_modbus_tcp_cmd_regist, 26);

#endif // CONFIG_AT_MODBUSTCP_COMMAND_SUPPORT
