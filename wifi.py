#! /usr/bin/python

import subprocess as sp
import re
import os
import templater as tp


def connect_wifi(ssid, pwd, iface='wlan0'):
  tp.fill_template(file='wpa_supplicant.conf', values={'ssid':ssid, 'pwd':pwd})
  tp.fill_template(file='interfaces.wifi', values={'iface':iface})
  
  sp.call('sudo cp /etc/network/interfaces /etc/network/interfaces.bak',shell=True)  
  sp.call('sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak', shell=True)
  sp.call('sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf',shell=True)
  sp.call('sudo ifdown '+iface, shell=True)
  sp.call('sudo cp interfaces.wifi /etc/network/interfaces',shell=True)  
  sp.call('sudo ifup '+iface, shell=True)


def start_ap(ssid = 'flaskwf', pwd = '1257Berkeley', ip = '10.10.0.1', iface='wlan0'):

  tp.fill_template(file='hostapd.conf', values={'iface':iface,'ssid':ssid, 'pwd':pwd, 'ip':ip})
  tp.fill_template(file='interfaces.ap', values={'iface':iface, 'ip':ip})
  tp.fill_template(file='dhcpd.conf', values={'network':'10.10.0.0'})

  #sp.call('sudo cp hostapd.conf /etc/hostapd/hostapd.conf',shell=True)  
  sp.call('sudo cp dhcpd.conf /etc/dhcp/dhcpd.conf',shell=True)  
  sp.call('sudo ifdown '+iface, shell=True)
  sp.call('sudo cp interfaces.ap /etc/network/interfaces',shell=True)  
  sp.call('sudo ifup '+iface, shell=True)


  sp.call('sudo service isc-dhcp-server restart ', shell=True)
  #sp.call('sudo service hostapd restart', shell=True)
  sp.call('sudo ../hostapd hostapd.conf', shell=True)

def ifup(iface='wlan0'):
  sp.call('sudo ifup '+iface, shell=True)

def ifdown(iface='wlan0'):
  sp.call('sudo ifdown '+iface, shell=True)

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





