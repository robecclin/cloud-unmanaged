import pytest

from cloud_index.aws.arn import parse_arn


@pytest.mark.parametrize(
    "arn,expected",
    [
        (
            "arn:aws:s3:::my-bucket",
            ("aws", "s3", None, None, None, "my-bucket"),
        ),
        (
            "arn:aws:iam::123456789012:role/my-role",
            ("aws", "iam", None, "123456789012", "role", "my-role"),
        ),
        (
            "arn:aws:sns:us-east-1:123456789012:my-topic",
            ("aws", "sns", "us-east-1", "123456789012", None, "my-topic"),
        ),
        (
            "arn:aws:elasticache:us-east-1:123456789012:user:default",
            ("aws", "elasticache", "us-east-1", "123456789012", "user", "default"),
        ),
        (
            "arn:aws:lambda:us-east-1:123456789012:function:MyFunction:1",
            ("aws", "lambda", "us-east-1", "123456789012", "function", "MyFunction:1"),
        ),
        (
            "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable",
            ("aws", "dynamodb", "us-east-1", "123456789012", "table", "MyTable"),
        ),
        (
            "arn:aws:resource-explorer-2:us-east-1:123456789012:view/us-east-1/367b491a-1e6d-41b1-9065-1de5d7f63d65",
            (
                "aws",
                "resource-explorer-2",
                "us-east-1",
                "123456789012",
                "view",
                "us-east-1/367b491a-1e6d-41b1-9065-1de5d7f63d65",
            ),
        ),
        (
            "arn:aws:ssm:us-east-1:123456789012:parameter/parent/child",
            ("aws", "ssm", "us-east-1", "123456789012", "parameter", "parent/child"),
        ),
        (
            "arn:aws:ssm:us-east-1:123456789012:parameter/parent/child:1",
            ("aws", "ssm", "us-east-1", "123456789012", "parameter", "parent/child:1"),
        ),
        (
            "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/my-function:*",
            ("aws", "logs", "us-east-1", "123456789012", "log-group", "/aws/lambda/my-function:*"),
        ),
    ],
)
def test_parse_arn(arn: str, expected: tuple[str, str, str | None, str | None, str | None, str]) -> None:
    parsed = parse_arn(arn)
    assert parsed.partition == expected[0]
    assert parsed.service == expected[1]
    assert parsed.region == expected[2]
    assert parsed.account_id == expected[3]
    assert parsed.resource_type == expected[4]
    assert parsed.resource_id == expected[5]


@pytest.mark.parametrize(
    "arn",
    [
        "not-an-arn",
        "invalid:::::",
        "arn::::",
        "",
    ],
)
def test_parse_arn_invalid(arn: str) -> None:
    with pytest.raises(ValueError):
        parse_arn(arn)
