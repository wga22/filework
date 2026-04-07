c:

net use q: \\tenda\mediahub
REM docs
echo docs
xcopy "C:\Users\Will\Documents" "D:\personalbackup\documents" /e /c /q /r /y /z /d /i

rem PICS
echo pics - google DISABLED
rem xcopy "C:\Users\Will\Google Drive\Google Photos" "D:\personalbackup\Google Photos-Will" /e /c /q /r /y /z /d /i

REM music (both ways)
xcopy "D:\My Music\Pop" "Q:\Music" /e /c /q /r /y /z /d /i
xcopy "Q:\Music" "D:\My Music\Pop" /e /c /q /r /y /z /d /i

REM xcopy D:\Users\willallen\Documents w:\docs /e /c /q /r /y /z /d /i
rem xcopy C:\Detica w:\Detica /e /c /q /r /y /z /d /i


REM TENDA PHOTOS BEGIN----------------
rem 2018-Jan - skipping using tenda for now
REM create network connection

rem echo pics - main
rem xcopy "D:\personalbackup\My Pictures" "Q:\PersonalBackup\pictures" /e /c /q /r /y /z /d /i
REM xcopy "D:\personalbackup\Google Photos-Will" "Q:\PersonalBackup\pictures" /e /c /q /r /y /z /d /i
REM personal movies
rem echo personal movies
rem xcopy "D:\personalbackup\personal videos" "Q:\PersonalBackup\personal videos" /e /c /q /r /y /z /d /i
REM TENDA PHOTOS END-------------


net use q: /delete