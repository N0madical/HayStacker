// -------------------
// HayStacker Espressif ESP32-C3 & S2 Firmware
// Designed by N0madical, based off of OpenHaystack
// Using NimBLE as the bluetooth framework for lower power usage
// And ESP32 Deep Sleep
// -------------------

// Things to know about Esp32 programming:

// - Espressif provides several variable types that are not standard, for example:
// - struct ble_gap_adv_params adv_params;
// - 'ble_gap_adv_params' is the type of the variable 'adv_params' here


// ---------------------------------------
// Start code:

/** Standard C libraries for types, memory, booleans, and I/O. */
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>

/** ESP-IDF specific headers for: */
//     Logging
//     Bluetooth and BLE operations
//     Power management (hibernation)
//     Event handling and timers
#include "esp_log.h"
#include "esp_sleep.h"
#include "esp_nimble_hci.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/ble_gap.h"
#include "host/util/util.h"

#include "esp_bt.h"    // for esp_bt_controller_mem_release()


/** For real-time OS features (FreeRTOS tasks) and NVS (non-volatile storage, like reading the key from flash). */
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"

#include "esp_partition.h"





/** Device name for debugging */
static const char * deviceName = "HaystackerTag";

/** Random device address */
static uint8_t randomAddress[6] = { 0xFF, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF };






/** Pre-defining functions to allocate memory */
void host_task(void *param);
static void ble_app_on_sync(void);
static int ble_app_gap_event(struct ble_gap_event *event, void *arg);
void setBLEAddress(uint8_t *addr, const uint8_t *public_key);
void setBLEPayload(uint8_t *payload, const uint8_t *public_key);






/** Advertisement payload */
static uint8_t tagPayload[31] = {
	0x1e, /* Length (30) */
	0xff, /* Manufacturer Specific Data (type 0xff) */
	0x4c, 0x00, /* Company ID (Apple) */
	0x12, 0x19, /* Offline Finding type and length */
	0x00, /* State */
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, /* First two bits */
	0x00, /* Hint (0x00) */ 
};








/** Check if advertising key partition and file are present */
/** Returns advertising status */
int loadKey(uint8_t *dst, size_t size) {
    const esp_partition_t *keypart = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, 0x40, "key");
    if (keypart == NULL) {
        ESP_LOGE(deviceName, "Could not find key partition");
        return 1;
    }
    esp_err_t status;
    status = esp_partition_read(keypart, 0, dst, size);
    if (status != ESP_OK) {
        ESP_LOGE(deviceName, "Could not read key from partition: %s", esp_err_to_name(status));
    }
    return status;
}






/** Setting BLE Advertisement address. First 6 bytes of the adv key are this address */
/** Address stored in addr[5] */
void setBLEAddress(uint8_t *addr, const uint8_t *public_key) {
	addr[0] = public_key[5];
	addr[1] = public_key[4];
	addr[2] = public_key[3];
	addr[3] = public_key[2];
	addr[4] = public_key[1]; 
	addr[5] = public_key[0] | 0b11000000; //Set the first two bits to high (1) to signify random static address
}






/** Genereate a decryptable advertising payload
    * Can be decrypted by the private key stored in the key's .keys file
    * Advertising payload stored in payload[29] variable 
    * */
void setBLEPayload(uint8_t *payload, const uint8_t *public_key) {
    /* copy last 22 bytes */
	memcpy(&payload[7], &public_key[6], 22);
	/* append two bits of public key */
	payload[29] = public_key[0] >> 6;
}





/** Starts the NimBLE bluetooth host task in a seperate thread */
void host_task(void *param)
{
    // This will return only when nimble_port_stop() is called
    nimble_port_run();
    nimble_port_freertos_deinit();
}





/** Get data from keyfile and start bluetooth advertising
 * Should occur once bluetooth chip and processor have synced
 */
static void ble_app_on_sync(void)
{
    int rc;

    // 1) Load the public key
    static uint8_t public_key[28];
    if (loadKey(public_key, sizeof public_key) != ESP_OK) {
        ESP_LOGE(deviceName, "Key load failed—halting");
        return;
    }


    // 2) Derive address & payload bytes
    setBLEAddress(randomAddress, public_key);
    setBLEPayload(tagPayload, public_key);
    

    // Set the random static address
    ESP_LOGI(deviceName, "Setting random address");
    rc = ble_hs_id_set_rnd(randomAddress);
    if (rc != 0) {
        ESP_LOGE(deviceName, "ble_hs_id_set_rnd failed: %d", rc);
        return;
    }

    uint8_t own_addr_type;
    rc = ble_hs_id_infer_auto(0, &own_addr_type);
    if (rc != 0) {
        ESP_LOGE(deviceName, "ble_hs_id_infer_auto failed: %d", rc);
        return;
    }

    // Initialize raw data advertising
    uint8_t adv_data_len = tagPayload[0];
    rc = ble_gap_adv_set_data(&tagPayload[1], adv_data_len);
    if (rc) {
        ESP_LOGE(deviceName, "ble_gap_adv_set_data failed: %d", rc);
        return;
    }

    // Flags:
    struct ble_gap_adv_params advp = { 0 };
    advp.conn_mode     = BLE_GAP_CONN_MODE_NON; // Classic Bluetooth is not supported
    advp.disc_mode     = BLE_GAP_DISC_MODE_NON; // general discoverable
    advp.itvl_min      = 0x0021; //min advertise time 20ms (0x0021 → 33 * 0.625 ms ≈ 20.6 ms)
    advp.itvl_max      = 0x0021; //max advertise time 20ms (0x0021 → 33 * 0.625 ms ≈ 20.6 ms)
    advp.channel_map   = 0x07; // Set advertising channel, 0x07 means “all three advertising channels (37, 38, 39).”
    advp.filter_policy = 0; // Allow any to pick up packet (no whitelist)

    // Advertising settings:
    rc = ble_gap_adv_start(
        own_addr_type,       // use the static random address from above
        NULL,                // no peer whitelist
        BLE_HS_FOREVER,      // advertise until we tell it to stop
        &advp,               // our config defined above
        ble_app_gap_event,   // a callback for GAP events (adv complete, etc.)
        NULL                 // end arguments
    );

    // Error catching
    if (rc) {
        ESP_LOGE(deviceName, "ble_gap_adv_start failed: %d", rc);
        return;
    }

    ESP_LOGI(deviceName, "Advertising started");
}







/** Handle Generic Access Profile (GAP) events */
static int ble_app_gap_event(struct ble_gap_event *event, void *arg)
{
    switch (event->type) {

        // Event: Advertisement stopped
        case BLE_GAP_EVENT_ADV_COMPLETE:
            ESP_LOGI(deviceName, "Advertising complete; now stopping");
            // ble_gap_adv_stop() called by the stack automatically
            break;

        default:
            break;
    }
    return 0;
}








/* Code to run on ESP32 start */
void app_main(void)
{   
    ESP_LOGI(deviceName, "Boot starting!");

    // Initiate flash memory, then free memory used by classic Bluetooth as it's not needed for NimBLE
    nvs_flash_init();
    ESP_ERROR_CHECK(esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT));

    ESP_LOGI(deviceName, "Memory freed");

    // Bring up the controller + HCI for NimBLE
    ESP_ERROR_CHECK(nimble_port_init());

    // Configure host callbacks - specefic events that the BLE controller can return to the host
    ble_hs_cfg.reset_cb = NULL;                              // Unexpected controller reset
    ble_hs_cfg.sync_cb  = ble_app_on_sync;                   // When the host and controller are synced
    ble_hs_cfg.store_status_cb = ble_store_util_status_rr;   // Status of persistent storage


    // Start up the host task
    nimble_port_freertos_init(host_task);

    ESP_LOGI(deviceName, "Bluetooth host task started");

    // Let tag advertise a couple times
    // Because the bluetooth controller handles advertising,
    // Pausing the main thread will not pause advertising
    // vTaskDelay(pdMS_TO_TICKS(2000)); // 2 seconds of advertising, same as Apple

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(500));  // yields to the Idle task
    }

 
    // // Enter hibernate mode for 5 minutes
    // ESP_LOGI(deviceName, "Entering hibernation");


    // //Stop BLE ports
    // ESP_ERROR_CHECK(nimble_port_stop());
    // ESP_ERROR_CHECK(nimble_port_deinit());


    // // Set time to wake up
    // const int wakeup_seconds = 1 * 60;
    // esp_sleep_enable_timer_wakeup((uint64_t)wakeup_seconds * 1000000ULL);


    // // Rest, my sweet child
    // esp_deep_sleep_start();
    
}
