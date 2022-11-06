import json

import pulumi
import pulumi_aws as aws

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

lambda_function_url = aws.lambda_.FunctionUrl(
    resource_name="url",
    function_name=lambda_function.name,
    authorization_type="NONE",
)

pulumi.export("url", lambda_function_url.function_url)
