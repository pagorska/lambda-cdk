from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    RemovalPolicy,
    Tags,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
import os

TAGS = {
    "Project": "SampleLambdaDeployment",
    "Environment": "Dev",
}

def create_lambda(scope, name, code_path, memory=128, timeout=120, env_vars=None):
    environment = {}
    if env_vars:
        environment = {k: os.getenv(k, '') for k in env_vars}
    
    lambda_fn = _lambda.Function(
        scope, f'{name}Function',
        code=_lambda.Code.from_asset_image(code_path),
        handler=_lambda.Handler.FROM_IMAGE,
        runtime=_lambda.Runtime.FROM_IMAGE,
        memory_size=memory,
        timeout=Duration.seconds(timeout),
        environment=environment
    )
    
    return lambda_fn

def create_table(scope, name, partition_key="id", removal_policy=RemovalPolicy.RETAIN):
    return dynamodb.Table(
        scope, name,
        partition_key=dynamodb.Attribute(
            name=partition_key,
            type=dynamodb.AttributeType.STRING
        ),
        billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        removal_policy=removal_policy
    )

# Helper functions for common schedules
def hourly(hours=1):
    return events.Schedule.rate(Duration.hours(hours))

def minutely(minutes=30):
    return events.Schedule.rate(Duration.minutes(minutes))

def daily_at(hour, minute=0):
    return events.Schedule.cron(hour=str(hour), minute=str(minute))

def weekdays_at(hour, minute=0):
    return events.Schedule.cron(hour=str(hour), minute=str(minute), week_day="MON-FRI")

def add_schedule(scope, name, lambda_fn, schedule=None, description=""):
    # Supports rate or cron schedules
    if schedule is None:
        schedule = events.Schedule.rate(Duration.hours(1))  # default to hourly
    
    rule = events.Rule(
        scope, name,
        schedule=schedule,
        description=description
    )
    rule.add_target(targets.LambdaFunction(lambda_fn))
    return rule

class LambdaDeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Apply global tags
        for key, value in TAGS.items():
            Tags.of(self).add(key, value)

        # Lambda function using container image
        # Duplicate this block for additional lambdas, update the name and path accordingly
        hello_lambda = create_lambda(self, 'HelloWorld', code_path='lambdas/sample-lambda')

        add_schedule(self, "HourlyRule", hello_lambda, hourly(1), "Trigger Lambda every hour")

        '''
        table = create_table(self, 'SampleTable', partition_key='id')
        table.grant_read_write_data(hello_lambda)
        
        # Optional Using Existing DynamoDB Table, replace with your table ARN
        
        table = dynamodb.Table.from_table_arn(
            self, "ImportedTable",
            "arn:aws:dynamodb:{region}:{account-id}:table/{table-name}"
        )
        '''

        CfnOutput(self, 'LambdaFunctionName', 
                 value=hello_lambda.function_name,
                 description='Lambda function name for manual testing')
