from flask import Flask, request, render_template
from wifi import get_aps2, get_connection_info, write_wpa_file, write_hostapd_conf

app = Flask(__name__)



@app.route('/', methods = ['POST', 'GET'])
def wifilist():

  if request.method == 'POST':
  #The page was used to make a connection

    if 'pwd' in request.form: 
      #connect to a wifi
      pwd=request.form['pwd']
      ssid=request.form['ssid']
      write_wpa_file(ssid, pwd)

    if 'apssid' in request.form: 
      pwd=request.form['appwd']
      ssid=request.form['apssid']
      ip=request.form['apip']      
      write_hostapd_conf('wlan0', ssid, pwd, ip)

  aps = get_aps2('wlan0') 
  conn_info = get_connection_info('wlan0')
 
  return render_template("wifilist.html",aps = aps, conn_info = conn_info)


if __name__ == '__main__':
   app.run(host = '0.0.0.0')

