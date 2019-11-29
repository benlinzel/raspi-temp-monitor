# raspi-temp-monitor
Temperature Monitoring for Raspberry Pi

### Quick Start  

If you haven't already, install the DS18B20 sensor:  
`sudo nano /boot/config.txt`  
Append this at the end of the file: `dtoverlay=w1–gpio`  
`sudo reboot`  
~`sudo modprobe w1–gpio`~ (doesn't work)  
`sudo raspi-config`  
Go to Interface options, enable the 1-wire interface, then reboot  
`sudo modprobe w1-therm`  
`ls /sys/bus/w1/devices` (make sure there is a dir beginning with "28-")  

1. Install Dependencies:  
`sudo apt-get install python-pip` (if you don't already have it)  
`sudo pip install requests`  
`sudo -H pip install -U python-dotenv`  
2. Clone this repo in home directory (`/home/pi`)  
3. Run `sudo ./install.sh` to set up the services and start them  
4. Run `nano .env` and place your Pushover user and token ids  
5. Run `curl -X GET localhost:8000` to check if the http service is working, it should return the temperature value  

###### Watching logs
Run `sudo journalctl -fu tempmonitor` to check main service logs  
Run `sudo journalctl -fu tempmonitor_http` to check http service logs  
Run `sudo journalctl -fu tempmonitor*` to check both  


### Features:  
1. Sends push notifications when temperature is outside of normal range  
2. Regular-priority "warning" thresholds (warm/chilly) and high-priority "danger" thresholds (hot/freezing)   
3. Adjustable intervals (checks every 15 minutes by default)  
4. Adjustable temperature thresholds  

Default temperature thresholds (degrees C):
```
temp_freezing = 19.0
temp_chilly = 21.0
temp_warm = 27.0
temp_hot = 29.0
```


### Prerequisites:  
1. DS18B20 attached to raspberry pi  
2. Python (installed by default on raspberry pi)  
3. Python "requests" library `pip install requests` (run `sudo apt-get install python-pip` to install pip)  
4. [Pushover](https://pushover.net) installed on devices to be notified  
5. Git  

### Setup:  
1. In default home directory (`/home/pi`) run `git clone https://github.com/benlinzel/raspi-temp-monitor`  
2. Create an account at Pushover and place your user id and token in the `pushover_user` and `pushover_token` vars [here](https://github.com/benlinzel/raspi-temp-monitor/blob/master/temp_sensor.py#L19) and [here](https://github.com/benlinzel/raspi-temp-monitor/blob/master/temp_sensor.py#L20)
3. Change the running interval in the `time.sleep` command (900 seconds by default)

### Optional:  
Create a service to get it to run automatically on boot.  
1. `cd /lib/systemd/system`  
2. `sudo nano tempmonitor.service`  
3. Paste this and save:  
```
[Unit]
Description=Raspberry Pi Temp Monitor
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/pi/raspi-temp-monitor/temp_sensor.py

[Install]
WantedBy=multi-user.target
```
4. `sudo systemctl enable tempmonitor.service`

Do the same for the http python script  
2. `sudo nano tempmonitor_http.service`  
3. Paste this and save:  
```
[Unit]
Description=Raspberry Pi Temp Monitor
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/pi/raspi-temp-monitor/http_server.py

[Install]
WantedBy=multi-user.target
```
4. `sudo systemctl enable tempmonitor_http.service`  
5. `sudo systemctl daemon-reload`
