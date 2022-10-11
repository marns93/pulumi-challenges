import mimetypes
from pathlib import Path
from typing import Optional

from pulumi import ComponentResource, FileAsset, Output, ResourceOptions
from pulumi_aws import cloudfront, s3


class CdnWebsite(ComponentResource):
    bucket: s3.Bucket = None
    bucket_acl: s3.BucketAclV2 = None
    cloudfront_distribution: cloudfront.Distribution = None
    s3_origin_id: str = "custom-s3-origin"

    def __init__(self, name: str, static_website_directory: Path, opts: Optional[ResourceOptions] = None):
        super().__init__("custom:challenge:CdnWebsite", name=name, opts=opts, props={})
        opts = ResourceOptions.merge(opts, ResourceOptions(parent=self))

        self.bucket = s3.Bucket(
            resource_name=name,
            tags={"Name": name},
            opts=opts,
        )

        self.bucket_acl = s3.BucketAclV2(
            resource_name=name,
            bucket=self.bucket.id,
            acl="public-read",
            opts=opts,
        )

        self.cloudfront_distribution = cloudfront.Distribution(
            resource_name=name,
            enabled=True,
            is_ipv6_enabled=True,
            wait_for_deployment=True,
            default_root_object="index.html",
            origins=[
                cloudfront.DistributionOriginArgs(
                    domain_name=self.bucket.bucket_regional_domain_name, origin_id=self.s3_origin_id
                ),
            ],
            default_cache_behavior=cloudfront.DistributionDefaultCacheBehaviorArgs(
                allowed_methods=[
                    "DELETE",
                    "GET",
                    "HEAD",
                    "OPTIONS",
                    "PATCH",
                    "POST",
                    "PUT",
                ],
                cached_methods=["GET", "HEAD"],
                target_origin_id=self.s3_origin_id,
                forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                    query_string=False,
                    cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                        forward="none",
                    ),
                ),
                viewer_protocol_policy="allow-all",
                min_ttl=0,
                default_ttl=3600,
                max_ttl=86400,
            ),
            price_class="PriceClass_200",
            restrictions=cloudfront.DistributionRestrictionsArgs(
                geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                    restriction_type="whitelist",
                    locations=["US", "CA", "GB", "DE"],
                ),
            ),
            viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
                cloudfront_default_certificate=True,
            ),
            opts=opts,
        )

        for file in static_website_directory.glob("*"):
            s3.BucketObject(
                resource_name=f"{name}-{file}",
                bucket=self.bucket.id,
                key=file.name,
                source=FileAsset(file),
                content_type=mimetypes.guess_type(file)[0],
                acl="public-read",
                opts=opts,
            )

        self.register_outputs({"bucket_name": self.bucket, "cdn_url": self.cloudfront_distribution.domain_name})

    @property
    def url(self) -> Output[str]:
        return self.cloudfront_distribution.domain_name
