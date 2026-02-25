@echo off
:: --- CONFIGURATION ---
:: Using UNC path for reliability in background tasks
:: SET "SOURCE=\\spiderman.lan\ten\backup\personalbackup\immich_library\library\admin"
SET "SOURCE=\\spiderman.lan\ten\backup\personalbackup\immich_library\admin"


SET "TARGET1=C:\Users\wga22\Pictures\Camera Roll"
SET "TARGET2=D:\personalbackup\AllPictures"

:: --- LOGGING ---
SET "LOGFILE=C:\Users\wga22\Documents\PhotoSyncLog.txt"

echo --------------------------------------------------- > "%LOGFILE%"
echo Starting Sync at %DATE% %TIME% >> "%LOGFILE%"

:: --- SYNC JOB 1 (To C: Drive) ---
:: /E  = Copy subdirectories, including empty ones
:: /XO = Exclude Older (Only copy new/changed files)
:: /FFT = Assume FAT File Times (useful for Linux-to-Windows time differences)
:: /R:3 = Retry 3 times
:: /W:5 = Wait 5 seconds between retries
echo Syncing to Target 1... >> "%LOGFILE%"
robocopy "%SOURCE%" "%TARGET1%" /E /XO /FFT /R:3 /W:5 >> "%LOGFILE%"

:: --- SYNC JOB 2 (To D: Drive) ---
echo Syncing to Target 2... >> "%LOGFILE%"
robocopy "%TARGET1%" "%TARGET2%" /E /XO /FFT /R:3 /W:5 >> "%LOGFILE%"

echo Finished Sync at %DATE% %TIME% >> "%LOGFILE%"