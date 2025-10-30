# GitHub Integration and Version Management

Guide for setting up and managing LocalTranscribe's GitHub integration, version display, and release automation.

---

## Current Setup

**Repository:** https://github.com/aporb/LocalTranscribe
**Package:** https://pypi.org/project/localtranscribe/
**Version:** 3.1.0 (synchronized across all sources)
**Package Version:** 3.1.0 (as of `localtranscribe/__init__.py`)

**Note:** Version is now synchronized across pyproject.toml, __init__.py, and documentation.

---

## Version Management

### Version Sources

1. **Primary Source:** `pyproject.toml` (used for PyPI packaging)
2. **Runtime Source:** `localtranscribe/__init__.py` (used by Python import)
3. **Documentation:** `README.md` and `docs/CHANGELOG.md`

### Version Synchronization

All version sources must be kept in sync:

```bash
# Before releasing, ensure all versions match
# 1. Update pyproject.toml
# 2. Update localtranscribe/__init__.py
# 3. Update CHANGELOG.md
# 4. Commit changes
# 5. Create git tag
```

---

## GitHub Workflows

### Release Workflow (`.github/workflows/release.yml`)

**Trigger:** Git tags matching pattern `v*`

**Actions:**
1. Build Python package
2. Extract release notes from CHANGELOG.md
3. Create GitHub Release
4. Publish to PyPI

**Usage:**
```bash
# Create and push a new release
git tag -a v2.0.2 -m "Release version 2.0.2"
git push origin v2.0.2
```

### Version Display Workflow (`.github/workflows/version-display.yml`)

**Trigger:** Push to `main` branch or pull requests

**Actions:**
1. Install package
2. Extract version information
3. Display version in GitHub Actions logs

---

## GitHub Release Process

### Prerequisites

1. **Version Synchronization:** Ensure all version sources match
2. **CHANGELOG Update:** Document changes for the new version
3. **Git Commit:** All changes committed and pushed to `main`

### Release Steps

```bash
# 1. Synchronize versions
# Update pyproject.toml to version = "2.0.2"
# Update localtranscribe/__init__.py to __version__ = "2.0.2"

# 2. Update CHANGELOG.md
# Add new version section with changes

# 3. Commit changes
git add .
git commit -m "Release v2.0.2"

# 4. Create and push tag
git tag -a v2.0.2 -m "Release version 2.0.2"
git push origin main
git push origin v2.0.2

# 5. GitHub Actions will automatically:
# - Build the package
# - Create GitHub Release
# - Publish to PyPI
```

---

## Version Display on GitHub

### Badges in README.md

The README already includes a PyPI version badge:
```markdown
[![PyPI version](https://img.shields.io/pypi/v/localtranscribe?color=blue)](https://pypi.org/project/localtranscribe/)
```

This badge automatically updates when new versions are published to PyPI.

### GitHub Releases

Each tagged release creates a GitHub Release with:
- Release notes extracted from CHANGELOG.md
- Attached distribution files
- Automatic version tracking

### Package Information

GitHub displays package information through:
1. **Repository description** (set in GitHub settings)
2. **README badges** (automatically updated)
3. **GitHub Releases** (manual and automated)
4. **Package version workflows** (CI/CD verification)

---

## Version Status

**Current Version: 3.1.0**
- `pyproject.toml`: 3.1.0
- `localtranscribe/__init__.py`: 3.1.0
- `docs/CHANGELOG.md`: 3.1.0 entry added

**✅ All versions are synchronized!**

## Configuring PyPI Authentication

To enable automatic PyPI publishing, you need to configure a PyPI API token as a GitHub secret:

### 1. Create PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Give it a descriptive name (e.g., "GitHub Actions Release")
4. Set scope to "Project: localtranscribe" (or "All projects" if you prefer)
5. Click "Add token"
6. **Copy the token immediately** (it won't be shown again)

### 2. Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/aporb/LocalTranscribe
2. Click "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Name: `PYPI_API_TOKEN`
6. Value: Paste your PyPI API token
7. Click "Add secret"

### 3. Verify Configuration

After adding the secret, the next release workflow should automatically publish to PyPI.

**Note:** The release workflow is now configured with PyPI authentication. Creating a v3.0.0 tag will automatically publish to PyPI.

---

## Best Practices

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Pre-release suffixes:**
- `-alpha`: Early development
- `-beta`: Feature complete, testing
- `-rc1`: Release candidate

### Release Notes

Structure CHANGELOG.md entries with:
```markdown
## [2.0.2] - 2025-10-14

### ✨ Added
- New features

### 🐛 Fixed
- Bug fixes

### 🔧 Changed
- Improvements
```

### Git Tagging

Always use annotated tags:
```bash
git tag -a v2.0.2 -m "Release version 2.0.2"
```

---

## Monitoring and Verification

### Check Current Status

```bash
# View current version
python -c "import localtranscribe; print(localtranscribe.__version__)"

# List existing tags
git tag -l

# View recent commits
git log --oneline -5
```

### Verify GitHub Integration

1. **Workflows:** Check Actions tab for workflow runs
2. **Releases:** Check Releases tab for published versions
3. **Badges:** Verify README badges display correctly
4. **PyPI:** Confirm package is published and accessible

---

## Troubleshooting

### Version Mismatch

**Symptom:** Different versions in different files
**Solution:** Update all version sources to match

### Release Workflow Fails

**Symptom:** GitHub Actions workflow fails
**Check:**
- Version numbers are synchronized
- CHANGELOG.md has entry for version
- Git tag format is correct (`v*`)
- PyPI API token is configured in secrets

### PyPI Publish Fails

**Symptom:** Cannot publish to PyPI
**Check:**
- Version already exists on PyPI (cannot overwrite)
- PyPI API token is valid and has correct permissions
- Package builds successfully locally

---

## Future Improvements

### Automated Version Synchronization

Consider adding a pre-commit hook or CI check to ensure version synchronization.

### Enhanced Release Notes

Automatically generate release notes from commit messages and pull requests.

### Version Matrix

Display compatibility matrix for different Python versions and platforms.

---

## Resources

- **GitHub Actions:** https://docs.github.com/en/actions
- **GitHub Releases:** https://docs.github.com/en/repositories/releasing-projects-on-github
- **PyPI:** https://pypi.org/
- **Semantic Versioning:** https://semver.org/
