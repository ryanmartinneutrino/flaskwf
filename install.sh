#! /bin/bash

#sudo apt-get update
sudo apt-get install -y  iw hostapd isc-dhcp-server openvpn


#enable ipv4 forwarding (for vpn)
echo -e '\n#Enable IP Routing\nnet.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

#make backups
sudo cp /etc/network/interfaces /etc/network/interfaces.orig
sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.orig




