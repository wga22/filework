# Define source and target directories
$SourceDir = "D:\My Music\Pop"
$TargetDir = "Z:\music\Pop"

Write-Output "Starting folder replacement process..."
Write-Output "Source Directory: $SourceDir"
Write-Output "Target Directory: $TargetDir"

# Get folders in the source directory that were modified in the last 24 hours
$UpdatedFolders = Get-ChildItem -Path $SourceDir -Directory | Where-Object { $_.LastWriteTime -ge (Get-Date).AddDays(-1) }

if ($UpdatedFolders.Count -eq 0) {
    Write-Output "No folders updated in the last 24 hours. Process complete."
    exit
}

foreach ($Folder in $UpdatedFolders) {
    $TargetFolder = Join-Path -Path $TargetDir -ChildPath $Folder.Name

    Write-Output "Processing folder: $($Folder.Name)"

    # Remove existing folder in the target directory if it exists
    if (Test-Path $TargetFolder) {
        Write-Output "Removing existing folder: $TargetFolder"
        Remove-Item -Path $TargetFolder -Recurse -Force
    }

    # Copy the updated folder to the target directory
    Write-Output "Copying folder: $($Folder.FullName) to $TargetDir"
    Copy-Item -Path $Folder.FullName -Destination $TargetDir -Recurse -Force

    Write-Output "Folder $($Folder.Name) has been replaced."
}

Write-Output "All updated folders have been processed successfully."
