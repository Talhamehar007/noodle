# Change Log

## [Unreleased](https://github.com/wilfredinni/noodle/tree/develop)

### Added

- Added `TooManyArguments` warning.
- Added `AnswerTypeError` warning.
- Add colorized output: `noodle.output`, `noodle.output.info`, `noodle.output.warning`, `noodle.output.danger`, `noodle.output.success`.
- Add validated questions: `noodle.ask.any`, `noodle.ask.integer`, and `noodle.ask.float`.
- Add support for default option values.

### Fixed

- All options printing in the Command help when no user arguments are defined.
- Wrong Command formatting.

### Changed

- `self.option()` can now evaluate multiple options (`self.options(opt1, opt2)`).

## [0.0.2](https://github.com/wilfredinni/noodle/releases/tag/0.0.2) - 2019-05-15

Initial release.