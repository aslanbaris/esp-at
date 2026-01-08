/*
 * SPDX-FileCopyrightText: 2024 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_err.h"

#include "driver/gpio.h"
#include "esp_at.h"
#include "esp_at_init.h"

void app_main(void)
{
    // Configure IO12 (BOOT) as Output Low
    // Configure IO13 (NRST) as Output High (Open Drain + Pull-up)
    
    // Set levels BEFORE config to avoid glitches
    gpio_set_level(12, 0);
    gpio_set_level(13, 1);

    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT_OD; // Open Drain for safety on Reset line
    io_conf.pin_bit_mask = (1ULL << 12) | (1ULL << 13);
    io_conf.pull_down_en = 0;
    io_conf.pull_up_en = 1; // Enable internal pull-up
    gpio_config(&io_conf);

    esp_at_main_preprocess();

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_at_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    esp_at_init();
}
