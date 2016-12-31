#! /bin/bash

sudo iptables -t nat -A POSTROUTING -o tun0 -j MASQUERADE
sudo iptables -A FORWARD -i tun0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan00 -o tun0 -j ACCEPT

#sudo sh –c “iptables-save > /etc/iptables.restore” $ echo “up iptables-restore < /etc/iptables.restore” | sudo tee --append /etc/network/interfaces

