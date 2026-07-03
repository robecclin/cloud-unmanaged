# AGENTS.md

## Project overview

- Tool to identify cloud resources not managed by infrastructure as code (IaC)
- Current features:
  - Discover resources in an AWS account and display them to the user
- Future scope (for context only):
  - Discover resources defined by CloudFormation and Terraform
  - Store discovered resources in a local database
  - Identify resources that are not represented in IaC

## Module layout

- `cloud_index` - Package for indexing cloud resources
- `cloud_index.aws` - AWS resource indexer using AWS Resource Explorer
- `cloud_index.error` - Base error class (`CloudIndexError`) for all errors exposed to callers
- `cloud_index.resource` - Data class for representing resources (`Resource` and `ResourceType`)
- `cloud_unmanaged` - Package for CLI app
- `cloud_unmanaged.app` - Typer app object
- `cloud_unmanaged.main` - Entrypoint and command registration
- `cloud_unmanaged.command` - Command implementations
- `cloud_unmanaged.command.index` - Command to discover and display resources
- `tests.cloud_index` - Library tests
- `tests.cloud_unmanaged` - CLI app tests

## Testing

- Complete branch test coverage is enforced
- Tests mirror the package module structure under `tests/`
- Required test types:
  - Library tests covering exported interfaces
  - Command tests with mocked library interfaces
  - Unit tests of discrete logic
- Avoid redundant assertions across layers; test behavior at the lowest appropriate layer
- Mock only when necessary to isolate external systems or architectural boundaries; otherwise use real objects
- Tests must not require live credentials or network access

## Development commands

- Run these commands on completion:
  - `make format` - Automatically format and fix Python files using ruff
  - `make check` - Verify changes by running linting, static analysis and test suite

## Conventions

- Target Python 3.14 and dependency versions resolved by `uv.lock`; backwards compatibility is not required
- Use strict type annotations; assertions are appropriate for internal invariants and type narrowing
- Do not use assertions for user input, expected AWS failures or other recoverable runtime conditions
- Do not prefix private modules, functions or variables with `_`, except in nested closures
