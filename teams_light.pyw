# RUN THIS FILE AND ENSURE teams_status.py IS LOCATED IN THE SAME FOLDER!
#
# Project: Teams Light
# Written By: Lorentz Factr
# Date: 2/1/22
#
# Instructions & Prerequisites:
# 1. Setup an MQTT broker service with a TOPIC called "TEAMS_STATUS"
# 2. Setup an MQTT controlled light source that subscribes to your MQTT broker with topic "TEAMS_STATUS" on port 1883.
# 3. The default settings of this program assumes your light source accepts instructions as a formated string "R,G,B" (line 24).
# 4. If your light source is not setup to accept the format I designed, you will need update to the key values
#       in the custom_return dictionary with what your subcriber expects (line 28).
# 5. Update the mqtt_broker variable with YOUR MQTT broker IP address (DONT USE 'localhost') or public domain (line 35)
# 6. Update the filepath to the logs.txt location in your computer (line 38).
# 7. Not required: update the hard interval update to the desired amount of time in seconds (line 49)
# 8. If you want to run this on startup... Make a shortcut to teams_light.py, move the short cut here: %appdata%\Microsoft\Windows\Start Menu\Programs\Startup

import serial
from time import sleep,time       # You must install this dependency! https://pypi.org/project/paho-mqtt/#installation
from teams_status import teamsStatus

# Set to false if you want to set custom instructions for your lighting subscriber.
# IMPORTANT: if you set to False, you must update the custom return instructions (line 28)!
default_instruction = True

# UPDATE THIS LIST IF YOU SET ABOVE TO FALSE
# Update the key values to whatever your device expects for each. It may be an integer, string, RGB tuple, it's up to you. 
custom_return = {"Green": "YOUR VALUE FOR GREEN",
                "Yellow": "YOUR VALUE FOR YELLOW", 
                "Red": "YOUR VALUE FOR RED",
                "Off": "YOUR VALUE FOR OFF"
                }

com_port = "COM9"

# UPDATE with your filepath to the folder that contains logs.txt! 
filepath = "C:\\Users\\z003213d\\AppData\\Roaming\\Microsoft\\Teams"

# Temp var to store that last status reported.
last_status = None

# Variable for the hard check timer. You can update the interval (seconds) to check status every 'interval' seconds.
# If you don't want a hard interval check, set to very large value.
start = 0
interval = 10 #UPDATE if desired

ser = serial.Serial()
ser.baudrate = 9600
ser.port = com_port

# Instatiate the teams status class, leave kwargs empty for default settings. The logic instatiates the class based on
# the default_instruction variable above.
if default_instruction == True:
    teams = teamsStatus(filepath=filepath)

elif default_instruction == False:
    teams = teamsStatus(green_hue=custom_return["Green"],
                        yellow_hue=custom_return["Yellow"],
                        red_hue=custom_return["Red"],
                        off_hue=custom_return["Off"],
                        filepath=filepath
                        )

# A forever while loop since this is designed to run on start up and not shut down.
while True:
    # Get the current Teams status.
    status = teams.get_status()
    # Get the RGB color from the current Teams status.
    color, color_name = teams.status_color(status)

    # Check if the status changed
    if status != last_status or interval <= time()-start:
        print(f'Current Teams Status: {status} | Status Color: {color_name}')
        if not ser.is_open:
            try:
                ser.open()
            except:
                print(f'Could not open serial port {com_port}')
        if ser.is_open:
            command = f'{color[0]},{color[1]},{color[2]} 1000\n'
            try:
                ser.write(command.encode())
                ser.flush()
            except:
                print(f'Could not write serial port {com_port}')
                ser.close()

        start = time()
    
    # Sleep for one second to reduce the amount of log file reads (in seconds).
    sleep(1)
    # Store the last known status change in the temp variable.
    last_status = status
