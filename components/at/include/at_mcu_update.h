/*
 * SPDX-FileCopyrightText: 2025 Taytech AS
 *
 * SPDX-License-Identifier: MIT
 */

#pragma once

#include <stdint.h>
#include "esp_err.h"

// AN3155 Command Codes
#define AN3155_CMD_GET              0x00
#define AN3155_CMD_GET_VER          0x01
#define AN3155_CMD_GET_ID           0x02
#define AN3155_CMD_READ_MEM         0x11
#define AN3155_CMD_GO               0x21
#define AN3155_CMD_WRITE_MEM        0x31
#define AN3155_CMD_ERASE            0x43 // Extended Erase (for modern chips) or 0x44 (old Erase)
#define AN3155_CMD_EXT_ERASE        0x44 // Check datasheet, often 0x44 is standard erase, 0x43 extended
#define AN3155_CMD_WRITE_PROTECT    0x63
#define AN3155_CMD_WRITE_UNPROTECT  0x73
#define AN3155_CMD_READOUT_PROTECT  0x82
#define AN3155_CMD_READOUT_UNPROTECT 0x92

#define AN3155_ACK                  0x79
#define AN3155_NACK                 0x1F

void at_mcu_update_init(void);

// AT Command Wrapper
uint8_t at_mcu_update_cmd(uint8_t para_num);

// Web Server trigger
void at_mcu_update_start_task(void);

// Debug Tool
esp_err_t at_mcu_check_bootloader(void);

// Get Update Status (0=Idle, 1=Running, 2=Done, -1=Error)
void at_mcu_update_get_status(int *status, uint32_t *written, uint32_t *total);
