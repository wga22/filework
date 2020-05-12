
#!/bin/bash
# You will need to tune these lines for your system
# https://www.reddit.com/r/PleX/comments/81gfwn/my_linux_postprocessing_script/
execdir="/home/will/processed"
medialoc="/media/ten/video/tv"
hboptions="-f mkv --aencoder copy -e qsv_h264 --x264-preset slow --x264-profile auto -q 16 --maxHeight 720 --decomb bob"
#
# edit below at your own risk
if pgrep -x "HandBrakeCLI" > /dev/null
then
    echo "HanBrakeCLI is already working"
else
    echo "HanBrakeCLI stopped, let's do some work!"
    /usr/bin/find "$medialoc" -name "*.ts" -print0 | while IFS= read -r -d $'\0' file ; do
        tempfile=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)".tmp"
        temptarget="$execdir/$tempfile"
        echo $(date "+%Y%m%d-%H%M%S")": $tempfile $file" >> "$execdir/encode.log"
        if nice -n 20 HandBrakeCLI -i "$file" "\ $hboptions" -o "$temptarget" </dev/null ; then
            wait
            sleep 5
            if mv -f "$temptarget" "${file%.ts}.mkv"; then
                rm -f "$file"
            fi
        else
            echo "Process failed for: $file" >> "$execdir/encode.log"
        fi
    done
fi
