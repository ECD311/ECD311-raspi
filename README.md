# ECD311-raspi

this repository contains all scripts and unit files that are used on the raspberry pi as well as the bingdev server

the 2 scripts that run on bingdev are ``cleanup_archive.py`` and ``New_SQL_Transfer.py``
all other files are for the raspberry pi

one file is not included in the repository - ``conf.py`` contains API keys for openweathermap and cronitor, as well as the SQL table to write to and the password for that SQL server

``conf.py`` also includes the latitude and longitude used to calculate the position of the sun and the location to use for weather data from openweathermap