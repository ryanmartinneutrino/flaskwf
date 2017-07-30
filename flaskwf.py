from flask import Flask, request, render_template
import wifi as wf


app = Flask(__name__)

#hostapd_proc = ''

@app.route('/', methods = ['POST', 'GET'])
def wifilist():
#The main page:

  aps=[] #list of APs if scan was called
  interfaces = wf.get_interface_list()
 
  message = '' 
  iface_wifi= "unset"
  iface_wired= "unset"

  #Use these by default if they exists
  if 'wlan0' in interfaces:
    iface_wifi = 'wlan0'
  if 'eth0' in interfaces:
    iface_wired = 'eth0'

  if request.method == 'POST':

    if "choose_iface" in request.form:
      iface_wifi=request.form['new_iface_wifi']
      iface_wired=request.form['new_iface_wired']

    else:
      iface_wifi=request.form['iface_wifi']
      iface_wired=request.form['iface_wired']
   
    if 'connect' in request.form: 
      if iface_wifi != "unset":
        #connect to a wifi
        pwd=request.form['pwd']
        ssid=request.form['ssid']
        wf.connect_wifi(ssid, pwd, iface=iface_wifi, iface_eth=iface_wired)
        message = 'wrote wpa_supplicant.conf'
      else:
        message = "Need wifi interface to be set to connect"

    if 'start_ap' in request.form:
      if iface_wifi != "unset" : 
        pwd=request.form['appwd']
        ssid=request.form['apssid']
        subnet=request.form['apsubnet']      
        wf.start_ap(ssid = ssid, pwd = pwd, subnet = subnet, iface=iface_wifi, iface_eth=iface_wired)
        message = 'started AP, wrote hostapd.conf and interfaces'
      else:
        message = "Need wifi interface to be set for AP to run" 

    if 'stop_ap' in request.form: 
      wf.stop_ap()   
      message = 'stopped AP'

    if 'connect_vpn' in request.form:
      if iface_wifi != "unset" and iface_wired != "unset":  
        wf.connect_vpn(request.form['vpn_config'],iface=iface_wifi, iface_eth=iface_wired)
        message = "connected VPN"
      else:
        message = "Need to set both interfaces for VPN!"

    if 'disconnect_vpn' in request.form:
      wf.disconnect_vpn(iface=iface_wifi, iface_eth=iface_wired)
      message = "disconnected VPN"

    if 'scan' in request.form:
      if iface_wifi != "unset":    
        aps = wf.get_aps2(iface=iface_wifi)
        message = 'done scanning'
      else:
        message = "Need to set wifi interface to scan!"

  else: #Get request
    if iface_wifi != "unset" :
      aps = wf.get_aps(iface=iface_wifi) 
    else:
      aps = []
      message = "need wifi interface to be set for AP list"

  iface_info = wf.get_interface_info()
  external_ip = wf.get_external_ip()

  if 'tun0' in iface_info:
    vfile = open('lastvpn')
    lastvpn=vfile.readline()
    vfile.close()
    iface_info['tun0']['lastvpn']=lastvpn

  vpn_confs = wf.get_vpn_configs()
  hostapd_info = wf.get_ap_info()

  #Start AP if no wifi (untested!!!)
  if iface_wifi  != "unset": 
    if 'ip' not in iface_info[iface_wifi]  or iface_info[iface_wifi]['ip'].find('.') <0:
      wf.start_ap(ssid = 'flaskwf', pwd = '123flask', ip = '10.10.0.0', iface=iface_wifi, iface_eth=iface_wired)
      iface_info[iface_wifi] = wf.get_connection_info(iface_wifi)


  return render_template("wifilist.html",aps = aps,
                         iface_info = iface_info,
                         external_ip = external_ip,
                         vpn_confs = vpn_confs,
                         hostapd_info = hostapd_info,
                         message=message,
                         url_root=request.url_root,
                         iface_wifi=iface_wifi,
                         iface_wired=iface_wired)


if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug=True)

