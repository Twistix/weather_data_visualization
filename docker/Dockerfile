#Base image
FROM    httpd:2.4

#Init
USER    root
WORKDIR /

#Install dependencies
RUN     apt update && \
        apt install -y python3 python3-pip libeccodes-dev cron vim gdal-bin && \
        apt clean

#Install Python packages
RUN     pip3 install --break-system-packages eccodes numpy matplotlib requests && \
        pip3 cache purge

#Copy repository files
COPY    core /core
COPY    website /website
COPY    docker/init.sh /init.sh

#Setup permissions
RUN     chmod 755 /init.sh

#Configure HTTPD document root
RUN     sed -i 's/\/usr\/local\/apache2\/htdocs/\/website/g' /usr/local/apache2/conf/httpd.conf

#Setup cron
RUN     echo "0 */3 * * * root cd /core && python3 download_arome_data.py -d rain && sleep 120 && python3 download_arome_data.py -d temp && sleep 120 && python3 download_arome_data.py -d clouds" >> /etc/crontab
RUN     echo "15 * * * * root cd /core && python3 arome_data_to_image.py --mlat 40 --Mlat 54 --mlon -8 --Mlon 12 -p EPSG:3857 && cp -rf weather_outputs/ /website/" >> /etc/crontab

#Workdir (dev purpose)
RUN     mkdir -p /workdir
RUN     chmod -R 777 /workdir
WORKDIR /workdir

#Start command
CMD     /init.sh
