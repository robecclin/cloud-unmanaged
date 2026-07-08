import pytest

from cloud_index.aws.resource_type import parse_resource_type
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("dynamodb:table", ResourceType("aws", "dynamodb", "table")),
        ("resource-explorer-2:index", ResourceType("aws", "resource-explorer-2", "index")),
        ("s3:bucket", ResourceType("aws", "s3", "bucket")),
    ],
)
def test_parse_resource_type(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("apigateway:restapis", ResourceType("aws", "apigateway", "rest-api")),
        ("apigateway:restapis/deployments", ResourceType("aws", "apigateway", "deployment")),
        ("apigateway:restapis/resources", ResourceType("aws", "apigateway", "resource")),
        ("apigateway:restapis/resources/methods", ResourceType("aws", "apigateway", "method")),
        ("apigateway:restapis/stages", ResourceType("aws", "apigateway", "stage")),
        ("apprunner:autoscalingconfiguration", ResourceType("aws", "apprunner", "auto-scaling-configuration")),
        ("athena:datacatalog", ResourceType("aws", "athena", "data-catalog")),
        ("athena:namedquery", ResourceType("aws", "athena", "named-query")),
        ("autoscaling:autoScalingGroup", ResourceType("aws", "autoscaling", "auto-scaling-group")),
        ("ce:anomalymonitor", ResourceType("aws", "ce", "anomaly-monitor")),
        ("ce:anomalysubscription", ResourceType("aws", "ce", "anomaly-subscription")),
        ("cognito-identity:identitypool", ResourceType("aws", "cognito", "identity-pool")),
        ("cognito-idp:userpool", ResourceType("aws", "cognito", "user-pool")),
        ("ec2:natgateway", ResourceType("aws", "ec2", "nat-gateway")),
        ("elasticache:cluster", ResourceType("aws", "elasticache", "cache-cluster")),
        ("elasticache:parametergroup", ResourceType("aws", "elasticache", "parameter-group")),
        ("elasticache:replicationgroup", ResourceType("aws", "elasticache", "replication-group")),
        ("elasticache:subnetgroup", ResourceType("aws", "elasticache", "subnet-group")),
        ("elasticloadbalancing:listener-rule/app", ResourceType("aws", "elasticloadbalancingv2", "listener-rule")),
        ("elasticloadbalancing:listener/app", ResourceType("aws", "elasticloadbalancingv2", "listener")),
        ("elasticloadbalancing:listener/net", ResourceType("aws", "elasticloadbalancingv2", "listener")),
        ("elasticloadbalancing:loadbalancer", ResourceType("aws", "elasticloadbalancing", "load-balancer")),
        ("elasticloadbalancing:loadbalancer/app", ResourceType("aws", "elasticloadbalancingv2", "load-balancer")),
        ("elasticloadbalancing:loadbalancer/gwy", ResourceType("aws", "elasticloadbalancingv2", "load-balancer")),
        ("elasticloadbalancing:loadbalancer/net", ResourceType("aws", "elasticloadbalancingv2", "load-balancer")),
        ("elasticloadbalancing:targetgroup", ResourceType("aws", "elasticloadbalancingv2", "target-group")),
        ("firehose:deliverystream", ResourceType("aws", "firehose", "delivery-stream")),
        ("iam:policy", ResourceType("aws", "iam", "managed-policy")),
        ("memorydb:parametergroup", ResourceType("aws", "memorydb", "parameter-group")),
        ("rds:cluster", ResourceType("aws", "rds", "db-cluster")),
        ("rds:cluster-pg", ResourceType("aws", "rds", "db-cluster-parameter-group")),
        ("rds:db", ResourceType("aws", "rds", "db-instance")),
        ("rds:og", ResourceType("aws", "rds", "option-group")),
        ("rds:pg", ResourceType("aws", "rds", "db-parameter-group")),
        ("rds:ri", ResourceType("aws", "rds", "reserved-db-instance")),
        ("rds:secgrp", ResourceType("aws", "rds", "db-security-group")),
        ("rds:subgrp", ResourceType("aws", "rds", "db-subnet-group")),
        ("route53:hostedzone", ResourceType("aws", "route53", "hosted-zone")),
        ("wafv2:ipset", ResourceType("aws", "wafv2", "ip-set")),
        ("wafv2:webacl", ResourceType("aws", "wafv2", "web-acl")),
    ],
)
def test_parse_resource_type_canonical_type(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("acm:certificate", ResourceType("aws", "certificatemanager", "certificate")),
        ("es:domain", ResourceType("aws", "opensearchservice", "domain")),
    ],
)
def test_parse_resource_type_renamed_service(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected
