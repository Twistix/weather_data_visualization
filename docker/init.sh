#!/bin/bash

cd /core && python3 download_arome_data.py -d rain temp && sleep 65 && python3 download_arome_data.py -d clouds
cd /core && python3 arome_data_to_image.py --mlat 38 --Mlat 53 --mlon -8 --Mlon 12 && cp -rf weather_outputs/ /website/

cron
httpd-foreground