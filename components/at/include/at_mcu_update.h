/*
 * SPDX-FileCopyrightText: 2025 Taytech AS
 *
 * SPDX-License-Identifier: MIT
 */

#ifndef AT_MCU_UPDATE_H
#define AT_MCU_UPDATE_H

#include "esp_err.h"

/**
 * @brief Initialize MCU update GPIOs (Reset and Boot)
 */
void at_mcu_update_init(void);

/**
 * @brief Write data to the MCU firmware partition.
 * 
 * @param buffer specific buffer data
 * @param len specific length
 * @param offset offset in partition
 * @return esp_err_t 
 */
esp_err_t at_mcu_fw_write(const void *buffer, uint32_t len, uint32_t offset);

/**
 * @brief Start the MCU Update process (Phase 2).
 * 
 * This function handles the entire update flow:
 * 1. Suspend AT Parser
 * 2. Enter Bootloader
 * 3. Erase and Write STM32 Flash
 * 4. Verify (Optional)
 * 5. Resume AT Parser
 * 
 * @return esp_err_t 
 */
void at_mcu_update_start(void *pvParameters);

#endif // AT_MCU_UPDATE_H
