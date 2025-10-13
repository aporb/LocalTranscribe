"""
Download utilities with progress tracking for LocalTranscribe.

Provides progress indicators for model downloads to prevent users from
thinking the application is frozen during first-run downloads.
"""

import os
from pathlib import Path
from typing import Optional, Callable
from contextlib import contextmanager

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn

console = Console()


def get_cache_dir() -> Path:
    """
    Get the cache directory for models.
    
    Returns:
        Path to cache directory
    """
    # Try to get HuggingFace cache directory
    hf_cache = os.environ.get("HF_HOME")
    if hf_cache:
        return Path(hf_cache)
    
    # Default HuggingFace cache location
    home = Path.home()
    return home / ".cache" / "huggingface"


def get_mlx_cache_dir() -> Path:
    """
    Get the cache directory for MLX models.
    
    Returns:
        Path to MLX cache directory
    """
    home = Path.home()
    return home / ".cache" / "mlx"


def check_model_cached(model_id: str, cache_dir: Optional[Path] = None) -> bool:
    """
    Check if a model is already cached locally.
    
    Args:
        model_id: HuggingFace model identifier (e.g., "pyannote/speaker-diarization-3.1")
        cache_dir: Optional cache directory (default: auto-detect)
        
    Returns:
        True if model is cached
    """
    if cache_dir is None:
        cache_dir = get_cache_dir()
    
    # HuggingFace stores models in hub/models--org--name format
    model_path = model_id.replace("/", "--")
    model_dir = cache_dir / "hub" / f"models--{model_path}"
    
    return model_dir.exists()


@contextmanager
def download_status(description: str, show_spinner: bool = True):
    """
    Context manager to show download status.
    
    Shows a spinner and message while downloading/loading models.
    
    Args:
        description: Description of what's being downloaded
        show_spinner: Whether to show spinner animation
        
    Example:
        with download_status("Downloading diarization model..."):
            pipeline = Pipeline.from_pretrained(model_name, use_auth_token=token)
    """
    if show_spinner:
        with console.status(f"[bold cyan]{description}[/bold cyan]") as status:
            yield status
    else:
        console.print(f"[cyan]{description}[/cyan]")
        yield None


def show_cache_info(cache_dir: Optional[Path] = None) -> dict:
    """
    Get information about cached models.
    
    Args:
        cache_dir: Optional cache directory (default: auto-detect)
        
    Returns:
        Dictionary with cache statistics
    """
    if cache_dir is None:
        cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        return {
            "exists": False,
            "location": str(cache_dir),
            "size_mb": 0,
            "model_count": 0,
        }
    
    # Calculate total size
    total_size = 0
    model_count = 0
    
    hub_dir = cache_dir / "hub"
    if hub_dir.exists():
        for item in hub_dir.iterdir():
            if item.is_dir() and item.name.startswith("models--"):
                model_count += 1
                for file in item.rglob("*"):
                    if file.is_file():
                        try:
                            total_size += file.stat().st_size
                        except (OSError, PermissionError):
                            pass
    
    return {
        "exists": True,
        "location": str(cache_dir),
        "size_mb": total_size / (1024 * 1024),
        "size_gb": total_size / (1024 * 1024 * 1024),
        "model_count": model_count,
    }


def clear_cache(model_id: Optional[str] = None, cache_dir: Optional[Path] = None, dry_run: bool = False) -> int:
    """
    Clear cached models.
    
    Args:
        model_id: Optional specific model to clear (clears all if None)
        cache_dir: Optional cache directory (default: auto-detect)
        dry_run: If True, only report what would be deleted
        
    Returns:
        Number of bytes freed
    """
    if cache_dir is None:
        cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        return 0
    
    freed_bytes = 0
    hub_dir = cache_dir / "hub"
    
    if not hub_dir.exists():
        return 0
    
    # Determine what to delete
    if model_id:
        # Specific model
        model_path = model_id.replace("/", "--")
        targets = [hub_dir / f"models--{model_path}"]
    else:
        # All models
        targets = [item for item in hub_dir.iterdir() if item.is_dir() and item.name.startswith("models--")]
    
    for target in targets:
        if not target.exists():
            continue
            
        # Calculate size
        for file in target.rglob("*"):
            if file.is_file():
                try:
                    freed_bytes += file.stat().st_size
                except (OSError, PermissionError):
                    pass
        
        if dry_run:
            console.print(f"[dim]Would delete: {target.name} ({freed_bytes / (1024*1024):.1f} MB)[/dim]")
        else:
            import shutil
            shutil.rmtree(target, ignore_errors=True)
            console.print(f"[dim]Deleted: {target.name} ({freed_bytes / (1024*1024):.1f} MB)[/dim]")
    
    return freed_bytes


def estimate_model_size(model_id: str) -> dict:
    """
    Estimate download size for a model.
    
    Args:
        model_id: HuggingFace model identifier
        
    Returns:
        Dictionary with size estimates
    """
    # Common model size estimates (in MB)
    size_estimates = {
        # Whisper models
        "whisper-tiny": 150,
        "whisper-base": 290,
        "whisper-small": 970,
        "whisper-medium": 3100,
        "whisper-large": 6200,
        # Pyannote models
        "speaker-diarization": 1500,
        "speaker-segmentation": 500,
    }
    
    # Try to match model
    model_lower = model_id.lower()
    for key, size_mb in size_estimates.items():
        if key in model_lower:
            return {
                "estimated_mb": size_mb,
                "estimated_gb": size_mb / 1024,
                "estimated_minutes_10mbps": size_mb / (10 * 60 / 8),
                "estimated_minutes_50mbps": size_mb / (50 * 60 / 8),
            }
    
    # Unknown model - generic estimate
    return {
        "estimated_mb": 1000,
        "estimated_gb": 1.0,
        "estimated_minutes_10mbps": 13.3,
        "estimated_minutes_50mbps": 2.7,
    }


def show_first_run_message(model_name: str, model_type: str = "model"):
    """
    Show informative message for first-run model download.
    
    Args:
        model_name: Name of the model being downloaded
        model_type: Type description (e.g., "diarization model", "Whisper model")
    """
    console.print()
    console.print(f"[bold yellow]📥 First-time setup: Downloading {model_type}[/bold yellow]")
    console.print(f"[dim]Model: {model_name}[/dim]")
    console.print()
    
    size_info = estimate_model_size(model_name)
    console.print(f"[dim]Estimated size: ~{size_info['estimated_mb']:.0f} MB ({size_info['estimated_gb']:.1f} GB)[/dim]")
    console.print(f"[dim]This may take 2-10 minutes depending on your connection...[/dim]")
    console.print()


@contextmanager
def loading_spinner(message: str, complete_message: Optional[str] = None):
    """
    Show loading spinner for operations without progress tracking.
    
    Args:
        message: Message to show while loading
        complete_message: Optional message to show when complete
        
    Example:
        with loading_spinner("Loading model...", "Model loaded!"):
            model = load_model()
    """
    with console.status(f"[bold cyan]{message}[/bold cyan]") as status:
        yield status
    
    if complete_message:
        console.print(f"[green]✓[/green] {complete_message}")


def wrap_model_download(
    download_func: Callable,
    model_name: str,
    model_type: str = "model",
    check_cache: bool = True,
    *args,
    **kwargs
):
    """
    Wrap model download function with progress indicators.
    
    Args:
        download_func: Function that downloads/loads the model
        model_name: Name of the model
        model_type: Type description
        check_cache: Whether to check cache first
        *args: Positional arguments for download_func
        **kwargs: Keyword arguments for download_func
        
    Returns:
        Result of download_func
    """
    # Check if cached
    if check_cache and check_model_cached(model_name):
        console.print(f"[dim]✓ Using cached {model_type}: {model_name}[/dim]")
        with loading_spinner(f"Loading {model_type}...", f"{model_type.capitalize()} loaded"):
            return download_func(*args, **kwargs)
    else:
        # First-time download
        show_first_run_message(model_name, model_type)
        with loading_spinner(
            f"Downloading and loading {model_type}...",
            f"{model_type.capitalize()} ready"
        ):
            return download_func(*args, **kwargs)
