#!/usr/bin/env python
# Read the display calibration values from a Looking Glass's EEPROM.
# This is basically a Python port of the EEPROM reading code 
# in https://crates.io/crates/pluton
#
# Uses python-hidapi (https://pypi.org/project/hidapi/)
#
# Paul Melis <paul.melis@surfsara.nl>
# SURFsara Visualization group
from struct import unpack
import json
import hid

USB_VID = 0x04d8
USB_PID = 0xef7e

def hid_multiread(dev):
    
    data = dev.read(128, timeout_ms=10)
    res = data
    
    while len(data) > 0:
        data = dev.read(128, timeout_ms=10)
        res.extend(data)
        
    return res

def hid_query(dev, addr):

    # 68 byte request, might actually need 64, but not clear
    # when hid versus hidraw is used.
    buffer = bytearray([0]*68)
    
    buffer[0] = 0               # Report ID
    buffer[1] = 0
    buffer[2] = addr >> 8       # Page to read
    buffer[3] = addr & 0xff
    
    res = dev.send_feature_report(buffer)        
    assert res >= 0

    res = hid_multiread(dev)
    assert res[:4] == list(buffer[:4])
    
    return res[4:]

devs = list(hid.enumerate(USB_VID, USB_PID))
#print(devs)
assert len(devs) == 1
devinfo = devs[0]

dev = hid.device()
dev.open_path(devinfo['path'])
#dev.set_nonblocking(1)

# Data is read in pages of 64 bytes. First page (0) starts with a
# 4 byte header denoting the length of the calibration data (in JSON
# format)
page = hid_query(dev, 0)

json_size = unpack('>I', bytes(page[:4]))[0]
#print('JSON size: %d' % json_size)

json_data = page[4:]
addr = 1
while len(json_data) < json_size:    
    page = hid_query(dev, addr)
    json_data.extend(page)
    addr += 1
    
json_data = json_data[:json_size]
json_data = bytes(json_data)
json_data = json_data.decode('utf8')

# Pretty print
parsed = json.loads(json_data)
print(json.dumps(parsed, indent=4))

