#Base image
FROM    httpd:2.4

#Init
USER    root
WORKDIR /

#Install dependencies
RUN     apt update && \
        apt install -y python3 python3-pip libeccodes-dev cron vim && \
        apt clean

#Install Python packages
RUN     apt install -y python3-eccodes python3-numpy python3-matplotlib python3-requests && \
        apt clean

#Copy repository files
COPY    core /core
COPY    website /website
COPY    docker/init.sh /init.sh

#Setup permissions
RUN     chmod 755 /init.sh

#Configure HTTPD document root
RUN     sed -i 's/\/usr\/local\/apache2\/htdocs/\/website/g' /usr/local/apache2/conf/httpd.conf

#Setup cron
RUN     echo "0 */3 * * * cd /core && python3 download_arome_data.py -d rain temp && sleep 65 && python3 download_arome_data.py -d clouds" >> /etc/crontab
RUN     echo "12 * * * * cd /core && python3 arome_data_to_image.py --mlat 40 --Mlat 54 --mlon -8 --Mlon 12 && cp -rf weather_outputs/ /website/" >> /etc/crontab

#Workdir (dev purpose)
RUN     mkdir -p /workdir
RUN     chmod -R 777 /workdir
WORKDIR /workdir

#Start command
CMD     /init.sh
