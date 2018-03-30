mkdir -p /dev/udev/rules.d/
cp -f 99-usb-serial.rules /dev/udev/rules.d/
udevadm trigger
