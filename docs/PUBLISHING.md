# Publishing the softapi Library

## One-time
1) Create accounts on **TestPyPI** and **PyPI**.
2) Create API tokens on both (Account settings → API tokens).
3) In GitHub repo → Settings → Secrets and variables → Actions:
   - Add `TEST_PYPI_API_TOKEN`
   - Add `PYPI_API_TOKEN`

## Version bump
Edit `version` in `pyproject.toml` (SemVer). Commit.

## Publish to TestPyPI (on push to main)
- Push to `main`. Workflow `.github/workflows/publish-testpypi.yml` builds and uploads.

Install to verify:
```bash
pip install -i https://test.pypi.org/simple/ softapi
softapi --help
```

## Publish to PyPI (on tag push)
```bash
git tag v0.1.0
git push origin v0.1.0
```
The `.github/workflows/publish-pypi.yml` workflow builds and uploads.

## Local manual publish (optional)
```bash
python -m pip install --upgrade build twine
python -m build
twine upload --repository testpypi dist/*
# later
twine upload dist/*
```