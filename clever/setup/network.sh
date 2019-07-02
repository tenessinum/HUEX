#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

sudo iw dev wlan0 scan | grep SSID

read -p 'SSID: ' ssid
read -sp 'Password: ' pass

sudo systemctl stop dnsmasq
sudo systemctl disable dnsmasq

sudo sed -i 's/interface wlan0//' /etc/dhcpcd.conf
sudo sed -i 's/static ip_address=192.168.11.1\/24//' /etc/dhcpcd.conf

sudo cat << EOF > /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={
    ssid="$ssid"
    psk="$pass"
}

EOF

sudo systemctl restart dhcpcd
