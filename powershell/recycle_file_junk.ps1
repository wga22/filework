$folderPath = "D:\My Music\Pop"  # Change this to your target folder

# Load the necessary .NET assembly for recycling files
Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class RecycleBin
    {
        [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
        public static extern int SHFileOperation(ref SHFILEOPSTRUCT lpFileOp);
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct SHFILEOPSTRUCT
        {
            public IntPtr hwnd;
            public int wFunc;
            public string pFrom;
            public string pTo;
            public short fFlags;
            public bool fAnyOperationsAborted;
            public IntPtr hNameMappings;
            public string lpszProgressTitle;
        }
        public static void SendToRecycleBin(string path)
        {
            SHFILEOPSTRUCT shf = new SHFILEOPSTRUCT();
            shf.wFunc = 3;
            shf.pFrom = path + "\0";
            shf.fFlags = 0x40 | 0x10;
            SHFileOperation(ref shf);
        }
    }
"@ -Language CSharp

# Get all files in the folder and subdirectories
$files = Get-ChildItem -Path $folderPath -File -Recurse

foreach ($file in $files) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $extension = $file.Extension
    
    if ($baseName -match "^(.*)\(1\)$") {
        $originalName = "$($matches[1])$extension"
        $originalPath = Join-Path $file.DirectoryName $originalName
        
        if (Test-Path $originalPath) {
            # Move the original file to the Recycle Bin
            [RecycleBin]::SendToRecycleBin($originalPath)
            Write-Output "Moved to Recycle Bin: $originalPath"
        }
        
        # Rename the (1) file
        $newName = "$($matches[1])$extension"
        $newPath = Join-Path $file.DirectoryName $newName
        Rename-Item -Path $file.FullName -NewName $newName -Force
        Write-Output "Renamed: $($file.FullName) -> $newPath"
    }
}