from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class LambdaDeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        '''
        # Optional DynamoDB table creation
        table = dynamodb.Table(
            self, "MyTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            #removal_policy=RemovalPolicy.RETAIN # Uncomment to retain table on stack deletion
        )
        '''
        
        # Optional Using Existing DynamoDB Table, replace with your table ARN
        '''
        table = dynamodb.Table.from_table_arn(
            self, "ImportedTable",
            "arn:aws:dynamodb:{region}:{account-id}:table/{table-name}"
        )
        '''

        # Lambda function using container image
        # Duplicate this block for additional lambdas, update the name and path accordingly
        hello_lambda = _lambda.Function(
            self, 'HelloWorldFunction',
            code=_lambda.Code.from_asset_image('lambdas/sample-lambda'),
            handler=_lambda.Handler.FROM_IMAGE,
            runtime=_lambda.Runtime.FROM_IMAGE,
            memory_size=128,  # minimum for container images
            timeout=Duration.seconds(120) # update as needed
        )

        # table.grant_read_write_data(hello_lambda)

        hourly_rule = events.Rule(
            self, 'HourlyRule',
            schedule=events.Schedule.rate(Duration.hours(1)), # Update as needed, sample options below
            description='Trigger Lambda every hour'
        )

        # # Every 30 minutes
        # schedule=events.Schedule.rate(Duration.minutes(30))
        # # Every day at 2 PM UTC
        # schedule=events.Schedule.cron(hour="14", minute="0")
        # # Every weekday at 9 AM UTC
        # schedule=events.Schedule.cron(hour="9", minute="0", week_day="MON-FRI")
        # # Every 5 minutes
        # schedule=events.Schedule.rate(Duration.minutes(5))

        hourly_rule.add_target(targets.LambdaFunction(hello_lambda))

        CfnOutput(self, 'LambdaFunctionName', 
                 value=hello_lambda.function_name,
                 description='Lambda function name for manual testing')
