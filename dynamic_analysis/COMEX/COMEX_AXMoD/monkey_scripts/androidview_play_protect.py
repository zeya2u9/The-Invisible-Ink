from com.dtmilano.android.viewclient import ViewClient
import time
import os
import sys

device, serialno = ViewClient.connectToDeviceOrExit()

device.wake()


device.shell("am start -a android.intent.action.MAIN -n com.android.vending/.AssetBrowserActivity")

#APP START
x = 530  # X-coordinate
y = 1850  # Y-coordinate
device.touch(x, y, device.DOWN_AND_UP)
time.sleep(2)

#3dot
x = 1025  # X-coordinate
y = 205  # Y-coordinate
device.touch(x, y, device.DOWN_AND_UP)
time.sleep(2)

#play protect
x = 830  # X-coordinate
y = 435  # Y-coordinate
device.touch(x, y, device.DOWN_AND_UP)
time.sleep(2)

#settings
x = 1025  # X-coordinate
y = 160  # Y-coordinate
device.touch(x, y, device.DOWN_AND_UP)
time.sleep(2)

#toggle
x = 910  # X-coordinate
y = 515  # Y-coordinate
device.touch(x, y, device.DOWN_AND_UP)
time.sleep(2)

#approve
x = 910  # X-coordinate
y = 1345  # Y-coordinate
device.touch(x, y, device.DOWN_AND_UP)
time.sleep(0.5)

sys.exit(0)
