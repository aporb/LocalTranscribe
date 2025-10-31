"""
Model management for spaCy and other NLP dependencies.

Handles automatic detection, downloading, and initialization of required
models for context-aware proofreading features.
"""

import sys
import subprocess
import warnings
from typing import Optional, Tuple
from pathlib import Path

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None


class ModelManager:
    """
    Manages NLP model lifecycle: detection, downloading, and loading.

    Provides automatic model management with user-friendly prompts and
    graceful degradation when models are unavailable.
    """

    DEFAULT_MODEL = "en_core_web_sm"
    AVAILABLE_MODELS = {
        "en_core_web_sm": {
            "size": "13 MB",
            "description": "Small model - Good for most use cases",
            "accuracy": "Standard"
        },
        "en_core_web_md": {
            "size": "43 MB",
            "description": "Medium model - Better accuracy",
            "accuracy": "Enhanced"
        },
        "en_core_web_lg": {
            "size": "741 MB",
            "description": "Large model - Best accuracy",
            "accuracy": "Maximum"
        }
    }

    def __init__(self, model_name: str = DEFAULT_MODEL, auto_download: bool = False):
        """
        Initialize model manager.

        Args:
            model_name: Name of spaCy model to use
            auto_download: If True, automatically download missing models
        """
        self.model_name = model_name
        self.auto_download = auto_download
        self._nlp = None
        self._initialized = False

    def is_model_installed(self, model_name: Optional[str] = None) -> bool:
        """
        Check if a spaCy model is installed.

        Args:
            model_name: Model to check (uses default if None)

        Returns:
            True if model is installed
        """
        if not SPACY_AVAILABLE:
            return False

        model = model_name or self.model_name

        try:
            spacy.load(model)
            return True
        except OSError:
            return False

    def get_installed_models(self) -> list:
        """
        Get list of installed spaCy models.

        Returns:
            List of installed model names
        """
        if not SPACY_AVAILABLE:
            return []

        try:
            # Get spaCy info which lists installed models
            result = subprocess.run(
                [sys.executable, "-m", "spacy", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse installed models from output
                # This is a simplified parser - spacy info output may vary
                installed = []
                for line in result.stdout.split('\n'):
                    if 'en_core_web' in line:
                        for model in self.AVAILABLE_MODELS.keys():
                            if model in line:
                                installed.append(model)
                return list(set(installed))
        except Exception:
            pass

        return []

    def download_model(self, model_name: Optional[str] = None, quiet: bool = False) -> bool:
        """
        Download a spaCy model.

        Args:
            model_name: Model to download (uses default if None)
            quiet: Suppress output

        Returns:
            True if download succeeded
        """
        if not SPACY_AVAILABLE:
            if not quiet:
                print("❌ spaCy not installed. Install with: pip install spacy")
            return False

        model = model_name or self.model_name

        if not quiet:
            info = self.AVAILABLE_MODELS.get(model, {})
            size = info.get("size", "unknown size")
            print(f"📥 Downloading spaCy model '{model}' ({size})...")
            print("   This may take a minute...")

        try:
            subprocess.run(
                [sys.executable, "-m", "spacy", "download", model],
                check=True,
                capture_output=quiet,
                timeout=300  # 5 minute timeout
            )

            if not quiet:
                print(f"✅ Model '{model}' downloaded successfully!")
            return True

        except subprocess.CalledProcessError as e:
            if not quiet:
                print(f"❌ Failed to download model: {e}")
            return False
        except subprocess.TimeoutExpired:
            if not quiet:
                print("❌ Download timed out. Please check your internet connection.")
            return False
        except Exception as e:
            if not quiet:
                print(f"❌ Unexpected error: {e}")
            return False

    def prompt_download(self, model_name: Optional[str] = None) -> bool:
        """
        Prompt user to download a model interactively.

        Args:
            model_name: Model to download (uses default if None)

        Returns:
            True if user agreed and download succeeded
        """
        model = model_name or self.model_name
        info = self.AVAILABLE_MODELS.get(model, {})

        print("\n" + "="*70)
        print("🔍 Context-Aware Proofreading Feature")
        print("="*70)
        print(f"\nThe spaCy model '{model}' is required for:")
        print("  • Intelligent acronym disambiguation (IP, PR, AI, OR, PI)")
        print("  • Context-aware term expansion")
        print("  • Enhanced accuracy in domain-specific proofreading")
        print(f"\nModel details:")
        print(f"  • Size: {info.get('size', 'unknown')}")
        print(f"  • {info.get('description', 'English language model')}")
        print(f"  • Accuracy: {info.get('accuracy', 'Standard')}")
        print("\nWithout this model, basic proofreading will still work,")
        print("but context-aware features will be disabled.")
        print("="*70)

        try:
            response = input("\nWould you like to download it now? [Y/n]: ").strip().lower()

            if response in ['', 'y', 'yes']:
                return self.download_model(model)
            else:
                print("\n⚠️  Skipping download. Context-aware features will be disabled.")
                print("   You can download later with: python -m spacy download", model)
                return False

        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️  Download cancelled. Context-aware features will be disabled.")
            return False

    def load_model(self, force_download: bool = False) -> Optional['spacy.Language']:
        """
        Load spaCy model with automatic download if needed.

        Args:
            force_download: Force download even if model exists

        Returns:
            Loaded spaCy model or None if unavailable
        """
        if not SPACY_AVAILABLE:
            warnings.warn(
                "spaCy not installed. Context-aware features disabled. "
                "Install with: pip install spacy"
            )
            return None

        # Check if already loaded
        if self._nlp is not None and not force_download:
            return self._nlp

        # Check if model is installed
        if not self.is_model_installed() or force_download:
            if self.auto_download:
                # Auto-download without prompting
                success = self.download_model(quiet=False)
                if not success:
                    return None
            else:
                # Prompt user to download
                success = self.prompt_download()
                if not success:
                    return None

        # Try to load the model
        try:
            self._nlp = spacy.load(self.model_name)
            self._initialized = True
            return self._nlp

        except OSError as e:
            warnings.warn(
                f"Failed to load spaCy model '{self.model_name}': {e}\n"
                f"Try downloading manually: python -m spacy download {self.model_name}"
            )
            return None

    def get_model(self) -> Optional['spacy.Language']:
        """
        Get loaded model (loads if not already loaded).

        Returns:
            Loaded spaCy model or None
        """
        if self._nlp is None:
            return self.load_model()
        return self._nlp

    def is_ready(self) -> bool:
        """
        Check if model manager is ready with a loaded model.

        Returns:
            True if model is loaded and ready
        """
        return self._initialized and self._nlp is not None


def ensure_spacy_model(
    model_name: str = ModelManager.DEFAULT_MODEL,
    auto_download: bool = False,
    quiet: bool = False
) -> Tuple[Optional['spacy.Language'], bool]:
    """
    Ensure spaCy model is available, downloading if necessary.

    Convenience function for one-time model loading.

    Args:
        model_name: Name of spaCy model
        auto_download: Automatically download if missing
        quiet: Suppress output

    Returns:
        Tuple of (loaded_model, context_aware_enabled)
    """
    if not SPACY_AVAILABLE:
        if not quiet:
            print("⚠️  spaCy not installed. Context-aware features disabled.")
        return None, False

    manager = ModelManager(model_name=model_name, auto_download=auto_download)

    # Try to load model
    nlp = manager.load_model()

    if nlp is None:
        if not quiet:
            print("ℹ️  Running in basic mode (context-aware features disabled)")
        return None, False

    if not quiet:
        print(f"✅ Loaded spaCy model '{model_name}' successfully!")

    return nlp, True


def check_dependencies() -> dict:
    """
    Check status of all NLP dependencies.

    Returns:
        Dictionary with dependency status information
    """
    status = {
        "spacy_installed": SPACY_AVAILABLE,
        "installed_models": [],
        "context_aware_ready": False
    }

    if SPACY_AVAILABLE:
        manager = ModelManager()
        status["installed_models"] = manager.get_installed_models()
        status["context_aware_ready"] = len(status["installed_models"]) > 0

    try:
        from flashtext import KeywordProcessor
        status["flashtext_available"] = True
    except ImportError:
        status["flashtext_available"] = False

    try:
        from rapidfuzz import fuzz
        status["rapidfuzz_available"] = True
    except ImportError:
        status["rapidfuzz_available"] = False

    return status
