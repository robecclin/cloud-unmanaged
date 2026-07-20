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
- `cloud_index.aws` - Physical resource indexer using AWS Resource Explorer
- `cloud_index.cloudformation` - Logical resource indexer using AWS CloudFormation
- `cloud_index.error` - Base error class (`CloudIndexError`) for all errors exposed to callers
- `cloud_index.progress` - Progress event and reporter interfaces
- `cloud_index.resource` - Data classes for representing resources (`Resource`, `PhysicalResource`, `LogicalResource`, `ResourceType`)
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
- Test types used where applicable:
  - Library tests covering exported interfaces
  - Command tests with mocked library interfaces
  - Unit tests of discrete logic
- Test behavior at the highest stable boundary that exposes the contract; test lower-level state only when callers depend on it through a supported interface, not merely because it cannot be observed at a higher layer
- Do not add tests solely for declarative configuration or branchless implementation changes already exercised by higher-level tests
- Prefer realistic, supported states and failure modes; test synthetic or abnormal conditions only when handling them is an explicit requirement
- Avoid redundant coverage across layers
- Name tests for the scenario being exercised, not the expected result; name the primary expected path `test_<subject>`
- Mock only when necessary to isolate external systems or architectural boundaries; otherwise use real objects
- Do not use pytest's `monkeypatch` fixture
- Tests must not require live credentials or network access

## Development commands

- Run these commands on completion:
  - `make format` - Automatically format and fix Python files using ruff
  - `make check` - Verify changes by running linting, static analysis and test suite

## Conventions

- Target Python 3.14 and dependency versions resolved by `uv.lock`; backwards compatibility is not required
- Use strict type annotations; assertions are appropriate for internal invariants and type narrowing
- Do not use assertions for user input, expected AWS failures or other recoverable runtime conditions
- Do not prefix private modules, private functions or private variables with `_`; it is allowed as a discard identifier
- Keep commit messages concise, lowercase, at most 72 characters and without a period; include the reason only when space permits
