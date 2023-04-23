## get_ip.service
the unit file for this service is at ``/etc/systemd/system/get_ip.service``
it runs the ``/home/pi/Scripts/get_ip.sh`` script once on boot to ensure that whatever dynamic IP the pi gets is known as soon as possible
the service does not run until the pi has at least *some* name lookup capability


## recv_data.service
the unit file for this service is at ``/etc/systemd/system/recv_data.service``
it runs the ``/home/pi/Scripts/test_serial.py`` script after the network is available - this may be before name lookup is available, but this will not have a significant impact on the functionality of the script as it takes approximately 30 minutes before name lookup is required
the service will restart the python script on any exit, but systemd will give up on restarting it if there are too many restarts in a short period of time