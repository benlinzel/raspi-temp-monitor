#!/bin/bash

if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo"
    echo "sudo $0 $*"
    exit 1
fi

echo "Installing raspi-temp-monitor"

touch .env
echo "PUSHOVER_USER=" >> .env
echo "PUSHOVER_TOKEN=" >> .env
sudo chown pi:pi .env

echo "Copying service files to /lib/systemd/system..."
sudo install -v services/* /lib/systemd/system

echo "Enabling services..."
sudo systemctl enable tempmonitor.service
sudo systemctl enable tempmonitor_http.service
sudo systemctl daemon-reload
sudo systemctl start tempmonitor
sudo systemctl start tempmonitor_http

echo "Done!"
