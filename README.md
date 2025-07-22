# AWS Lambda CDK Template

This repository provides a sample Dockerized Python Lambda function with EventBridge scheduling (set on a one hour basis), GitHub Actions for automated deployment on push to main, and instructions for setting up OIDC authentication for GitHub Actions with optional DynamoDB setup. This is a hobby project meant for use in a single AWS environment.

## What's Included

- **Dockerized Python Lambda Function**: Containerized Lambda function with sample API call
- **EventBridge Scheduling**: Automated Lambda execution every hour
- **AWS CDK Infrastructure**: Infrastructure as Code using AWS CDK
- **GitHub Actions CI/CD**: Automated deployment pipeline - start your commit with 'deploy:'
- **OIDC Authentication**: Secure GitHub-to-AWS authentication setup
- **Optional DynamoDB**: Database configuration examples

## Prerequisites 

* AWS Account
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) & [completed setup](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
* AWS CDK - `npm install -g aws-cdk`
* Docker
* Python 3.7+

## Quick Start

### 1. Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
```

> **Note**: If you run into venv issues, just run `rm -rf .venv` and start over.

### 2. Deploy to AWS

Ensure Docker is running (`docker ps` to verify), then:

```bash
cdk bootstrap
```

> **Note**: `cdk bootstrap` is only needed once per AWS account/region.

```bash
cdk synth
cdk deploy
```
At this point, you'll be able to verify and observe the creation of the resources in the AWS Console. 

Your main CDK stack configuration is in `lambda_cdk/lambda_deployment_stack.py`.

If you're setting up a DynamoDB table (optional), this file includes an example configuration for that as well.

> ⚠️ You're responsible for your own AWS charges. This is a hobby setup — keep track of what resources are live, especially if you enable periodic/scheduled jobs or create a DynamoDB table.

### 3. Customize Your Lambda

Update the Lambda function in `lambdas/sample-lambda/app.py` and its dependencies in `lambdas/sample-lambda/requirements.txt`. The current implementation calls an external API and returns part of its response.

To add additional dependencies, for example other CDK libraries, just add them to your `setup.py` file and rerun the `pip install -r requirements.txt` command.

Update the lambda in `lambdas/sample-lambda/app.py` and its `lambdas/sample-lambda/requirements.txt` file to actually make changes to your lambda. At present, the lambda calls an API an returns part of its response. 
### 4. Optional: Adding More Lambdas

Feel free to use only one lambda per folder, or duplicate the sample lambda and its setup to add additonal lambdas. To not overcomplicate things, copy over the sample lambda to a new folder:

```bash
cp -r lambdas/sample-lambda lambdas/second-lambda
```

Update `lambda_cdk/lambda_deployment_stack.py` to include the new lambda.

### 5. Optional: Clean Up

This repo creates a lambda that runs on a regular schedule, and optional instructions for adding a table. While lambdas are mostly cheap, tables can be more expensive, and you may want to shut down projects that are not in use. 

**Before destroying:**
- Check CloudWatch logs for any important data or debugging information
- Export any DynamoDB data you want to keep
- Note down any configuration settings you might want to recreate later

To destroy the stack:
```bash
cdk destroy
```
> ⚠️ If you created a table in the stack, the table and its data will be destroyed with this action. To preserve data, consider managing the table outside of the CDK stack, or export/import data before destroying. Alternatively, add in a removal policy when creating your table (`RETAIN` or `SNAPSHOT`).

**Post-cleanup verification:**
- Check the AWS Console to ensure resources were deleted
- Verify no unexpected charges on your AWS bill
- Consider cleaning up ECR repositories if no longer needed
---
## Project Structure

```
├── lambda_cdk/
│   ├── lambda_deployment_stack.py # Main CDK stack
│   └── __init__.py
├── lambdas/
│   └── sample-lambda/
│       ├── app.py                # Lambda function code
│       ├── requirements.txt      # Lambda dependencies
│       └── Dockerfile           # Container configuration
├── tests/
├── .github/workflows/deploy.yml  # GitHub Actions workflow (if exists)
├── app.py                       # CDK app entry point
├── cdk.json                     # CDK configuration
├── requirements.txt             # CDK dependencies
└── source.bat                   # Windows activation script
```
---
## Useful CDK Commands

* `cdk ls` - list stacks in your app
* `cdk synth` - emit synthesized CloudFormation template
* `cdk deploy` - deploy the current stack
* `cdk diff` - compare deployed stack with local changes
* `cdk docs` - open CDK documentation

---
## Local Lambda Testing via Docker

Builds and run your Lambda container locally. This is mostly useful for local testing.
Update the name (`hello-world-lambda`) and path (`sample-lambda/`) as needed.

```bash
docker build -t hello-world-lambda sample-lambda/
docker run -p 9000:8080 hello-world-lambda
```

In a second terminal, invoke the container with:

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

Or test with a scheduled event payload:

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"source": "aws.events", "detail-type": "Scheduled Event"}'
```
---
## GitHub Actions Setup (Optional)
This template uses [OpenID Connect (OIDC)](https://docs.github.com/en/actions/concepts/security/openid-connect) to grant Github depoyment access. If you prefer to deploy locally with `cdk deploy`, you can delete `.github/workflows/deploy.yml`.
### OIDC Configuration Steps
1. **Once Per Repo:** After cloning, add your AWS Account ID to Settings > Secrets and variables > Actions > Repository secrets, named `AWS_ACCOUNT_ID`. 
2. **Once Per AWS Account:** Go to the AWS Console > IAM, and set up an identity provider. Follow the Github instructions for [Adding the identity provider to AWS](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services#adding-the-identity-provider-to-aws). Select OpenID Connect for the provider type, `https://token.actions.githubusercontent.com/` for the provider URL, and `sts.amazonaws.com` for the audience.
3. **Once Per AWS Account:** Still under IAM, navigate to Roles and create a new role. Follow the AWS instructions for [Creating a role for OIDC](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html#idp_oidc_Create). When creating a new role, select 'Web identity' for the trusted entity type,  `https://token.actions.githubusercontent.com/` for the identity provider from the dropdown, and `sts.amazonaws.com` for the audience from the dropdown. Use your Github username for the organization (or the organization where you clone your repository). For personal development, add the AdministratorAccess policy. Name the policy `GitHubActionsRole`, which is what is used in the `deploy.yml`.Your policy should look something like this:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::{AWS-ACCOUNT-ID}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:pagorska/*"
                }
            }
        }
    ]
}
```
Once configured, pushes to the main branch **which begin with 'deploy:'** will automatically deploy to AWS. Consider the permissions to your repository with these or any Github actions on push to main.
