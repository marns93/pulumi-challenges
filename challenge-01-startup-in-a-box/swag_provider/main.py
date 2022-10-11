from dataclasses import dataclass
from typing import Any, Optional

import pulumi.dynamic
import requests
from dataclasses_json import dataclass_json
from pulumi import Input, ResourceOptions
from pulumi.dynamic import CreateResult

SUBMITTION_URL = (
    "https://hooks.airtable.com/workflows/v1/genericWebhook/apptZjyaJx5J2BVri/wflmg3riOP6fPjCII/wtr3RoDcz3mTizw3C"
)


@dataclass_json
@dataclass(frozen=True)
class SwagInputs:
    name: str
    email: str
    address: str
    size: str


class SwagProvider(pulumi.dynamic.ResourceProvider):
    name: str = None

    def __init__(self, name):
        super().__init__()
        self.name = name

    def create(self, props: Any) -> CreateResult:
        response = requests.post(
            url=SUBMITTION_URL,
            headers={"Content-Type": "application/json"},
            json=props,
        )

        response.raise_for_status()

        return CreateResult(id_=props["email"], outs=props)


class Swag(pulumi.dynamic.Resource):
    name: Input[str]

    def __init__(self, name: str, props: SwagInputs, opts: Optional[ResourceOptions] = None):
        super().__init__(
            SwagProvider(name),
            name=name,
            props=vars(props),
            opts=opts,
        )
