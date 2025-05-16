# Create analysis timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$output_file = "workspace_analysis_$timestamp.txt"

# Analyze workspace structure
Write-Output "Sprint2Vec Workspace Analysis ($timestamp)`n" | Out-File $output_file

# Directory structure
Write-Output "Directory Structure:`n" | Out-File $output_file -Append
Get-ChildItem -Path "D:\REVA\Capstone1\sprint2vec_revision" -Directory | 
Select-Object FullName | Format-Table -AutoSize | 
Out-File $output_file -Append

# File listing with details
Write-Output "`nFile Details:`n" | Out-File $output_file -Append
Get-ChildItem -Path "D:\REVA\Capstone1\sprint2vec_revision" -Recurse | 
Where-Object { -not $_.PSIsContainer } | 
Select-Object FullName, Length, LastWriteTime | 
Format-Table -AutoSize | 
Out-File $output_file -Append

# Dataset files
Write-Output "`nDataset Files:`n" | Out-File $output_file -Append
Get-ChildItem -Path "D:\REVA\Capstone1\sprint2vec_revision\Dataset" -Recurse -Include *.csv.gz | 
Select-Object FullName, Length | Format-Table -AutoSize | 
Out-File $output_file -Append

Write-Output "Analysis saved to: $output_file"