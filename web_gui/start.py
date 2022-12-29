import subprocess
import atexit
import socket

print("*** Starting MJPEG server ...***")
mjpeg_server = subprocess.Popen(
    ["python3", "./mjpeg.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

print("*** Starting API server ...  ***")
fastapi_server = subprocess.Popen(
    ["uvicorn", "app:app", "--host", "0.0.0.0"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

# Prepare a function on exit to shutdown the servers
def shutdown():
    mjpeg_server.kill()
    fastapi_server.kill()


# Get IP address
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print("*** Access the controls here ***")
print(f"--> http://{local_ip}:8000/")
print("    (If this doesn't work, run the `ifconfig`")
print("     command to see other IP addresses)")
print("*** Press CTRL+C to shutdown ***")

# Keep going until done
try:
    while True:
        pass
except KeyboardInterrupt:
    pass

atexit.register(shutdown)
