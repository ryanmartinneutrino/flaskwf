from flask import Flask, request, render_template
from wifi import get_aps2, get_connection_info
app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def wifilist():
  aps = get_aps2('wlan0') 
  conn_info = get_connection_info('wlan0')
  if request.method == 'POST':
    pwd=request.form['pwd']
    id=request.form['ssid']
  return render_template("wifilist.html",aps = aps, conn_info = conn_info)


if __name__ == '__main__':
   app.run(host = '0.0.0.0')

