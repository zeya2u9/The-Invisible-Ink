from com.dtmilano.android.viewclient import ViewClient
import time
import os
import sys

device, serialno = ViewClient.connectToDeviceOrExit()

device.wake()

vc = ViewClient(device, serialno)

for view in vc.views:
    if view.getId() == "com.emanuelef.remote_capture:id/skip":
        view.touch()
        break
        
time.sleep(0.5)

time.sleep(1)
app_x = 126
app_y = 2172

device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(2)

app_x = 1010  # X-coordinate
app_y = 225  # Y-coordinate
device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(0.5)

start_x = 500
start_y = 1500  # Starting coordinates
end_x = 500
end_y = 500       # Ending coordinates

# Simulate a swipe up
device.drag((start_x, start_y), (end_x, end_y), 500)
time.sleep(2)

# app_x = 961
# app_y = 1940

# device.touch(app_x, app_y, device.DOWN_AND_UP)
# time.sleep(0.5)

vc = ViewClient(device, serialno)
vc.findViewWithText("Capture as root").touch()
time.sleep(0.5)

os.system('adb shell input keyevent KEYCODE_BACK')
time.sleep(0.5)

app_x = 530
app_y = 870

device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(3)

app_x = 750
app_y = 1510

device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(1)

app_x = 870
app_y = 230

device.touch(app_x, app_y, device.DOWN_AND_UP)
time.sleep(1)

sys.exit(0)
