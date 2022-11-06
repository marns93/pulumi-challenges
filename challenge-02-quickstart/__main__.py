import json

import pulumi
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway

role = aws.iam.Role(
    resource_name="role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                },
            ],
        },
    ),
    managed_policy_arns=[aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE],
)

lambda_function = aws.lambda_.Function(
    resource_name="fn",
    runtime="python3.9",
    handler="handler.handler",
    role=role.arn,
    code=pulumi.FileArchive("./function"),
)

api = apigateway.RestAPI(
    resource_name="api",
    routes=[
        apigateway.RouteArgs(path="/", local_path="www"),
        apigateway.RouteArgs(path="/date", method=apigateway.Method.GET, event_handler=lambda_function),
    ],
)

pulumi.export("url", api.url)
