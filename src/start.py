import subprocess
import platform
import signal
import os
import time

def start_server():
    global server_process
    server_process = subprocess.Popen(['python', 'server.py'])
    print('Server has started')

def restart_server():
    global server_process
    if server_process:
        if platform.system() == 'Windows':
            subprocess.Popen(['taskkill', '/F', '/T', '/PID', str(server_process.pid)], shell=True)
        else:
            os.kill(server_process.pid, signal.SIGTERM)
            server_process.wait()
    start_server()

if __name__ == "__main__":
    server_process = None
    start_server()

    try:
        while True:
            print("Server restarting in 10 seconds...")
            time.sleep(10)
            restart_server()
    except KeyboardInterrupt:
        restart_server()
