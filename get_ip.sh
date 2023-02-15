#!/usr/bin/bash
_IP=$( hostname -I)||true
if [ "$_IP" ]
then
echo $(timedatectl | head -1 | xargs) > /home/pi/ip
echo $(ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+') >> /home/pi/ip
scp -F /home/pi/.ssh/config -i /home/pi/.ssh/id_rsa /home/pi/ip bingdev:ip
fi
