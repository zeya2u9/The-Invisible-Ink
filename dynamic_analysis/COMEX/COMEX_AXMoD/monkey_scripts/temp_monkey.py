from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import sys
import time
import os
import re

# Connect to the device
device = MonkeyRunner.waitForConnection()
device.wake()

print(dir(device))
print(device.getViewIdList())
print(device.getViewsByText("Settings"))