#!/usr/bin/env bash
mkdir -p /dev/udev/rules.d/
cp -f rs232.rules /dev/udev/rules.d/
cp -f rs485.rules /dev/udev/rules.d/
udevadm trigger
