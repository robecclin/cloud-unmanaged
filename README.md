# Cloud Unmanaged

Tool to identify cloud resources not managed by infrastructure as code (IaC).

## Setup

### Resource Explorer

Resources in AWS are discovered using AWS Resource Explorer.

[Enable cross-region search](https://docs.aws.amazon.com/resource-explorer/latest/userguide/getting-started-setting-up.html#getting-started-setting-up-quick), which creates a default view that returns all resources across all regions.

### Credentials

Configure AWS credentials using one of the [methods supported by Boto3](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html).

The supplied user or role should have the [`AWSResourceExplorerReadOnlyAccess` managed policy](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSResourceExplorerReadOnlyAccess.html) attached, or equivalent access. It also requires the [`kms:DescribeKey`](https://docs.aws.amazon.com/kms/latest/developerguide/kms-api-permissions-reference.html) permission on all keys.

## Usage

### Index resources

List all resources discoverable using the current credentials:

```sh
uv run cloud-unmanaged index
```
