#!/bin/sh
#wget https://downloads.plex.tv/plex-media-server/1.8.4.4249-3497d6779/plexmediaserver_1.8.4.4249-3497d6779_amd64.deb
echo deb https://downloads.plex.tv/repo/deb ./public main | sudo tee /etc/apt/sources.list.d/plexmediaserver.list
curl https://downloads.plex.tv/plex-keys/PlexSign.key | sudo apt-key add -
