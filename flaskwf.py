from flask import Flask, request, render_template
import wifi as wf

app = Flask(__name__)



@app.route('/', methods = ['POST', 'GET'])
def wifilist():

  aps=[] #list of APs if scan was called

  message = '' 

  if request.method == 'POST':

    if 'connect' in request.form: 
      #connect to a wifi
      pwd=request.form['pwd']
      ssid=request.form['ssid']
      wf.connect_wifi(ssid, pwd)
      message = 'wrote wpa_supplicant.conf'

    if 'ap' in request.form: 
      pwd=request.form['appwd']
      ssid=request.form['apssid']
      ip=request.form['apip']      
      wf.start_ap(ssid = 'flaskwf', pwd = '1257Berkeley', ip = '10.10.0.1', iface='wlan0')
      message = 'wrote hostapd.conf and interfaces'

    if 'scan' in request.form:    
      aps = wf.get_aps2('wlan0')
      message = 'done scanning'

  else:
    aps = wf.get_aps('wlan0') 

  conn_info = wf.get_connection_info('wlan0')

  return render_template("wifilist.html",aps = aps,
                         conn_info = conn_info,
                         message=message,
                         url_root=request.url_root)


if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug=True)

