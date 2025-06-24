import tkinter as tk
import subprocess, threading, base64, os
from threadedCommand import run_command

def write(port, advKey):
    popupWindow = tk.Toplevel()
    popupWindow.title("Deploying...")

    baudRate = 921600

    text_output = tk.Text(popupWindow)
    text_output.pack()
    text_output.delete(0.0, tk.END)

    # Make the popup modal (prevents interaction with main window)
    popupWindow.grab_set()

    def output(string):
        text_output.insert(tk.END, str(string).strip() + "\n")
        print(string)
        text_output.see(tk.END)

    # DO NOT RUN INDEPENDENTLY
    def writeBinaries():
        output("--- Writing binary files to ESP32 ---")
        output("DO NOT UNPLUG OR CLOSE")
        try:
            run_command(f"esptool --before no_reset --baud {baudRate} --port \"{port}\"\
            write_flash 0x1000  \"{bootloader}\" \
                        0x8000  \"{partitionTable}\" \
                        0xe000  \"{keyPath}\" \
                        0x10000 \"{openhaystackBinary}\"",
                        text_output,
                        output,
                        lambda: output("-----\nyay! All done!"))
        except Exception as e:
            output("Failed to write to ESP32: " + str(e))

    #Main process
    try:
        decodedBytes = base64.b64decode(advKey)
        keyFile = open(os.path.join("FindMyIntegration", "ESP32", "build", "keyfile.key"), "wb")
        keyFile.write(decodedBytes)
        keyFile.close()
        output("Decoded Advertisement Key...")
    except Exception as e:
        output("Failed to decode key: " + str(e))
    else:
        try:
            path = os.path.abspath(os.path.join("FindMyIntegration", "ESP32", "build"))
            output("Located path")
            output(path)
            bootloader = os.path.join(path, "bootloader.bin")
            output("Located bootloader binary")
            partitionTable = os.path.join(path, "partition-table.bin")
            output("Located partitionTable binary")
            openhaystackBinary = os.path.join(path, "openhaystack.bin")
            output("Located openhaystack binary")
            keyPath = os.path.join(path, "keyfile.key")
            output("Located key file")
        except Exception as e:
            output("Failed to find ESP32 binaries: " + str(e))
        else:
            try:
                output("--- Erasing ESP32 ---")
                output("DO NOT UNPLUG OR CLOSE")
                run_command(f"esptool --after no_reset --port {port} erase_region 0x9000 0x5000", text_output, output, writeBinaries)
            except Exception as e:
                output("Failed to erase ESP32: " + str(e))