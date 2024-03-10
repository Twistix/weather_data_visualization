#!/bin/bash

cd /core && python3 download_arome_data.py -d rain && sleep 65 && python3 download_arome_data.py -d temp && sleep 65 && python3 download_arome_data.py -d clouds
cd /core && python3 arome_data_to_image.py --mlat 40 --Mlat 54 --mlon -8 --Mlon 12 -p EPSG:3857 && cp -rf weather_outputs/ /website/

cron
httpd-foreground