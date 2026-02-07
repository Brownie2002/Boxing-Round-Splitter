# Todo List

This file tracks the tasks and priorities for the Boxing Round Splitter project.

## High Priority

- [ ] Add more test cases for bell detection

## Medium Priority

- [ ] Add integration tests for the bell detection function
- [ ] Update the README with more detailed usage examples
- [ ] Read metadata from multiple MP4 files to identify order or names

## Low Priority

- [ ] Improve error handling in the bell detection function

## Completed

- [x] Extract bell detection logic into a separate function - Commit: [feat: reorganize code into src/ directory](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/9a64b64)
- [x] Add debug file for bell detection timestamps - Commit: [feat: reorganize code into src/ directory](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/9a64b64)
- [x] Create unit tests for bell detection - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Document function documentation rules in DEVSTRAL.md - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Improve bell detection at specific timestamps (e.g., 7:04) - Done by lowering MAX_PEAK to 0.3 - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Optimize performance parameters for bell detection - Performance is sufficient for now - Commit: [docs: add function documentation rules and improve bell detection test](https://github.com/Brownie2002/Boxing-Round-Splitter/commit/33f617d)
- [x] Refactor code to better identify rounds in logs
- [x] Fix discrepancy between Creating round {i+1} and actual round number {round}
- [x] Reduce ffmpeg verbosity in terminal logs
- [x] Review and update existing ADRs
- [x] Add more comments to the code for clarity
- [x] Document the new bell detection improvements in an ADR
