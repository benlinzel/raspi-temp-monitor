import os
import glob
import time
import requests
import json
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

PUSHOVER_USER = os.environ.get("PUSHOVER_USER")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")
SNOOZE_HOST = os.environ.get("SNOOZE_HOST")

with open('/home/pi/raspi-temp-monitor/config.json') as json_data_file:
  config = json.load(json_data_file)
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

room_name = config["tempMonitor"]["roomName"]
check_interval_seconds = config["tempMonitor"]["intervalSeconds"]
temp_c_freezing = config["tempMonitor"]["tempFreezingCelsuis"]
temp_c_chilly = config["tempMonitor"]["tempChillyCelsuis"]
temp_c_warm = config["tempMonitor"]["tempWarmCelsuis"]
temp_c_hot = config["tempMonitor"]["tempHotCelsuis"]

pushover_url = 'https://api.pushover.net/1/messages.json'

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

# Return true if host says snoozed, false otherwise
def check_snooze():
	try:
		print(SNOOZE_HOST)
		r = requests.get(SNOOZE_HOST)
		if(r.status_code == 200):
			print(r.status_code)
			if(r.lower() == "true"):
				print(r)
				print("snooze active")
				return True
	except: 
		print("could not check snooze service")
	return False
 
def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0

	# TEST OVERRIDE
	# temp_c = 30.0

	if (temp_c <= temp_c_freezing):
		title = "Very Low Temp Alert"
		msg = room_name + ' is WAY too cold! (' + str(temp_c) + " C)"
		priority = 1
		# params = {'token':PUSHOVER_TOKEN, 'user':PUSHOVER_USER, 'title':'High Temperature Alert', 'message':msg}
		# r = requests.post(url = pushover_url, data = params)
		print("sending very low temp alert")
		if(not check_snooze()):
			# r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority}, files={"attachment":open("/home/pi/raspi-temp-monitor/gifs/freezing.gif","rb")})
			r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority})
		print(r)

	elif (temp_c <= temp_c_chilly):
		title = "Low Temp Warning"
		msg = room_name + ' is chilly. (' + str(temp_c) + " C)"
		priority = 0
		print("sending low temp alert")
		if(not check_snooze()):
			# r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority}, files={"attachment":open("/home/pi/raspi-temp-monitor/gifs/chilly.gif","rb")})
			r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority})
		print(r)

	elif (temp_c >= temp_c_hot):
		title = "Very High Temp Alert"
		msg = room_name + ' is WAY too hot! (' + str(temp_c) + " C)"
		priority = 1
		print("sending very high temp alert")
		if(not check_snooze()):
			# r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority}, files={"attachment":open("/home/pi/raspi-temp-monitor/gifs/hot.gif","rb")}) 
			r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority})
		print(r)

	elif (temp_c >= temp_c_warm):
		title = "High Temp Warning"
		msg = room_name + ' is warm: (' + str(temp_c) + " C)"
		priority = 0
		print("sending high temp alert")
		if(not check_snooze()):
			# r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority}, files={"attachment":open("/home/pi/raspi-temp-monitor/gifs/warm2.gif","rb")}) 
			r = requests.post(pushover_url, data={"token":PUSHOVER_TOKEN,"user":PUSHOVER_USER,"title":title,"message":msg,"priority":priority})
		print(r)

	else:
		print("temp within safe zone")

	return temp_c, temp_f
	
while True:
	print(read_temp())	
	time.sleep(config["tempMonitor"]["intervalSeconds"]) # every 15 minutes
