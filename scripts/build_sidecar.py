#!/usr/bin/env python3
"""
Build LocalTranscribe Python sidecar for Tauri GUI.

This script bundles the LocalTranscribe CLI into a standalone executable
using PyInstaller for distribution with the Tauri desktop application.
"""

import os
import sys
import platform
import shutil
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    print("ERROR: PyInstaller not installed. Install with: pip install pyinstaller")
    sys.exit(1)


def get_binary_name():
    """Get platform-specific binary name."""
    system = platform.system().lower()
    if system == "windows":
        return "localtranscribe.exe"
    elif system == "darwin":
        return "localtranscribe-macos"
    else:
        return "localtranscribe-linux"


def clean_previous_builds():
    """Remove previous build artifacts."""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)


def ensure_output_directory():
    """Ensure the Tauri binaries directory exists."""
    output_dir = Path("localtranscribe-gui/src-tauri/binaries")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_sidecar():
    """Build the Python sidecar executable."""
    print("=" * 60)
    print("Building LocalTranscribe Python Sidecar")
    print("=" * 60)

    binary_name = get_binary_name()
    output_dir = ensure_output_directory()

    print(f"\nPlatform: {platform.system()}")
    print(f"Binary name: {binary_name}")
    print(f"Output directory: {output_dir}")

    # Clean previous builds
    clean_previous_builds()

    print("\nBuilding with PyInstaller...")
    print("-" * 60)

    # PyInstaller arguments
    pyinstaller_args = [
        'localtranscribe/cli/main.py',
        '--name', binary_name,
        '--onefile',
        '--console',
        '--noconfirm',

        # Collect all LocalTranscribe modules
        '--collect-all', 'localtranscribe',

        # Collect ML dependencies
        '--collect-all', 'torch',
        '--collect-all', 'torchaudio',
        '--collect-all', 'pyannote',
        '--collect-all', 'pyannote.audio',
        '--collect-all', 'pyannote.core',
        '--collect-all', 'pyannote.pipeline',

        # Collect NLP dependencies
        '--collect-all', 'spacy',
        '--collect-all', 'flashtext',
        '--collect-all', 'rapidfuzz',

        # Collect audio processing
        '--collect-all', 'librosa',
        '--collect-all', 'soundfile',
        '--collect-all', 'pydub',
        '--collect-all', 'audioread',

        # Hidden imports for scikit-learn (pyannote dependency)
        '--hidden-import', 'sklearn.utils._cython_blas',
        '--hidden-import', 'sklearn.neighbors.typedefs',
        '--hidden-import', 'sklearn.neighbors.quad_tree',
        '--hidden-import', 'sklearn.tree._utils',
        '--hidden-import', 'sklearn.neighbors._partition_nodes',

        # Hidden imports for torch
        '--hidden-import', 'torch',
        '--hidden-import', 'torch.nn',
        '--hidden-import', 'torch.nn.functional',

        # Output directory
        '--distpath', str(output_dir),
    ]

    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n" + "=" * 60)
        print("✅ Build successful!")
        print(f"Binary location: {output_dir / binary_name}")
        print("=" * 60)

        # Verify the binary exists
        binary_path = output_dir / binary_name
        if binary_path.exists():
            size_mb = binary_path.stat().st_size / (1024 * 1024)
            print(f"\nBinary size: {size_mb:.2f} MB")
            return True
        else:
            print("\n❌ ERROR: Binary not found after build")
            return False

    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return False


if __name__ == "__main__":
    print("\nLocalTranscribe Sidecar Builder")
    print("================================\n")

    # Check we're in the right directory
    if not os.path.exists("localtranscribe"):
        print("ERROR: Must run from LocalTranscribe root directory")
        sys.exit(1)

    if not os.path.exists("pyproject.toml"):
        print("ERROR: pyproject.toml not found. Are you in the correct directory?")
        sys.exit(1)

    success = build_sidecar()
    sys.exit(0 if success else 1)
