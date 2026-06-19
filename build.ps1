Write-Host "🔍 Syntax check..." -ForegroundColor Cyan
python -m compileall backend/src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "🧹 Linting with flake8..." -ForegroundColor Cyan
flake8 backend/src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "🔎 Type checking with mypy..." -ForegroundColor Cyan
mypy backend/src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Write-Host "🧪 Running tests..." -ForegroundColor Cyan
# pytest -q
# if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "✅ Build successful!" -ForegroundColor Green
