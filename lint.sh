#!/bin/bash
isort -rc .
autoflake -r --in-place --remove-unused-variables .
black -l 120 .
flake8 --max-line-length 120 . --exclude .venv
mypy --disable-error-code import-not-found .
rm -rf .mypy_cache
find . -type d -name "__pycache__" -exec rm -rf {} +
