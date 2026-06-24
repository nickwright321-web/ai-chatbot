try {
    


Write-Host "Running sam validate..."
sam validate --template-file .\backend\template.yaml

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
sam build --template-file .\backend\template.yaml

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
  --template-file .\backend\template.yaml `
  --stack-name ai-chatbot-backend `
  --region eu-west-2 `
  --s3-bucket nick-ai-chatbot-artifacts `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
      ConnectionsTableName=WS_Chat_Connections `
      BedrockModelId=anthropic.claude-3-haiku-20240307-v1:0 `
      GenesysBaseUrl=https://api.mypurecloud.com `


Write-Host "Uploading Bob Prompt"

aws s3 cp Bedrock/bob-prompt.txt s3://bob-training-data-132696833143-eu-west-2/

}

finally {   
    Write-host "Cleaning up..."

    Remove-Item Env:AWS_ACCESS_KEY_ID
    Remove-Item Env:AWS_SECRET_ACCESS_KEY
    Remove-Item Env:AWS_SESSION_TOKEN

    Write-Host "Clean up complete"
}

