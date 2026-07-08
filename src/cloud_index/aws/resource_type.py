from cloud_index.resource import ResourceType

TYPE_MAP: dict[tuple[str, str], tuple[str, str]] = {
    ("apigateway", "restapis"): ("apigateway", "rest-api"),
    ("apigateway", "restapis/deployments"): ("apigateway", "deployment"),
    ("apigateway", "restapis/resources"): ("apigateway", "resource"),
    ("apigateway", "restapis/resources/methods"): ("apigateway", "method"),
    ("apigateway", "restapis/stages"): ("apigateway", "stage"),
    ("apprunner", "autoscalingconfiguration"): ("apprunner", "auto-scaling-configuration"),
    ("athena", "datacatalog"): ("athena", "data-catalog"),
    ("athena", "namedquery"): ("athena", "named-query"),
    ("autoscaling", "autoScalingGroup"): ("autoscaling", "auto-scaling-group"),
    ("ce", "anomalymonitor"): ("ce", "anomaly-monitor"),
    ("ce", "anomalysubscription"): ("ce", "anomaly-subscription"),
    ("cognito-identity", "identitypool"): ("cognito", "identity-pool"),
    ("cognito-idp", "userpool"): ("cognito", "user-pool"),
    ("ec2", "natgateway"): ("ec2", "nat-gateway"),
    ("elasticache", "cluster"): ("elasticache", "cache-cluster"),
    ("elasticache", "parametergroup"): ("elasticache", "parameter-group"),
    ("elasticache", "replicationgroup"): ("elasticache", "replication-group"),
    ("elasticache", "subnetgroup"): ("elasticache", "subnet-group"),
    ("elasticloadbalancing", "listener-rule/app"): ("elasticloadbalancingv2", "listener-rule"),
    ("elasticloadbalancing", "listener/app"): ("elasticloadbalancingv2", "listener"),
    ("elasticloadbalancing", "listener/net"): ("elasticloadbalancingv2", "listener"),
    ("elasticloadbalancing", "loadbalancer"): ("elasticloadbalancing", "load-balancer"),
    ("elasticloadbalancing", "loadbalancer/app"): ("elasticloadbalancingv2", "load-balancer"),
    ("elasticloadbalancing", "loadbalancer/gwy"): ("elasticloadbalancingv2", "load-balancer"),
    ("elasticloadbalancing", "loadbalancer/net"): ("elasticloadbalancingv2", "load-balancer"),
    ("elasticloadbalancing", "targetgroup"): ("elasticloadbalancingv2", "target-group"),
    ("firehose", "deliverystream"): ("firehose", "delivery-stream"),
    ("iam", "policy"): ("iam", "managed-policy"),
    ("memorydb", "parametergroup"): ("memorydb", "parameter-group"),
    ("rds", "cluster"): ("rds", "db-cluster"),
    ("rds", "cluster-pg"): ("rds", "db-cluster-parameter-group"),
    ("rds", "db"): ("rds", "db-instance"),
    ("rds", "og"): ("rds", "option-group"),
    ("rds", "pg"): ("rds", "db-parameter-group"),
    ("rds", "ri"): ("rds", "reserved-db-instance"),
    ("rds", "secgrp"): ("rds", "db-security-group"),
    ("rds", "subgrp"): ("rds", "db-subnet-group"),
    ("route53", "hostedzone"): ("route53", "hosted-zone"),
    ("wafv2", "ipset"): ("wafv2", "ip-set"),
    ("wafv2", "webacl"): ("wafv2", "web-acl"),
}

SERVICE_MAP: dict[str, str] = {
    "acm": "certificatemanager",
    "es": "opensearchservice",
}


def parse_resource_type(resource_type: str) -> ResourceType:
    """
    Parses a raw AWS Resource Explorer type such as `rds:pg` into a canonical ResourceType,
    e.g. `aws:rds:db-parameter-group`.
    """
    service, kind = resource_type.split(":", 1)
    if canonical := TYPE_MAP.get((service, kind)):
        service, kind = canonical
    else:
        service = SERVICE_MAP.get(service, service)
    return ResourceType("aws", service, kind)
