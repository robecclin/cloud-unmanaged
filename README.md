# Cloud Unmanaged

Tool to identify cloud resources not managed by infrastructure as code (IaC).

## Setup

### Resource Explorer

Resources in AWS are discovered using AWS Resource Explorer.

[Enable cross-region search](https://docs.aws.amazon.com/resource-explorer/latest/userguide/getting-started-setting-up.html#getting-started-setting-up-quick), which creates a default view that returns all resources across all regions.

### Credentials

Configure AWS credentials using one of the [methods supported by Boto3](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html).

The supplied user or role should have the [`AWSResourceExplorerReadOnlyAccess` managed policy](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSResourceExplorerReadOnlyAccess.html) attached, or equivalent access.

## Usage

### Index resources

List all resources discoverable using the current credentials:

```sh
$ uv run cloud-unmanaged index
```

## Development

```sh
make install # uv sync --locked
make check   # ruff, vulture, ty, pyright, mypy, pytest+coverage, yamllint
make upgrade # uv sync --upgrade
make clean   # remove caches
```
