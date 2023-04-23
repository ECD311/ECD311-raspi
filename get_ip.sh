#!/usr/bin/bash
while ! ping -c 1 8.8.8.8
do sleep 1
done
_IP=$( hostname -I)||true
if [ "$_IP" ]
then
echo $(timedatectl | head -1 | xargs) > /home/pi/ip
echo $(ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+') >> /home/pi/ip
echo $(ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+')
scp -F /home/pi/.ssh/config -i /home/pi/.ssh/id_rsa /home/pi/ip bingdev:ip
else
>&2 echo "err: something broke"
fi
