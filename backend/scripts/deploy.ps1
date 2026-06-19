Write-Host "Running sam validate..."
sam validate

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
sam build

# Run sam deploy
Write-Host "Running sam deploy..."
sam deploy `
  --stack-name ai-chatbot `
  --region eu-west-2 `
  --s3-bucket nick-ai-chatbot-artifacts `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
      ConnectionsTableName=WS_Chat_Connections `
      BedrockModelId=anthropic.claude-3-haiku-20240307-v1:0 `
      ServiceNowBaseUrl=https://your-instance.service-now.com `
      GenesysBaseUrl=https://api.mypurecloud.com
