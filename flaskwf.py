from flask import Flask, request, render_template
import wifi as wf


app = Flask(__name__)

#hostapd_proc = ''

@app.route('/', methods = ['POST', 'GET'])
def wifilist():

  aps=[] #list of APs if scan was called
  interfaces = wf.get_interface_list()

  message = '' 

  if request.method == 'POST':

    if 'connect' in request.form: 
      #connect to a wifi
      pwd=request.form['pwd']
      ssid=request.form['ssid']
      wf.connect_wifi(ssid, pwd)
      message = 'wrote wpa_supplicant.conf'

    if 'start_ap' in request.form: 
      pwd=request.form['appwd']
      ssid=request.form['apssid']
      subnet=request.form['apsubnet']      
      wf.start_ap(ssid = ssid, pwd = pwd, subnet = subnet, iface='wlan0')
      message = 'started AP, wrote hostapd.conf and interfaces'
 
    if 'stop_ap' in request.form: 
      wf.stop_ap()   
      message = 'stopped AP'

    if 'connect_vpn' in request.form:  
      wf.connect_vpn(request.form['vpn_config'])
      message = "connected VPN"

    if 'disconnect_vpn' in request.form:
      wf.disconnect_vpn()
      message = "disconnected VPN"

    if 'scan' in request.form:    
      aps = wf.get_aps2('wlan0')
      message = 'done scanning'

  else:
    if 'wlan0' in interfaces:
      aps = wf.get_aps('wlan0') 
    else:
      aps = []

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
  if 'wlan0' in interfaces: 
    if 'ip' not in iface_info['wlan0']  or iface_info['wlan0']['ip'].find('.') <0:
      wf.start_ap(ssid = 'flaskwf', pwd = '123flask', ip = '10.10.0.0', iface='wlan0')
      iface_info['wlan0'] = wf.get_connection_info('wlan0')


  return render_template("wifilist.html",aps = aps,
                         iface_info = iface_info,
                         external_ip = external_ip,
                         vpn_confs = vpn_confs,
                         hostapd_info = hostapd_info,
                         message=message,
                         url_root=request.url_root)


if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug=True)

