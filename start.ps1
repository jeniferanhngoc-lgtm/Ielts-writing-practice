Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    Write-Host 'Chua co moi truong Python. Xem README.md de cai dat.'
    exit 1
}
& '.\.venv\Scripts\python.exe' -m streamlit run app.py --server.address 127.0.0.1
