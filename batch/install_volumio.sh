#!/bin/sh
#
# update thingspeak with details from tesla api
# deployed APR 2017
# TODO, setup and use env variable for NODEHOME

#DAC plugin settings
#https://volumio.org/forum/audiophonics-i2s-dac-sabre-es9023-two-types-t3095-40.html

#TODO: TEST!
echo 'TODO: test'

(apt-get update && apt-get -y upgrade) > /dev/null
apt-get dist-upgrade -y
apt-get install -y raspi-gpio git build-essential python-dev python-pip python-imaging python-smbus libasound2-dev nodejs hostapd dnsmasq
apt-get clean -y

#make needed directories
export NODEDIR='/home/volumio/node'
mkdir $NODEDIR
cd $NODEDIR

mkdir ~/.ssh
chmod 700 ~/.ssh
printf 'ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAgliJwIq6pGS7x7+u6U+8kilLBQ4tAfWFWFN5eP/tGXt2cqa4LwqA2cr1N1p7/WdgniDnwQgfyChAK5lDxDyCSGdoNuZ107sZe9d697+CLLSynwbEz5E+nW4LTvvmHidvyaAFp0J2FaYrHn/83EVqpxwCIc5A2y7pZHQKYDDBchcq/o4LmbWNVhquvH3Rpz5deAkwV7eSi/7sahYlV/IPMaNh/LLbBbduno5zZVoJKKlBwTAserpSjbzCCNOtLBUR+KSxuoJuFgatE2uF5m3jMgV4aouPGnBRLpBtCbmxjRHbFvjiUK0PdB8AtlsYLfogzaoREbclXh6qNgi7rC5YOw== rsa-key-20170312' > authorized_keys

chmod 600 ~/.ssh/authorized_keys

ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

#node
cd /tmp

#npm install fs-extra -g
#npm install socket.io-client -g
#npm install v-conf -g
#npm install onoff -g
#npm install kew -g
#npm install node-mpd -g

cd /volumio
npm update
#npm install fs-extra
#npm install socket.io-client
#npm install v-conf
#npm install onoff
#npm install kew
#npm install node-mpd

 