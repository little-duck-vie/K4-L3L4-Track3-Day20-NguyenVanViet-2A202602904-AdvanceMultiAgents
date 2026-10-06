---
name: code-quality-checklist
description: Use whenever you are implementing or modifying code to ensure adherence to coding standards and documentation requirements.
---
1. Ensure all public functions have type annotations for parameters and return values.
2. Do not modify existing test files; create new test files for any new tests.
3. Write regression tests for every bug fixed, ensuring at least three tests are included in a dedicated regression test file.
4. Update the CHANGELOG.md with a bullet point for each fix under '## Unreleased', following the format: '- fix(<function name>): <short description>'.
5. Validate that all functions adhere to their docstring specifications and expected behavior.
6. Run the test suite and confirm all tests pass before finalizing changes.
