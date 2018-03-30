#!/usr/bin/env bash
cp -f 99-usb-serial.rules /etc/udev/rules.d/
udevadm trigger
