#! /usr/bin/python

import subprocess as sp
import re
import os
import templater as tp
import time
import glob

def connect_vpn(conf,iface='wlan0', iface_eth='eth0'):
#  sp.call('./startvpn.sh', shell=True)
  sp.Popen('sudo openvpn --config '+conf+ '&', shell=True)
  file = open('lastvpn', 'w')
  file.write(conf)
  file.close()
  time.sleep(12)
  tp.fill_template(file='iptablesVPN2WLAN.sh', values={'iface':iface,'iface_eth':iface_eth})
  sp.call('chmod +x iptablesVPN2WLAN.sh', shell=True)
  sp.call('./iptablesVPN2WLAN.sh', shell=True)
  

def disconnect_vpn(iface='wlan0', iface_eth='eth0'):
  #sp.call('./stopvpn.sh', shell = True)
  sp.call('sudo killall openvpn', shell = True)
  #sp.call('sudo iptables -F', shell = True)
  tp.fill_template(file='iptablesETH2WLAN.sh', values={'iface':iface,'iface_eth':iface_eth})
  sp.call('chmod +x iptablesETH2WLAN.sh', shell=True)
  sp.call('./iptablesETH2WLAN.sh', shell=True)
  time.sleep(10)


def get_pid(process_name):
  proc = sp.Popen(['pidof '+process_name], shell=True, stdout = sp.PIPE )
  pid=[]
  for line in iter(proc.stdout.readline,''):
    pid = line.rstrip().split()
  return pid  

def stop_ap():
  '''Stop hostapd if it's running'''
  pid = get_pid('hostapd')
  if len(pid) > 0:
    sp.call('sudo killall hostapd', shell=True)
    time.sleep(5)

def connect_wifi(ssid, pwd, iface='wlan0', iface_eth="eth0"):
  '''Connect the given interface to an AP'''

  #kill AP if running:
  stop_ap()
  #fill templates:
  tp.fill_template(file='wpa_supplicant.conf', values={'ssid':ssid, 'pwd':pwd})
  tp.fill_template(file='interfaces.wifi', values={'iface':iface,'iface_eth':iface_eth})
  
  sp.call('sudo cp /etc/network/interfaces /etc/network/interfaces.bak',shell=True)  
  sp.call('sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak', shell=True)
  sp.call('sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf',shell=True)
  sp.call('sudo ifdown '+iface, shell=True)
  sp.call('sudo cp interfaces.wifi /etc/network/interfaces',shell=True)  
  sp.call('sudo ifup '+iface, shell=True)


def start_ap(ssid = 'flaskwf', pwd = '123flaskwf', subnet = '10.10.0.0', iface='wlan0', iface_eth='eth0'):
  ''' Start an AP based on the passed parameters '''  

  #Determine the network configuration based on the subnet (router is *.*.*.1)
  subnets = subnet.split('.')
  network = subnets[0]+'.'+subnets[1]+'.'+subnets[2]+'.0' 
  rangeMin= subnets[0]+'.'+subnets[1]+'.'+subnets[2]+'.2' 
  rangeMax = subnets[0]+'.'+subnets[1]+'.'+subnets[2]+'.10'
  routerIP = subnets[0]+'.'+subnets[1]+'.'+subnets[2]+'.1'
 
  #Generate the config files from templates
  tp.fill_template(file='hostapd.conf', values={'iface':iface,'ssid':ssid, 'pwd':pwd, 'ip':routerIP})
  tp.fill_template(file='interfaces.ap', values={'iface':iface, 'ip':routerIP, 'iface_eth':iface_eth})
  tp.fill_template(file='dhcpd.conf', values={'network':network, 'rangeMin':rangeMin,
                                              'rangeMax': rangeMax, 'routerIP': routerIP})

  #Rewrite the network interface file
  sp.call('sudo ifdown '+iface, shell=True)
  sp.call('sudo cp interfaces.ap /etc/network/interfaces',shell=True)  
  sp.call('sudo ifup '+iface, shell=True)

  #Rewrite the DHCP configuration file
  sp.call('sudo service isc-dhcp-server stop', shell=True)
  sp.call('sudo cp dhcpd.conf /etc/dhcp/dhcpd.conf',shell=True)  
  sp.call('sudo service isc-dhcp-server start ', shell=True)

  #start the access point (kill it if already running)

  stop_ap()
  sp.Popen('sudo hostapd hostapd.conf &', shell=True)
  time.sleep(10)

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

def get_interface_info():
  '''return a dictionnary with information on network interfaces'''
  interfaces = get_interface_list()
  info = {}
  for iface in interfaces:
    info[iface]=get_connection_info(iface)
  return info


def get_interface_list():
  '''return a list of network interfaces'''
  proc = sp.Popen("ip link show", stdout = sp.PIPE, shell=True)
  interfaces = []
  for line in iter(proc.stdout.readline,''):
    rline = line.rstrip()
    if rline.find('link/')>-1:
      continue
    interfaces.append( rline.split(':')[1].strip() )
  return interfaces 

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

def get_external_ip():
  '''get external ip address'''
  proc = sp.Popen("curl ipinfo.io/ip", stdout = sp.PIPE, shell=True)
  ip=''
  for line in iter(proc.stdout.readline,''):
    ip = line.rstrip()
  return ip

def get_ap_info(): 
  info = {}
  pid = get_pid('hostapd')
  if len(pid) > 0:
    info['pid'] = pid[0]
    hfile = open('hostapd.conf')
    for line in hfile:
      line = line.rstrip()
      if line.find('ssid') > -1 and 'ssid' not in info:
        info['ssid']=line.split('=')[1]
      if line.find('wpa_passphrase') > -1:
        info['pwd']=line.split('=')[1]  

  return info

def get_vpn_configs():
  files = glob.glob('vpns/*.ovpn') 
  return files
