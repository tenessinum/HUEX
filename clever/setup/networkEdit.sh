#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

sudo iw dev wlan0 scan | grep SSID

readarray array < /home/pi/networkData.txt

index=0

while read line; do
	array[$index]="$line"
	index=$(($index+1));
done < /home/pi/networkData.txt

ssid=${array[0]}
pass=${array[1]}

echo "Check your SSID and password"
echo "=========================================="

echo "Network name:   $ssid"
echo "Password:       $pass"

echo  "========================================="
echo -n "Is your data correct? Want to continue? [Y/n] "

read item
case $item in 
y|Y) 

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
;;
n|N) echo "Successful setup!!!"
;;
*) exit 0 
;;
esac