---
name: python-package-quality-checklist
description: Use whenever you develop or fix a Python package to ensure compliance with type hints, test isolation, regression tests, and changelog rules.
---
- Inspect all public functions in the package; verify every parameter and return value has explicit type annotations.
- Confirm that existing test files under tests/ are not modified; add new test files or new test functions only.
- Create or update tests/test_regressions.py with at least one test function per fixed bug; ensure this file passes all tests.
- Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix, specifying the function name and a short description.
- Run the full test suite to verify no regressions and that all new tests pass.
- Only claim completion after all above checks pass and no original test files are altered.
