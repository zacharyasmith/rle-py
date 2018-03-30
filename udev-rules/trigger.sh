#!/usr/bin/env bash
cp -f 99-usb-serial.rules /dev/udev/rules.d/
udevadm trigger
