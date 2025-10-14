# Phase 3 Quick Reference Guide

**Target:** Production-ready LocalTranscribe with SDK and >80% test coverage
**Duration:** 4 weeks (28 days)
**Status:** Phase 2 Complete ✅ → Phase 3 Ready to Execute

---

## Week-by-Week Breakdown

### Week 1: Architecture Refactor (Days 1-7)
**Goal:** Modular, maintainable codebase

**Tasks:**
- **Day 1-2**: Split 655-line `cli.py` into modular commands
  - Create `localtranscribe/cli/commands/` directory
  - One file per command: `process.py`, `batch.py`, `doctor.py`, etc.
  - Update `pyproject.toml` entry point

- **Day 3-4**: Expose core API
  - Update `__init__.py` with public imports
  - Add `py.typed` marker file
  - Document all public functions

- **Day 5-7**: Code quality
  - Add type hints to all public APIs
  - Run mypy/ruff/black
  - Add comprehensive docstrings

**Deliverables:**
- ✅ Modular CLI (~100 lines per command)
- ✅ Clean public API surface
- ✅ Type-checked codebase

---

### Week 2: Testing Infrastructure (Days 8-14)
**Goal:** >60% test coverage with CI/CD

**Tasks:**
- **Day 8-10**: Create test suite
  - Set up `tests/` directory with unit/integration split
  - Create `conftest.py` with fixtures
  - Generate test audio samples
  - Write unit tests for core modules

- **Day 11-14**: Integration tests & CI/CD
  - Write integration tests for pipeline
  - Set up GitHub Actions workflows
  - Configure pytest with coverage
  - Add pre-commit hooks

**Deliverables:**
- ✅ Test infrastructure with fixtures
- ✅ >60% code coverage
- ✅ Automated CI/CD pipeline

---

### Week 3: Python SDK (Days 15-21)
**Goal:** Developer-friendly SDK

**Tasks:**
- **Day 15-17**: SDK implementation
  - Create `localtranscribe/api/` module
  - Implement `LocalTranscribe` client class
  - Define result types (`ProcessResult`, `BatchResult`)
  - Add SDK to main `__init__.py`

- **Day 18-21**: SDK testing & docs
  - Write SDK tests
  - Create API documentation
  - Build example Jupyter notebooks
  - Reach >75% total coverage

**Deliverables:**
- ✅ Functional Python SDK
- ✅ >75% code coverage
- ✅ Complete API documentation
- ✅ Example notebooks

---

### Week 4: PyPI & Documentation (Days 22-28)
**Goal:** Published package with docs

**Tasks:**
- **Day 22-24**: PyPI packaging
  - Create pre-release checklist script
  - Set up release workflow (GitHub Actions)
  - Test on TestPyPI
  - Publish to PyPI

- **Day 25-28**: Documentation overhaul
  - Simplify README to <100 lines
  - Create contributor guide
  - Write getting started guide
  - Create example notebooks
  - Update CHANGELOG.md

**Deliverables:**
- ✅ Package on PyPI
- ✅ Complete documentation
- ✅ Contributor guide
- ✅ v2.0.0 release

---

## Critical Code Changes

### 1. Modular CLI Structure

**Before:**
```
localtranscribe/
└── cli.py  (655 lines)
```

**After:**
```
localtranscribe/
└── cli/
    ├── __init__.py
    ├── main.py
    └── commands/
        ├── process.py
        ├── batch.py
        ├── doctor.py
        ├── config.py
        ├── label.py
        └── version.py
```

### 2. Public API Exposure

**File: `localtranscribe/__init__.py`**
```python
from .core.diarization import run_diarization, DiarizationResult
from .core.transcription import run_transcription, TranscriptionResult
from .core.combination import combine_results, CombinationResult
from .pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from .api.client import LocalTranscribe
from .api.types import ProcessResult, BatchResult

__all__ = [
    "run_diarization",
    "run_transcription",
    "combine_results",
    "PipelineOrchestrator",
    "LocalTranscribe",
    "ProcessResult",
    "BatchResult",
    # ... all results
]
```

### 3. Python SDK

**File: `localtranscribe/api/client.py`**
```python
class LocalTranscribe:
    def __init__(
        self,
        model_size: str = "base",
        num_speakers: Optional[int] = None,
        **kwargs
    ):
        """Initialize LocalTranscribe client."""
        pass

    def process(
        self,
        audio_file: Union[str, Path],
        **kwargs
    ) -> ProcessResult:
        """Process single audio file."""
        pass

    def process_batch(
        self,
        input_dir: Union[str, Path],
        max_workers: int = 2,
        **kwargs
    ) -> BatchResult:
        """Process multiple files."""
        pass
```

**Usage:**
```python
from localtranscribe import LocalTranscribe

lt = LocalTranscribe(model_size="base", num_speakers=2)
result = lt.process("meeting.mp3")
print(result.transcript)
```

### 4. Test Structure

```
tests/
├── conftest.py                # Shared fixtures
├── fixtures/
│   ├── audio/                 # Test audio files
│   └── expected/              # Expected outputs
├── unit/                      # Fast, isolated tests
│   ├── test_diarization.py
│   ├── test_transcription.py
│   ├── test_config.py
│   └── test_path_resolver.py
├── integration/               # Slower, e2e tests
│   ├── test_pipeline.py
│   ├── test_cli.py
│   └── test_batch.py
└── test_sdk.py               # SDK tests
```

### 5. CI/CD Pipeline

**File: `.github/workflows/test.yml`**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=localtranscribe
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Key Commands

### Development Setup
```bash
# Clone and setup
git clone <repo>
cd transcribe-diarization
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Generate test fixtures
python tests/generate_fixtures.py

# Run tests
pytest                          # All tests
pytest tests/unit/              # Unit only
pytest --cov=localtranscribe    # With coverage
```

### Code Quality
```bash
# Format
black localtranscribe/

# Lint
ruff check localtranscribe/ --fix

# Type check
mypy localtranscribe/

# Security scan
bandit -r localtranscribe/ -ll
```

### Release Process
```bash
# 1. Update version in __init__.py
__version__ = "2.0.0"

# 2. Run pre-release checks
python scripts/pre_release_check.py

# 3. Build package
python -m build

# 4. Test on TestPyPI
twine upload --repository testpypi dist/*

# 5. Upload to PyPI
twine upload dist/*

# 6. Create git tag
git tag v2.0.0
git push origin v2.0.0
```

---

## Risk Mitigation

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| Breaking changes | Backward compat shims | Keep old cli.py with warnings |
| Coverage <80% | Focus on high-value paths | Ship at 70%, improve later |
| PyPI issues | Test on TestPyPI first | Yank and re-release |
| Docs incomplete | Prioritize SDK + README | Release with basics |
| CI/CD failures | Set up early (Week 2) | Manual testing checklist |

---

## Success Criteria

### Week 1 ✅
- [ ] CLI split into modular commands
- [ ] All commands still work
- [ ] Core API exposed in `__init__.py`
- [ ] Type hints on public APIs

### Week 2 ✅
- [ ] Test infrastructure set up
- [ ] >60% code coverage
- [ ] CI/CD pipeline running
- [ ] Unit tests passing

### Week 3 ✅
- [ ] SDK implemented and functional
- [ ] >75% code coverage
- [ ] API documentation complete
- [ ] Example notebooks created

### Week 4 ✅
- [ ] Package on PyPI
- [ ] `pip install localtranscribe` works
- [ ] Documentation complete
- [ ] v2.0.0 released

### 30-Day Post-Release 🎯
- [ ] >1,000 PyPI downloads/month
- [ ] +200 GitHub stars
- [ ] 5+ external contributors
- [ ] 3+ production use cases

---

## Daily Checklist Template

```markdown
## Day X - [Task Name]

### Morning
- [ ] Review previous day's work
- [ ] Set today's goals
- [ ] Create/update branch

### Work
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]

### Testing
- [ ] Run relevant tests
- [ ] Check coverage delta
- [ ] Manual verification

### End of Day
- [ ] Run full test suite
- [ ] Commit changes
- [ ] Update progress
- [ ] Plan tomorrow
```

---

## Resources

### Documentation
- Full plan: `docs/Phase3_Implementation_Plan.md`
- Phase 2 summary: `docs/PHASE2_COMPLETION_SUMMARY.md`
- Usability review: `docs/USABILITY_REVIEW.md`

### Tools
- Testing: pytest, pytest-cov
- Linting: ruff, black, mypy
- CI/CD: GitHub Actions
- Packaging: build, twine

### References
- [PEP 561](https://peps.python.org/pep-0561/) - Type hints
- [PEP 517](https://peps.python.org/pep-0517/) - Build system
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

## Quick Links

- **GitHub**: [Repository]
- **PyPI**: [Package page]
- **Docs**: [ReadTheDocs]
- **Issues**: [Bug tracker]
- **Discussions**: [Community]

---

**Ready to start? Begin with Week 1, Day 1: CLI Refactoring!**
