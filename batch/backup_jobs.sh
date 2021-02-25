#!/bin/bash
# move movies from the dropfolder to the plex folder
BACKUPFOLDER=/media/ten/backup
NEXTCLOUDDATA=/var/www/nextcloud/data
NCCAMERA=/files/InstantUpload/Camera
NCCAMERA2=/files/Photos
PHOTOTARGET=/media/ten/backup/personalbackup/allphotos

tar -czvf $BACKUPFOLDER/backupconfig.tgz /root/backupconfig/
tar -czvf $BACKUPFOLDER/etc.tgz /etc/
tar -czvf $BACKUPFOLDER/opt.tgz /opt/

# TODO: photos from nextcloud
# /var/www/nextcloud/data/will/files/InstantUpload/Camera
cp -u -r $NEXTCLOUDDATA/danielle$NCCAMERA2/* $PHOTOTARGET
cp -u -r $NEXTCLOUDDATA/danica$NCCAMERA2/* $PHOTOTARGET
cp -u -r $NEXTCLOUDDATA/will$NCCAMERA/* $PHOTOTARGET

chown -R will:will $PHOTOTARGET/*
