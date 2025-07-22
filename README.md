# CDK Example for Lambda, Scheduling, & Optional Table Access

This is a hobby project meant for use in a single AWS environment, for things like scheduling Lambda jobs with optional DynamoDB access.

## Prerequisites 

* AWS Account
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) & [completed setup](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
* AWS CDK - `npm install -g aws-cdk`

## Setup: Python Virtual Environment (MacOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Reminder: if you run into issues with your venv setup, just run `rm -rf .venv`

### On Windows:

```bat
.venv\Scripts\activate.bat
```

---

## Deployment Steps

At this point you can now synthesize the CloudFormation template for this code. Docker must be running for these steps to work, sanity check with `docker ps`

### Bootstrap your environment (run once per account/region):

```bash
cdk bootstrap
```

### Synthesize and deploy the stack:

```bash
cdk synth
cdk deploy
```

Your main CDK stack lives in `lambdas/lambdas_stack.py`.
If you're setting up a DynamoDB table (optional), this file includes an example configuration for that as well.

> ⚠️ You're responsible for your own AWS charges. This is a hobby setup — keep track of what resources are live, especially if you enable periodic/scheduled jobs or create a DynamoDB table.

To add additional dependencies, for example other CDK libraries, just add them to your `setup.py` file and rerun the `pip install -r requirements.txt` command.

Update the lambda in `lambdas/sample-lambda/app.py` and its `lambdas/sample-lambda/requirements.txt` file to actually make changes to your lambda. At present, the lambda calls an API an returns part of its response. Feel free to use only one lambda per folder, or duplicate the sample lambda and its setup to add additonal lambdas. To not overcomplicate things, copy over the sample lambda to a new folder when you'd like to add more lambdas, and update the `lambda-cdk/lambdas_deployment_stack.py`.

```
cp -r lambdas/sample-lambda lambdas/second-lambda
```

### Clean up:

```bash
cdk destroy
```
> ⚠️ If you created a table in the stack, the table and its data will be destroyed with this action. To preserve data, consider managing the table outside of the CDK stack, or export/import data before destroying. Alternatively, add in a removal policy when creating your table (`RETAIN` or `SNAPSHOT`).
---

## Useful CDK Commands

* `cdk ls` - list stacks in your app
* `cdk synth` - emit synthesized CloudFormation template
* `cdk deploy` - deploy the current stack
* `cdk diff` - compare deployed stack with local changes
* `cdk docs` - open CDK documentation

---
## Local Lambda Testing via Docker

Build and run your Lambda container locally. This is mostly useful for testing.
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
## GitHub Actions Setup
This template uses [OpenID Connect (OIDC)](https://docs.github.com/en/actions/concepts/security/openid-connect) to grant Github depoyment access. If you'd like to just deploy locally with `cdk deploy`, delete `.github/workflows/deploy.yml`.
1. After cloning, add your AWS Account ID to Settings > Secrets and variables > Actions > Repository secrets, named `AWS_ACCOUNT_ID`
2. Go to the AWS Console > IAM, and set up an identity provider. Follow the Github instructions for [Adding the identity provider to AWS](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services#adding-the-identity-provider-to-aws). Select OpenID Connect for the provider type, `https://token.actions.githubusercontent.com/` for the provider URL, and `sts.amazonaws.com` for the audience.
3. Still under IAM, navigate to Roles and create a new role. Follow the AWS instructions for [Creating a role for OIDC](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html#idp_oidc_Create). When creating a new role, select 'Web identity' for the trusted entity type,  `https://token.actions.githubusercontent.com/` for the identity provider from the dropdown, and `sts.amazonaws.com` for the audience from the dropdown. Use your Github username for the organization (or the organization where you clone your repository). For personal development, add the AdministratorAccess policy. Your policy should look something like this:
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
At this point, you should be able to push to main and deploy to AWS through Github Actions.