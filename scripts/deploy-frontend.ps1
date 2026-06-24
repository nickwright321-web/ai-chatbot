try {

Write-Host "Running sam validate..."
sam validate --template-file .\frontend\template.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "sam validate failed. Stopping script."
    exit 1
}

Write-Host "Validation successful."

# Delete .aws-sam folder if it exists
if (Test-Path ".aws-sam") {
    Write-Host "Deleting .aws-sam folder..."
    Remove-Item -Recurse -Force ".aws-sam"
} else {
    Write-Host ".aws-sam folder not found, skipping delete."
}

# Run sam build
Write-Host "Running sam build..."
sam build --template-file .\frontend\template.yaml

Write-Host "Assuming deployment role..."

$credsJson = aws sts assume-role `
  --role-arn "arn:aws:iam::132696833143:role/sam-deployer-role" `
  --role-session-name "deploy" | ConvertFrom-Json

$env:AWS_ACCESS_KEY_ID     = $credsJson.Credentials.AccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $credsJson.Credentials.SecretAccessKey
$env:AWS_SESSION_TOKEN     = $credsJson.Credentials.SessionToken

Remove-Item Env:AWS_PROFILE -ErrorAction SilentlyContinue

Write-Host "Role assumed..."

aws sts get-caller-identity

# Run sam deploy
Write-Host "Running sam deploy..."
sam deploy `
  --template-file frontend/template.yaml `
  --stack-name ai-chatbot-frontend `
  --region eu-west-2 `
  --s3-bucket nick-ai-chatbot-artifacts `
  --capabilities CAPABILITY_NAMED_IAM `

# ---------------------------------------------------------
# Build Frontend (Vite)
# ---------------------------------------------------------
Write-Host "Building frontend..."
npm --prefix ./frontend run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed. Stopping script."
    exit 1
}

Write-Host "Frontend build complete."

# ---------------------------------------------------------
# Sync dist/ to S3
# ---------------------------------------------------------
$bucketName = "ai-chatbot-frontend-132696833143-eu-west-2"

Write-Host "Syncing frontend dist/ to S3 bucket $bucketName ..."
aws s3 sync ./frontend/dist/ s3://$bucketName/ --delete

if ($LASTEXITCODE -ne 0) {
    Write-Host "S3 sync failed. Stopping script."
    exit 1
}

Write-Host "Frontend uploaded successfully."

# ---------------------------------------------------------
# CloudFront Invalidation
# ---------------------------------------------------------
$distributionId = "E8WKHQK0AO4J6"

Write-Host "Invalidating CloudFront cache for distribution $distributionId ..."
aws cloudfront create-invalidation --distribution-id $distributionId --paths "/*"

if ($LASTEXITCODE -ne 0) {
    Write-Host "CloudFront invalidation failed."
    exit 1
}

Write-Host "CloudFront invalidation complete."
Write-Host "Deployment finished successfully."
}

finally {   
    Write-host "Cleaning up..."

    Remove-Item Env:AWS_ACCESS_KEY_ID
    Remove-Item Env:AWS_SECRET_ACCESS_KEY
    Remove-Item Env:AWS_SESSION_TOKEN

    Write-Host "Clean up complete"
}