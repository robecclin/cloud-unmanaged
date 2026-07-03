from botocore.stub import Stubber
from types_boto3_kms.literals import KeyManagerTypeType
from types_boto3_kms.type_defs import DescribeKeyResponseTypeDef
from types_boto3_resource_explorer_2.literals import IndexTypeType
from types_boto3_resource_explorer_2.type_defs import (
    ListIndexesOutputTypeDef,
    ListResourcesOutputTypeDef,
    ResourceTypeDef,
    ResponseMetadataTypeDef,
)

RESPONSE_METADATA: ResponseMetadataTypeDef = {
    "RequestId": "",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {},
    "RetryAttempts": 0,
}

VIEW_ARN = "arn:aws:resource-explorer-2:us-east-1:123456789012:view/us-east-1/367b491a-1e6d-41b1-9065-1de5d7f63d65"


def aws_resource(arn: str, resource_type: str, region: str = "us-east-1") -> ResourceTypeDef:
    return {
        "Arn": arn,
        "OwningAccountId": "123456789012",
        "Region": region,
        "ResourceType": resource_type,
    }


def stub_list_indexes(stubber: Stubber, index_type: IndexTypeType) -> None:
    response: ListIndexesOutputTypeDef = {
        "Indexes": [
            {
                "Type": index_type,
                "Region": "us-east-1",
            }
        ],
        "ResponseMetadata": RESPONSE_METADATA,
    }
    stubber.add_response("list_indexes", response, {})


def stub_list_resources(stubber: Stubber, *resources: ResourceTypeDef) -> None:
    stub_list_indexes(stubber, "AGGREGATOR")
    response: ListResourcesOutputTypeDef = {
        "Resources": list(resources),
        "ResponseMetadata": RESPONSE_METADATA,
        "ViewArn": VIEW_ARN,
    }
    stubber.add_response("list_resources", response, {})


def stub_describe_key(stubber: Stubber, key_id: str, key_manager: KeyManagerTypeType) -> None:
    response: DescribeKeyResponseTypeDef = {
        "KeyMetadata": {
            "KeyId": key_id,
            "KeyManager": key_manager,
        },
        "ResponseMetadata": RESPONSE_METADATA,
    }
    stubber.add_response("describe_key", response, {"KeyId": key_id})
