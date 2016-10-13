#! /usr/bin/python

import subprocess as sp
import re

def get_aps(iface="wlan0"):
  '''return a list of dictionnaries with access point info from iwlist'''
  proc = sp.Popen(["iwlist", iface, "scan"], stdout = sp.PIPE, stderr = sp.PIPE)

  #get info on the access points
  aps = []
  info = {}
  for line in iter(proc.stdout.readline,''):

    rline = line.rstrip()

    if rline.find("Address") > -1:
      if 'mac' in info:
        #This is not the first channel, dump info and append to aps:
        aps.append(info)
        info = {}
      info['mac']=rline.split("Address: ")[1] 

    if rline.find("ESSID") > -1:
      id = rline.split(':')[1][1:-1]
      info['ssid'] = id
 
  #add the last one to the list
  if 'mac' in info:
    aps.append(info)

  return aps

def get_connection_info(iface = 'wlan0'):
  '''return ip and MAC addresses of interface from ifconfig '''
  proc = sp.Popen(["ifconfig", iface ], stdout = sp.PIPE)

  info = {}
  info['iface']=iface
  for line in iter(proc.stdout.readline,''):

    rline = line.rstrip()
    if rline.find("HWaddr") > -1:
      mac = rline.split("HWaddr ")[1] 
      info['mac'] = mac

    if rline.find("inet addr") > -1:
      ip = rline.split(':')[1].split(' ')[0]
      info['ip'] = ip
   

  return info





