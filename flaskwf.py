from flask import Flask, request, render_template
import wifi as wf


app = Flask(__name__)

#hostapd_proc = ''

@app.route('/', methods = ['POST', 'GET'])
def wifilist():

  #global hostapd_proc
  aps=[] #list of APs if scan was called

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

    if 'connect_vpn' in request.form:  
      wf.connect_vpn(request.form['vpn_config'])

    if 'disconnect_vpn' in request.form:
      wf.disconnect_vpn()

    if 'scan' in request.form:    
      aps = wf.get_aps2('wlan0')
      message = 'done scanning'

  else:
    aps = wf.get_aps('wlan0') 


  conn_info = wf.get_connection_info('wlan0')
  vpn_info = wf.get_connection_info('tun0')
  vfile = open('lastvpn')
  lastvpn=vfile.readline()
  vfile.close()
  vpn_info['lastvpn']=lastvpn
  vpn_confs = wf.get_vpn_configs()
  hostapd_info = wf.get_ap_info()

  if 'ip' not in conn_info or conn_info['ip'].find('.') <0:
    hostapd_proc = wf.start_ap(ssid = ssid, pwd = pwd, ip = ip, iface='wlan0')
    conn_info = wf.get_connection_info('wlan0')


  return render_template("wifilist.html",aps = aps,
                         conn_info = conn_info,
                         vpn_info = vpn_info,
                         vpn_confs = vpn_confs,
                         hostapd_info = hostapd_info,
                         message=message,
                         url_root=request.url_root)


if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug=True)

