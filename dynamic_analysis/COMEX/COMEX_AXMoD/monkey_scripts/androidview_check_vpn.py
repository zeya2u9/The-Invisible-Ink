from com.dtmilano.android.viewclient import ViewClient
import time
import os
import sys

device, serialno = ViewClient.connectToDeviceOrExit()

vc = ViewClient(device, serialno)

ele = vc.findViewById("com.android.vpndialogs:id/warning")

if ele:
    try:
        ele.parent.parent.children[2].children[1].touch()
    except Exception as e:
        print(e)