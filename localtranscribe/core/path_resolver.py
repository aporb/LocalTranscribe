"""
Smart path resolution for audio files and output directories.

Resolves file paths from multiple locations and generates consistent output paths.
"""

from pathlib import Path
from typing import Optional, Union, List
import os

from ..utils.errors import AudioFileNotFoundError


class PathResolver:
    """Smart path resolution for audio files and outputs."""

    # Supported audio file extensions
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus'}

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize path resolver with base directory.

        Args:
            base_dir: Base directory for relative path resolution (default: current working directory)
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"

    def resolve_audio_file(self, file_path: Union[str, Path]) -> Path:
        """
        Find audio file in multiple locations with smart fallback.

        Search order:
        1. Absolute path (if provided)
        2. Relative to current directory
        3. Relative to input directory
        4. Filename only in input directory

        Args:
            file_path: Path to audio file (can be relative, absolute, or filename only)

        Returns:
            Resolved absolute path to audio file

        Raises:
            AudioFileNotFoundError: If file cannot be found in any location
        """
        path = Path(file_path)

        # Try absolute path first
        if path.is_absolute():
            if path.exists():
                return path
            raise AudioFileNotFoundError(
                f"Audio file not found: {file_path}",
                suggestions=[
                    "Check that the file path is correct",
                    f"Verify file exists at: {path}",
                    "Try using a relative path instead",
                ],
                context={
                    'searched_path': str(file_path),
                    'absolute_path': str(path),
                    'exists': path.exists(),
                },
            )

        # Try current directory
        if path.exists():
            return path.resolve()

        # Try relative to base directory
        base_path = self.base_dir / path
        if base_path.exists():
            return base_path.resolve()

        # Try input directory with full path
        input_path = self.input_dir / path
        if input_path.exists():
            return input_path.resolve()

        # Try input directory with just filename
        if self.input_dir.exists():
            filename_only = Path(path.name)
            input_filename_path = self.input_dir / filename_only
            if input_filename_path.exists():
                return input_filename_path.resolve()

        # File not found - provide helpful error
        self._raise_not_found_error(file_path)

    def _raise_not_found_error(self, file_path: Union[str, Path]) -> None:
        """Raise detailed error when audio file cannot be found."""
        path = Path(file_path)

        # List files in input directory if it exists
        input_files = []
        if self.input_dir.exists():
            input_files = [
                f.name
                for f in self.input_dir.iterdir()
                if f.is_file() and f.suffix.lower() in self.AUDIO_EXTENSIONS
            ]

        suggestions = [
            f"Place file in input directory: {self.input_dir}",
            "Provide absolute path to the file",
            f"Check file name spelling: '{path.name}'",
        ]

        if input_files:
            suggestions.append(f"Available files in input/: {', '.join(input_files[:5])}")

        context = {
            'searched_path': str(file_path),
            'current_dir': str(Path.cwd()),
            'base_dir': str(self.base_dir),
            'input_dir': str(self.input_dir),
            'input_dir_exists': self.input_dir.exists(),
            'audio_files_in_input': input_files if input_files else ['(none)'],
        }

        raise AudioFileNotFoundError(
            f"Audio file not found: {file_path}",
            suggestions=suggestions,
            context=context,
        )

    def resolve_output_path(
        self,
        input_file: Path,
        suffix: str,
        extension: str,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """
        Generate output path based on input filename with consistent naming.

        Args:
            input_file: Input audio file path
            suffix: Suffix to add to filename (e.g., 'diarization', 'transcript')
            extension: Output file extension (without dot, e.g., 'md', 'json')
            output_dir: Override output directory (default: self.output_dir)

        Returns:
            Path to output file with format: {basename}_{suffix}.{extension}
        """
        out_dir = Path(output_dir) if output_dir else self.output_dir

        # Create output directory if it doesn't exist
        out_dir.mkdir(parents=True, exist_ok=True)

        # Get base filename without extension
        base_name = input_file.stem

        # Construct output filename
        output_filename = f"{base_name}_{suffix}.{extension}"

        return out_dir / output_filename

    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        Ensure directory exists, create if necessary.

        Args:
            directory: Directory path to ensure exists

        Returns:
            Absolute path to directory
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path.resolve()

    def validate_audio_file(self, file_path: Path) -> bool:
        """
        Validate that file is a supported audio format.

        Args:
            file_path: Path to audio file

        Returns:
            True if valid audio file

        Raises:
            InvalidAudioFormatError: If file format is not supported
        """
        from ..utils.errors import InvalidAudioFormatError

        if not file_path.exists():
            return False

        if file_path.suffix.lower() not in self.AUDIO_EXTENSIONS:
            raise InvalidAudioFormatError(
                f"Unsupported audio format: {file_path.suffix}",
                suggestions=[
                    f"Supported formats: {', '.join(sorted(self.AUDIO_EXTENSIONS))}",
                    "Convert your audio to a supported format",
                    "Use FFmpeg to convert: ffmpeg -i input.ext output.mp3",
                ],
                context={
                    'file': str(file_path),
                    'extension': file_path.suffix,
                    'supported_formats': sorted(self.AUDIO_EXTENSIONS),
                },
            )

        # Check file is readable
        if not os.access(file_path, os.R_OK):
            raise InvalidAudioFormatError(
                f"Audio file is not readable: {file_path}",
                suggestions=[
                    "Check file permissions",
                    f"Try: chmod +r {file_path}",
                ],
                context={'file': str(file_path)},
            )

        return True

    def get_relative_path(self, file_path: Path, relative_to: Optional[Path] = None) -> Path:
        """
        Get relative path from base directory.

        Args:
            file_path: File path to make relative
            relative_to: Base path to make relative to (default: self.base_dir)

        Returns:
            Relative path
        """
        base = Path(relative_to) if relative_to else self.base_dir
        try:
            return file_path.relative_to(base)
        except ValueError:
            # If not relative, return absolute path
            return file_path.resolve()
