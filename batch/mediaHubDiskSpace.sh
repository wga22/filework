#!/bin/sh
df /mnt/mediahub | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 " " $1 }' | while read output;
do
  echo $output
  usep=$(echo $output | awk '{ print $1}' | cut -d'%' -f1  )
  partition=$(echo $output | awk '{ print $2 }' )
  if [ $usep -ge 85 ]; then
    echo "Running out of space \"$partition ($usep%)\" on $(hostname) as on $(date)" |
     mail -s "Alert: Almost out of disk space $usep%" will.allen@gmail.com
  fi
done