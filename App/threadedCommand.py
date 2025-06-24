import subprocess, threading

def run_command(command, parent, outputFunc, returnFunc):
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
                parent.after(0, outputFunc, line)

            process.stdout.close()
            process.wait()
        except Exception as e:
            parent.after(0, outputFunc, "--- Command failed with error ---\n" + str(e))
        else:
            if process.returncode != 0:
                parent.after(0, outputFunc, "--- Command failed ---")
            else:
                parent.after(0, outputFunc, "--- Command finished ---")
                returnFunc()

    threading.Thread(target=task, daemon=True).start()