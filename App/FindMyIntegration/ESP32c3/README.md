# HayStacker Firmware for ESP32

This project contains a PoC firmware for Espressif & Seeed ESP32-C3 & ESP32-C3S2 chips.
After flashing our firmware, the device sends out Bluetooth Low Energy advertisements such that it can be found by [Apple's Find My network](https://developer.apple.com/find-my/).


## Disclaimer

Note that the firmware is just a proof-of-concept and currently only implements advertising a single static key. This means that **devices running this firmware are trackable** by other devices in proximity.


## Changes

From the base created by OpenHaystack, I have rewritten this code for the ESP32-C3 and implimented ESP Deep Sleep modes for power savings 
New idle power = 10uA
New advertising power = 7mA


## Requirements

To change and rebuild the firmware, you need Espressif's IoT Development Framework (ESP-IDF).
Installation instructions for the latest version of the ESP-IDF can be found in [its documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/).
The firmware is tested on version 5.4.

Haystacker v2 or above, with configurable flash settings ability


## Build

With the ESP-IDF on your `$PATH`, you can use `idf.py` to build the application from within this directory:

```bash
idf.py build
```

This will create the following files:

- `build/bootloader/bootloader.bin` -- The second stage bootloader
- `build/partition_table/partition-table.bin` -- The partition table
- `build/openhaystack.bin` -- The application itself

These files are required for the next step: Deploy the firmware.


## Deploy the Firmware

Place the parent directory of this file, containing the `build` folder, into haystacker/app/findmyintegration

> **Note:** You may need to manualy put the device into bootloader mode after it first connects.
> **Note:** You might need to press the boot button on your device after installing this firmware before it starts sending advertisements.
