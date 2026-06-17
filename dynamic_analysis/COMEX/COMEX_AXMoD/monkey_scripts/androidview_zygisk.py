from com.dtmilano.android.viewclient import ViewClient
import time
import os
import sys

device, serialno = ViewClient.connectToDeviceOrExit()

device.wake()

app_x = 150  # X-coordinate
app_y = 2300  # Y-coordinate
device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(0.5)

# settings
app_x = 1025  # X-coordinate
app_y = 170  # Y-coordinate
device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(0.5)

start_x = 500
start_y = 1000  # Starting coordinates
end_x = 500
end_y = 500       # Ending coordinates

# Simulate a swipe up
device.drag((start_x, start_y), (end_x, end_y), 100)
time.sleep(1)

vc = ViewClient(device, serialno)

vc.findViewWithText("Zygisk").touch()
time.sleep(0.5)

vc.findViewWithText("Enforce DenyList").touch()
time.sleep(0.5)

sys.exit(0)