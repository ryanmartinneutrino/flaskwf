#! /bin/bash

sudo iptables -F
sudo iptables -A INPUT -i eth0 -j ACCEPT
sudo iptables -A OUTPUT -o eth0 -j ACCEPT

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

#sudo sh –c “iptables-save > /etc/iptables.restore” $ echo “up iptables-restore < /etc/iptables.restore” | sudo tee --append /etc/network/interfaces

