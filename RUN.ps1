clear
Add-Type -AssemblyName System.Windows.Forms

$folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog
$folderDialog.Description = "Select Search Folder"

if ($folderDialog.ShowDialog() -eq "OK") {
    $search_path = $folderDialog.SelectedPath
}

$folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog
$folderDialog.Description = "Select Output Folder"

if ($folderDialog.ShowDialog() -eq "OK") {
    $output_path = $folderDialog.SelectedPath
}

python .\main.py "$search_path" "$output_path"