import tkinter as tk
import subprocess, threading, base64, os

def write(port, advKey):
    popupWindow = tk.Toplevel()
    popupWindow.title("Deploying...")

    baudRate = 921600

    text_output = tk.Text(popupWindow)
    text_output.pack()
    text_output.delete(0.0, tk.END)

    # Make the popup modal (prevents interaction with main window)
    popupWindow.grab_set()

    def run_command(command, returnFunc):
        """Run command in a thread and pipe output to a Tkinter text box."""

        def task():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    text=True,  # so we get strings, not bytes
                    bufsize=1  # line-buffered
                )

                for line in process.stdout:
                    # Safe update of text widget using .after()
                    text_output.after(0, output, line)

                process.stdout.close()
                process.wait()
            except Exception as e:
                text_output.after(0, output, "--- Command failed with error ---\n" + str(e))
            else:
                if process.returncode != 0:
                    text_output.after(0, output, "--- Command failed ---")
                else:
                    text_output.after(0, output, "--- Command finished ---")
                    returnFunc()

        threading.Thread(target=task, daemon=True).start()

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
                run_command(f"esptool --after no_reset --port {port} erase_region 0x9000 0x5000", writeBinaries)
            except Exception as e:
                output("Failed to erase ESP32: " + str(e))