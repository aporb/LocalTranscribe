# PyPI Release Process

Guide for publishing LocalTranscribe to PyPI (Python Package Index).

---

## Prerequisites

### One-Time Setup

1. **Create PyPI account**
   - Visit https://pypi.org/account/register/
   - Verify your email

2. **Create TestPyPI account** (for testing)
   - Visit https://test.pypi.org/account/register/
   - Verify your email

3. **Install build tools**
   ```bash
   pip install build twine
   ```

4. **Create API tokens**

   **PyPI:**
   - Go to https://pypi.org/manage/account/token/
   - Create token with "Entire account" scope
   - Save token securely (you'll only see it once)

   **TestPyPI:**
   - Go to https://test.pypi.org/manage/account/token/
   - Create token with "Entire account" scope
   - Save token securely

5. **Configure credentials**

   Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-YOUR-TOKEN-HERE

   [testpypi]
   username = __token__
   password = pypi-YOUR-TESTPYPI-TOKEN-HERE
   ```

   Secure the file:
   ```bash
   chmod 600 ~/.pypirc
   ```

---

## Pre-Release Checklist

Before every release:

- [ ] All tests pass (when implemented in Phase 4+)
- [ ] Version number updated in:
  - [ ] `pyproject.toml`
  - [ ] `localtranscribe/__init__.py`
- [ ] `CHANGELOG.md` updated with release notes
- [ ] `README.md` reviewed and updated
- [ ] Git tag created for version
- [ ] All changes committed and pushed

---

## Release Process

### Step 1: Prepare Release

```bash
# 1. Update version number
vim localtranscribe/__init__.py  # Change __version__
vim pyproject.toml                # Change version

# 2. Update CHANGELOG
vim CHANGELOG.md  # Add release notes

# 3. Commit changes
git add .
git commit -m "Release v3.1.0"
git push origin main
```

### Step 2: Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python3 -m build

# This creates:
# - dist/localtranscribe-3.1.0-py3-none-any.whl (wheel)
# - dist/localtranscribe-3.1.0.tar.gz (source)
```

### Step 3: Test on TestPyPI

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation in clean environment
python3 -m venv test_env
source test_env/bin/activate
pip install --index-url https://test.pypi.org/simple/ localtranscribe

# Test that it works
localtranscribe --help
localtranscribe version

# Clean up
deactivate
rm -rf test_env
```

### Step 4: Release to PyPI

```bash
# Upload to PyPI (CANNOT BE UNDONE!)
python3 -m twine upload dist/*

# Verify on PyPI
open https://pypi.org/project/localtranscribe/
```

### Step 5: Create Git Tag

```bash
# Tag the release
git tag -a v3.1.0 -m "Release version 3.1.0"
git push origin v3.1.0

# Or create release on GitHub
gh release create v3.1.0 --title "v3.1.0" --notes "See CHANGELOG.md"
```

---

## Post-Release

After publishing:

1. **Verify installation works:**
   ```bash
   pip install localtranscribe
   localtranscribe --help
   ```

2. **Update documentation:**
   - Update README if needed
   - Announce on project channels

3. **Monitor for issues:**
   - Check GitHub issues
   - Monitor PyPI download stats

---

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR** - Breaking changes (e.g., 2.0.0 → 3.0.0)
- **MINOR** - New features, backward compatible (e.g., 3.0.0 → 3.1.0)
- **PATCH** - Bug fixes, backward compatible (e.g., 3.1.0 → 3.1.1)

**Pre-release tags:**
- `3.2.0-alpha` - Early testing
- `3.2.0-beta` - Feature complete, testing
- `3.2.0-rc1` - Release candidate

---

## Troubleshooting

### Build Fails

**Error:** `No module named 'build'`
```bash
pip install --upgrade build
```

### Upload Fails

**Error:** `Invalid or non-existent authentication`
```bash
# Check ~/.pypirc exists and has correct tokens
cat ~/.pypirc

# Make sure file permissions are correct
chmod 600 ~/.pypirc
```

**Error:** `File already exists`
```bash
# Version already published (cannot overwrite)
# Bump version number and rebuild
```

### Installation Fails

**Missing dependencies:**
```bash
# Some dependencies might not be on TestPyPI
# Use both TestPyPI and PyPI:
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            localtranscribe
```

---

## Quick Reference

**Build package:**
```bash
python3 -m build
```

**Test on TestPyPI:**
```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ localtranscribe
```

**Release to PyPI:**
```bash
twine upload dist/*
```

**Create git tag:**
```bash
git tag -a v3.1.0 -m "Release 3.1.0"
git push origin v3.1.0
```

---

## Resources

- **PyPI:** https://pypi.org/
- **TestPyPI:** https://test.pypi.org/
- **Packaging Guide:** https://packaging.python.org/
- **Twine Docs:** https://twine.readthedocs.io/
- **Build Docs:** https://build.pypa.io/

---

## Notes

- **Cannot delete or overwrite** published versions on PyPI
- Always test on TestPyPI first
- Keep credentials secure (never commit `.pypirc`)
- Document all changes in CHANGELOG.md
- Tag all releases in git
- Monitor download stats and issues after release

---

**Last Updated:** 2025-10-30 (v3.1.0)
