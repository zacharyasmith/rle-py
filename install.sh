#!/bin/bash
rm -rf /opt/SeaLion
mkdir /opt/SeaLion
cp -R main.py RunMainWindow.py __init__.py components view /opt/SeaLion
cp SeaLion.desktop /usr/share/applications
