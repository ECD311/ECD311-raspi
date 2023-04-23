## raspi
``/etc/cron`` should contain at minimum
``*/15 * * * * /home/pi/Scripts/get_ip.sh``
this runs the ``get_ip.sh`` script every 15 minutes, although running it that often is slightly overkill - once or twice a day would be plenty

if running twice a day, ``/etc/cron`` should contain 
``0 */12 * * * /home/pi/Scripts/get_ip.sh``

that file currently does not have exactly that line - it also includes the cronitor executable which sends the output of the ``get_ip.sh`` script to ``https://cronitor.io`` so failures cause alerts to fire

## bingdev
``crontab -e`` should contain at minimum
``*/15 * * * * python New_SQL_Transfer.py``
this runs the ``New_SQL_Transfer.py`` script every 15 minutes
