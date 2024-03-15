# spotfishing
Finding FISH spots

## Development

### Testing
From the Nix shell, run `nox --list` to see a list of available commands, notably to run tests against different versions of Python, to reformat code to be style-compliant, and to run the linter.

NB: To pass arguments through `nox` to `pytest`, separate the argument strings with `--`, e.g.:
```shell
nox -s tests-3.11 -- -vv
```
to run the tests with additional verbosity (e.g., `pytest -vv`)

