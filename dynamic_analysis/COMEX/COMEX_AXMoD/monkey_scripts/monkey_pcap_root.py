from com.android.monkeyrunner import MonkeyDevice, MonkeyRunner
import sys
import time
import os

device = MonkeyRunner.waitForConnection()
device.wake()


time.sleep(1)
app_x = 126
app_y = 2172

device.touch(app_x, app_y, MonkeyDevice.DOWN_AND_UP)
time.sleep(2)

app_x = 1010  # X-coordinate
app_y = 225  # Y-coordinate
device.touch(app_x, app_y, MonkeyDevice.DOWN_AND_UP)
time.sleep(0.5)

start_x = 500
start_y = 1500  # Starting coordinates
end_x = 500
end_y = 500       # Ending coordinates

# Simulate a swipe up
device.drag((start_x, start_y), (end_x, end_y), 0, 500)
time.sleep(2)

app_x = 961
app_y = 1940

device.touch(app_x, app_y, MonkeyDevice.DOWN_AND_UP)
time.sleep(0.5)

os.system('adb shell input keyevent KEYCODE_BACK')
time.sleep(0.5)

app_x = 530
app_y = 870

device.touch(app_x, app_y, MonkeyDevice.DOWN_AND_UP)
time.sleep(3)

app_x = 750
app_y = 1510

device.touch(app_x, app_y, MonkeyDevice.DOWN_AND_UP)
time.sleep(1)

app_x = 870
app_y = 230

device.touch(app_x, app_y, MonkeyDevice.DOWN_AND_UP)
time.sleep(1)

sys.exit(0)