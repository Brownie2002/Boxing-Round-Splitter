# Todo List

This file tracks the tasks and priorities for the Boxing Round Splitter project.

## High Priority

- [ ] Add more test cases for bell detection
- [x] Add parameter handling for --debug and other CLI options
- [x] Create docs/design/bell_detection.md to explain design choices
- [x] Update README with --debug option usage

## Medium Priority

- [x] Document the new bell detection improvements in an ADR
- [ ] Add integration tests for the bell detection function
- [ ] Update the README with more detailed usage examples
- [ ] Read metadata from multiple MP4 files to identify order or names
- [x] Refactor code to better identify rounds in logs
- [x] Fix discrepancy between Creating round {i+1} and actual round number {round}

## Low Priority

- [x] Review and update existing ADRs
- [x] Add more comments to the code for clarity
- [ ] Improve error handling in the bell detection function
- [x] Reduce ffmpeg verbosity in terminal logs

## Completed

- [x] Extract bell detection logic into a separate function - Commit: [feat: reorganize code into src/ directory](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/9a64b64)
- [x] Add debug file for bell detection timestamps - Commit: [feat: reorganize code into src/ directory](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/9a64b64)
- [x] Create unit tests for bell detection - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Document function documentation rules in DEVSTRAL.md - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Improve bell detection at specific timestamps (e.g., 7:04) - Done by lowering MAX_PEAK to 0.3 - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Optimize performance parameters for bell detection - Performance is sufficient for now - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
