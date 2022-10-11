from pathlib import Path

from cdn.main import CdnWebsite
from pulumi import export
from pulumi_checkly import Check
from swag_provider.main import Swag, SwagInputs

IDENTIFIER = "challenge-01"

website = CdnWebsite(name=IDENTIFIER, static_website_directory=Path("./website"))
export(name="website_url", value=website.url)

Check(
    resource_name=IDENTIFIER,
    activated=True,
    frequency=10,
    type="BROWSER",
    locations=["eu-central-1"],
    script=website.url.apply(lambda url: Path("checkly-embed.js").read_text().replace("{{websiteUrl}}", url)),
)

Swag(
    name=IDENTIFIER,
    props=SwagInputs(
        name="YourName",
        email="YourEmail",
        address="YourAddress",
        size="YourSize",
    ),
)
