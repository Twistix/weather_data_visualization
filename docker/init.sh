#!/bin/bash

cd /core && python3 download_arome_data.py -d rain temp && sleep 65 && python3 download_arome_data.py -d clouds
cd /core && python3 arome_data_to_image.py --mlat 41.5 --Mlat 45 --mlon -0.4 --Mlon 3.6 -b osm && cp -rf meteo_outputs/ /website/

cron
httpd-foreground