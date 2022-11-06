import requests
from pulumi_policy import (
    EnforcementLevel,
    PolicyConfigSchema,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)


def pulumi_swag_not_submitted(args: ResourceValidationArgs, report_violation: ReportViolation):
    if not args.resource_type == "pulumi:pulumi:Stack":
        return
    swag = args.get_config()
    response = requests.post(
        url="https://docs.google.com/forms/d/e/1FAIpQLSfBr2f6rhXYbMXi8Caftu-zWtNPRDoWUEukrTJKuwO3OyYRvg/formResponse",
        headers={
            "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSfBr2f6rhXYbMXi8Caftu-zWtNPRDoWUEukrTJKuwO3OyYRvg/viewform",
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36",
        },
        data={
            "usp": "pp_url",
            "entry.1720843992": swag["name"],
            "entry.511943887": swag["email"],
            "entry.1289952319": swag["address"],
            "entry.1240089905": swag["size"],
        },
    )
    print(response)
    response.raise_for_status()


submit_swag = ResourceValidationPolicy(
    name="pulumi-challenge-swag",
    description="stuff",
    validate=pulumi_swag_not_submitted,
    config_schema=PolicyConfigSchema(
        properties={
            "name": {
                "type": "string",
                "minLength": 2,
            },
            "email": {
                "type": "string",
                "minLength": 6,
                "format": "email",
            },
            "address": {
                "type": "string",
                "minLength": 2,
            },
            "size": {
                "type": "string",
                "minLength": 1,
                "enum": [
                    "XS",
                    "S",
                    "M",
                    "L",
                    "XL",
                ],
            },
        },
        required=[
            "name",
            "email",
            "address",
            "size",
        ],
    ),
)

PolicyPack(
    name="aws-python",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        submit_swag,
    ],
)
