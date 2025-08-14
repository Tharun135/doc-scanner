# Test upload script
$uri = "http://127.0.0.1:5000/upload"
$filePath = "D:\doc-scanner\test_upload_file.txt"

# Read file content
$fileContent = Get-Content $filePath -Raw
$fileBytes = [System.Text.Encoding]::UTF8.GetBytes($fileContent)

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"test_upload_file.txt`"",
    "Content-Type: text/plain$LF",
    $fileContent,
    "--$boundary--$LF"
) -join $LF

try {
    $response = Invoke-WebRequest -Uri $uri -Method Post -Body $bodyLines -ContentType "multipart/form-data; boundary=$boundary"
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Response: $($_.Exception.Response)"
}
