#! /bin/bash

#To make this a service:
#Make this executable
#Make sure the path with cd is correct directory for the app
#Add the following line to /etc/rc.local (change path as necessary):
#/home/pi/flaskwf/startme.sh


cd /home/pi/flaskwf
sudo nohup python flaskwf.py > log.txt 2>&1 &
