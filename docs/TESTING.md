# Testing

## Running

```sh
pytest tests/test_typosquat_detector.py
```

## Policy

The repository contains one pytest module. Tests import the public API from `typosquat_detector` and the CLI `main` from `typosquat_detector.__main__`. They assert returned `Finding` objects, raised `TyposquatError` codes, normalisation results, distance values, and CLI output and exit codes. They use `tmp_path` for the popular-file CLI cases and do not use the network.

## Tiers

There is a single test module in `tests/test_typosquat_detector.py`; the repository does not contain separate local/CI conformance tiers or conformance setup scripts.

## Layout

`tests/test_typosquat_detector.py` covers:

- `test_check_distance_transposition`, `test_check_npm_distance`: one-edit and transposition distance findings for PyPI and npm.
- `test_check_same_name_returns_empty`: a candidate equal to a popular name after normalisation is skipped.
- `test_check_separator_rule_reported_once`: separator finding reported once even when distance also matches.
- `test_check_homoglyph_django_and_boto3`: ASCII homoglyph rule for `djang0` and `b0to3`.
- `test_check_affix_rule`: affix rule for `requests-python`.
- `test_check_short_name_excluded_from_distance`: names shorter than 4 characters are excluded from the distance rule.
- `test_custom_popular_list_and_scoped_npm`: `popular=` override and a scoped npm name.
- `test_check_multiple_targets`, `test_popular_constant_no_close_pairs`: multiple targets can be reported; no two bundled names are within distance 1.
- `test_invalid_ecosystem_raises`, `test_normalize_invalid_ecosystem`: unsupported ecosystem raises code `invalid_ecosystem`.
- `test_osa_distance_known_values`: known OSA distance values.
- `test_input_too_large`, `test_invalid_name_regex`, `test_invalid_name_trailing_newline_pypi`, `test_invalid_name_trailing_newline_npm`: length, regex and trailing-newline validation.
- `test_normalize_pypi`, `test_normalize_npm`: PEP 503 normalisation and npm lowercasing.
- `test_main_findings`, `test_main_no_findings`, `test_main_npm_ecosystem`, `test_main_no_arguments_returns_2`, `test_main_invalid_name_returns_2`, `test_main_with_popular_file`, `test_main_popular_file_missing_returns_2`: CLI output, exit codes and `--popular` handling.

There is no `tests/conftest.py` in the repository.
