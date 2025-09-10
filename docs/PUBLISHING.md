# PUBLISHING

## Local
```bash
python -m pip install --upgrade build twine
python -m build
twine upload --repository testpypi dist/*
# later:
twine upload dist/*
```

## GitHub Actions (add repo secrets)
- TEST_PYPI_API_TOKEN
- PYPI_API_TOKEN
Workflows:
- `.github/workflows/publish-testpypi.yml` (on push to main)
- `.github/workflows/publish-pypi.yml` (on tag `v*`)