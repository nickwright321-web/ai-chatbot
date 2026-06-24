#!/bin/bash

ACCOUNT_ID=132696833143
REGION=eu-west-2
ROLE_NAME="sam-deployer-role"
POLICY_NAME="sam-deployer-policy"
USER_NAME="sam-deployer"

echo "Creating trust policy..."
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::$ACCOUNT_ID:user/$USER_NAME"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

echo "Creating deployment role..."
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://trust-policy.json

echo "Creating managed policy..."
cat > full-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": $(jq '.Statement' <<'POLICY'
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "APIGatewayPermissions",
            "Effect": "Allow",
            "Action": [
                "apigateway:TagResource",
                "apigateway:DELETE",
                "apigateway:PATCH",
                "apigateway:GET",
                "apigateway:PUT",
                "apigateway:POST"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMPermissions",
            "Effect": "Allow",
            "Action": [
                "iam:ListAttachedUserPolicies",
                "iam:PassRole"
            ],
            "Resource": "*"
        },
        {
            "Sid": "LambdaPermissions",
            "Effect": "Allow",
            "Action": [
                "lambda:GetEventSourceMapping",
                "lambda:GetPolicy",
                "lambda:CreateFunction",
                "Lambda:CreateEventSourceMapping",
                "lambda:DeleteFunction",
                "lambda:GetFunction",
                "lambda:UpdateFunctionConfiguration",
                "lambda:UpdateFunctionCode",
                "lambda:AddPermission",
                "lambda:TagResource",
                "lambda:RemovePermission"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudWatchLogsPermissions",
            "Effect": "Allow",
            "Action": [
                "logs:FilterLogEvents",
                "logs:DescribeLogStreams",
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
                "logs:DeleteLogGroup"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SecretsManagerPermissions",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:CreateSecret",
                "secretsmanager:DeleteSecret"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3Permissions",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketPublicAccessBlock",
                "s3:DeleteBucketPolicy",
                "s3:ListBucket",
                "s3:DeleteBucket",
                "s3:PutEncryptionConfiguration",
                "s3:DeleteObject",
                "s3:TagResource",
                "s3:PutObject",
                "s3:GetObject",
                "s3:CreateBucket",
                "s3:PutBucketPolicy",
                "s3:PutBucketWebsite"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudFormationPermissions",
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeStackEvents",
                "cloudformation:UpdateStack",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeStackResources",
                "cloudformation:DescribeStacks",
                "cloudformation:CreateStack",
                "cloudformation:GetTemplate",
                "cloudformation:DeleteStack"
            ],
            "Resource": "*"
        },
        {
            "Sid": "KMSPermissions",
            "Effect": "Allow",
            "Action": [
                "kms:ListAliases"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudfrontPermissions",
            "Effect": "Allow",
            "Action": [
                "cloudfront:GetDistributionConfig",
                "cloudfront:CreateDistribution",
                "cloudfront:UpdateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:DeleteDistribution",
                "cloudfront:CreateInvalidation",
                "cloudfront:GetInvalidation",
                "cloudfront:ListDistributions",
                "cloudfront:CreateOriginAccessControl"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SQSPermissions",
            "Effect": "Allow",
            "Action": [
                "sqs:createqueue",
                "sqs:getqueueattributes",
                "sqs:deletequeue",
                "sqs:setqueueattributes"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowKmsKeyManagement",
            "Effect": "Allow",
            "Action": [
                "kms:CreateKey",
                "kms:PutKeyPolicy",
                "kms:EnableKeyRotation",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DynamoDB",
            "Effect": "Allow",
            "Action": [
                "dynamodb:UpdateTimeToLive",
                "dynamodb:DescribeTimeToLive",
                "dynamodb:Query",
                "dynamodb:DeleteItem",
                "dynamodb:DeleteTable",
                "dynamodb:DescribeTable",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:UpdateTable",
                "dynamodb:CreateTable",
                "dynamodb:GetItem"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowPassRoleForApiGateway",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::132696833143:role/ApiGatewayCloudWatchRole"
        },
        {
            "Sid": "AllowKmsKeyDeletion",
            "Effect": "Allow",
            "Action": [
                "kms:ScheduleKeyDeletion",
                "kms:DisableKey",
                "kms:DescribeKey",
                "kms:PutKeyPolicy"
            ],
            "Resource": "arn:aws:kms:eu-west-2:132696833143:key/*"
        },
        {
            "Sid": "AllowDeleteLogGroup",
            "Effect": "Allow",
            "Action": [
                "logs:DeleteLogGroup"
            ],
            "Resource": "arn:aws:logs:eu-west-2:132696833143:log-group:/aws/apigateway/ai-chatbot-websocket:*"
        },
        {
            "Sid": "AllowPassApiGatewayCloudWatchRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::132696833143:role/ApiGatewayCloudWatchRole"
        },
        {
            "Sid": "AllowCFNToUseKmsKey",
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "arn:aws:kms:eu-west-2:132696833143:key/*"
        },
        {
            "Sid": "AllowCloudFormationUseKmsKey",
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ApiGatewayGeneral",
            "Effect": "Allow",
            "Action": [
                "apigateway:DELETE",
                "apigateway:PUT",
                "apigateway:POST",
                "apigateway:GET"
            ],
            "Resource": "arn:aws:apigateway:eu-west-2::/apis/*"
        },
        {
            "Sid": "ApiGatewayV2StagePatch",
            "Effect": "Allow",
            "Action": [
                "apigateway:PATCH"
            ],
            "Resource": [
                "arn:aws:apigateway:eu-west-2::/apis/*/stages",
                "arn:aws:apigateway:eu-west-2::/apis/*/stages/*"
            ]
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "cloudformation:DescribeStackEvents",
                "cloudformation:CreateStack",
                "cloudformation:GetTemplate",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStackResources",
                "cloudformation:UpdateStack",
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:GetTemplateSummary",
                "cloudformation:DescribeStacks"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "iam:PassedToService": "lambda.amazonaws.com"
                }
            }
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": [
                "cloudformation:ListStacks",
                "iam:DetachRolePolicy",
                "iam:CreateServiceLinkedRole",
                "iam:DeleteRolePolicy",
                "iam:TagRole",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:GetRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "cloudformation:ValidateTemplate"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor5",
            "Effect": "Allow",
            "Action": [
                "cloudformation:DescribeStackEvents",
                "cloudformation:CreateStack",
                "cloudformation:GetTemplate",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStackResources",
                "cloudformation:UpdateStack",
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeStacks"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor6",
            "Effect": "Allow",
            "Action": "cloudformation:ValidateTemplate",
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor7",
            "Effect": "Allow",
            "Action": [
                "cloudformation:DescribeStackEvents",
                "cloudformation:CreateStack",
                "cloudformation:GetTemplate",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStackResources",
                "cloudformation:UpdateStack",
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:ValidateTemplate",
                "cloudformation:DescribeStacks"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor8",
            "Effect": "Allow",
            "Action": "lambda:ListFunctions",
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor9",
            "Effect": "Allow",
            "Action": "logs:DescribeLogGroups",
            "Resource": "*"
        }
    ]
}
POLICY
)
}
EOF

aws iam create-policy \
  --policy-name $POLICY_NAME \
  --policy-document file://full-policy.json

echo "Attaching managed policy to role..."
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME

echo "Allowing user to assume the role..."
aws iam put-user-policy \
  --user-name $USER_NAME \
  --policy-name AssumeSamDeployerRole \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
      {
        \"Effect\": \"Allow\",
        \"Action\": \"sts:AssumeRole\",
        \"Resource\": \"arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME\"
      }
    ]
  }"

echo "Done."
