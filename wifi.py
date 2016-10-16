#! /usr/bin/python

import subprocess as sp
import re
import os

def connect_wifi(ssid, pwd, iface='wlan0'):
  write_wpa_conf(ssid, pwd)
  sp.call('sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak', shell=True)
  sp.call('sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf',shell=True)
  sp.call('sudo ifdown '+iface, shell=True)
  sp.call('sudo ifup '+iface, shell=True)



def write_wpa_conf(ssid, pwd):
  '''Write the wpa_supplicant file'''
  wfile = open ("wpa_supplicant.conf", "w")
  info = "network={\n ssid=\"" + ssid + "\"\n psk=\"" + pwd + "\"\n}"
  wfile.write(info)
  wfile.close()

def write_hostapd_conf(iface, ssid, pwd, ip):
  '''Create the hostapd.conf file'''

  info = "\
interface={} \n\
ssid={} \n\
wpa_passphrase={}\n\
hw_mode=g\n\
channel=10\n\
auth_algs=1\n\
wpa=2\n\
wpa_key_mgmt=WPA-PSK\n\
wpa_pairwise=CCMP\n\
rsn_pairwise=CCMP\n\
".format(iface,ssid, pwd)
  
  hfile = open("hostapd.conf", "w")
  hfile.write(info)
  hfile.close()

def write_network_interfaces_AP(ip = '10.10.0.0', iface='wlan0' ):
  '''Write the /etc/network/interfaces file for AP mode'''
  network = '10.10.0.0'
  info = "\
allow-hotplug {}\n\
iface {} inet static\n\
	address {}\n\
	netmask 255.255.255.0\n\
	network {}\n\
	broadcast 10.0.0.255\n\
       	wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf\n\
".format(iface,iface, ip, network)

  hfile = open("interfaces", "w")
  hfile.write(info)
  hfile.close()



def get_aps2(iface="wlan0"):
  '''return a list of dictionnaries with access point info from iw'''
  proc = sp.Popen(["sudo","iw","dev",iface,"scan","ap-force"], stdout = sp.PIPE, stderr = sp.PIPE)

  #get info on the access points
  aps = []
  info = {}
  for line in iter(proc.stdout.readline,''):

    rline = line.rstrip()
    #Each new entry starts with BSS as the first 3 characters
    if rline.find("BSS ") > -1 and rline.find(iface) > -1 :
      if 'mac' in info:
        #This is not the first channel, dump info and append to aps:
        aps.append(info)
        info = {}
      info['mac']=rline.split("BSS ")[1].split('(')[0]

    if rline.find("SSID") > -1:
      id = rline.split('SSID: ')[1]
      info['ssid'] = id

    if rline.find("signal: ") > -1:
      signal = rline.split('signal: ')[1]
      info['signal'] = signal


  #add the last one to the list
  if 'mac' in info:
    aps.append(info)

  return aps



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





