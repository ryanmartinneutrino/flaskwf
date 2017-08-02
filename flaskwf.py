from flask import Flask, request, render_template
import wifi as wf


app = Flask(__name__)

#hostapd_proc = ''

@app.route('/', methods = ['POST', 'GET'])
def wifilist():
#The main page:

  aps=[] #list of APs if scan was called

  message = ''
  iface_wifi= "unset"
  iface_ap = "unset"
  iface_wired= "unset"
  iface_internet = wf.get_internet_iface()

  iface_wifi_list = wf.get_wifi_interfaces()
  iface_wifi_list.append("unset")
  iface_wired_list = wf.get_wired_interfaces()
  iface_wired_list.append("unset")
  nwifi = len(iface_wifi_list)

  #wf.write_network_interfaces()

  #Guess interfaces to use
  if nwifi>0:
    iface_ap=iface_wifi_list[0]
    iface_wifi=iface_wifi_list[0]
  if nwifi>1:
    iface_wifi=iface_wifi_list[1]
  if len(iface_wired_list)>0:
    iface_wired=iface_wired_list[0]

  if request.method == 'POST':

    if 'connect' in request.form:
      iface_ap = request.form['iface_ap']
      iface_wired=request.form['iface_wired']
      iface_wifi=request.form['new_iface_wifi']

      if iface_wifi != "unset":
        #connect to a wifi
        pwd=request.form['pwd']
        ssid=request.form['ssid']
        #wf.connect_wifi(ssid, pwd, iface=iface_wifi, iface_eth=iface_wired)
        if iface_wifi == iface_ap:
            wf.stop_ap()
            iface_ap = "unset"

        wf.connect_wifi(ssid, pwd, wifi_interface=iface_wifi, ap_interface=iface_ap, ap_ip='10.10.0.1')
        message = 'wrote wpa_supplicant.conf'
      else:
        message = "Need wifi interface to be set to connect"

    if 'start_ap' in request.form:
      iface_wifi=request.form['iface_wifi']
      iface_wired=request.form['iface_wired']
      iface_ap=request.form['new_iface_ap']

      if iface_ap != "unset" :
        pwd=request.form['appwd']
        ssid=request.form['apssid']
        subnet=request.form['apsubnet']
        if iface_ap == iface_wifi:
            iface_wifi="unset"

        wf.start_ap(ssid = ssid, pwd = pwd, subnet = subnet, wifi_interface=iface_wifi, ap_interface=iface_ap)
        message = 'started AP, wrote hostapd.conf and interfaces'
      else:
        message = "Need wifi interface to be set for AP to run"

    if 'stop_ap' in request.form:
      iface_wifi=request.form['iface_wifi']
      iface_wired=request.form['iface_wired']
      iface_ap=request.form['iface_ap']
      wf.stop_ap()
      message = 'stopped AP'

    if 'connect_vpn' in request.form:
      iface_wifi=request.form['iface_wifi']
      iface_wired=request.form['iface_wired']
      iface_ap=request.form['iface_ap']

      if iface_ap != "unset" and iface_wired != "unset":
        wf.connect_vpn(request.form['vpn_config'],iface_ap=iface_ap)
        message = "connected VPN"
      else:
        message = "Need to set both interfaces for VPN!"

    if 'disconnect_vpn' in request.form:
      iface_wifi=request.form['iface_wifi']
      iface_wired=request.form['iface_wired']
      iface_ap=request.form['iface_ap']

      wf.disconnect_vpn(iface_ap=iface_ap)
      message = "disconnected VPN"

    if 'scan' in request.form:
      iface_wired=request.form['iface_wired']
      iface_ap=request.form['iface_ap']
      iface_wifi=request.form['iface_wifi']
      if iface_wifi != "unset":
        aps = wf.get_aps2(iface=request.form['iface_scan'])
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
  if iface_ap  != "unset":
    if 'ip' not in iface_info[iface_ap]  or iface_info[iface_ap]['ip'].find('.') <0:
      wf.start_ap(ssid = 'flaskwf', pwd = '123flaskwf', subnet = '10.10.0.0', wifi_interface=iface_wifi, ap_interface=iface_ap)
      iface_info[iface_ap] = wf.get_connection_info(iface_ap)

  return render_template("wifilist.html",aps = aps,
                         iface_info = iface_info,
                         external_ip = external_ip,
                         vpn_confs = vpn_confs,
                         hostapd_info = hostapd_info,
                         message=message,
                         url_root=request.url_root,
                         iface_wifi_list=iface_wifi_list,
                         iface_wired_list=iface_wired_list,
                         iface_ap=iface_ap,
                         iface_wifi=iface_wifi,
                         iface_wired=iface_wired,
                         iface_internet=iface_internet)


if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug=True)
