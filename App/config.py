import write_ESP32
import write_ESP32_C3

# Format: "Device Type" : [deployScript : {"Firmware Name" : "FirmwareFolder"}]
# Note: deployScript must have a function headed: write(firmware, port, advKey)
# FirmwareFolder must exist in App/FindMyIntegration

firmwareOptions = {
    "ESP32 Generic" : [write_ESP32, {
        "Constant Ping" : "ESP32",
        "Hibernate 1 minute" : "ESP32-h1min",
        "Sleep 20 seconds" : "ESP32-LowPower",
    }],
    "ESP32 C3 & S2" : [write_ESP32_C3, {
        "Constant Ping" : "ESP32c3",
        "Hibernate 5 minutes" : "ESP32c3-h5min",
    }]
}