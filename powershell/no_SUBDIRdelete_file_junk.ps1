$folderPath = "C:\work\music\test"  # Change this to your target folder

# Get all files in the folder
$files = Get-ChildItem -Path $folderPath -File

foreach ($file in $files) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $extension = $file.Extension
    
    if ($baseName -match "^(.*)\(1\)$") {
        $originalName = "$($matches[1])$extension"
        $originalPath = Join-Path $folderPath $originalName
        
        if (Test-Path $originalPath) {
            # Delete the original file
            Remove-Item -Path $originalPath -Force
            Write-Output "Deleted: $originalPath"
        }
        
        # Rename the (1) file
        $newName = "$($matches[1])$extension"
        $newPath = Join-Path $folderPath $newName
        Rename-Item -Path $file.FullName -NewName $newName -Force
        Write-Output "Renamed: $($file.FullName) -> $newPath"
    }
}