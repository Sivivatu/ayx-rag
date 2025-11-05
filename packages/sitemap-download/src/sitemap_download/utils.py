"""Utility functions for sitemap download operations."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


def archive_file(file_path: Path) -> Optional[Path]:
    """Archive existing file with timestamp suffix.
    
    Creates a copy of the file with a timestamp appended to the filename
    in the format: {stem}_{YYYY_MM_DD_HH_MM}{suffix}
    
    Args:
        file_path: Path to file to archive
        
    Returns:
        Path to archived file, or None if file doesn't exist
        
    Example:
        >>> archive_file(Path("sitemap.xml"))
        PosixPath("sitemap_2025_11_05_14_30.xml")
    """
    if not file_path.exists():
        return None
    
    # Generate timestamp suffix (yyyy_mm_dd_hh_mm)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    
    # Create archive filename
    stem = file_path.stem
    suffix = file_path.suffix
    archive_name = f"{stem}_{timestamp}{suffix}"
    archive_path = file_path.parent / archive_name
    
    # Copy file to archive (preserves metadata)
    shutil.copy2(file_path, archive_path)
    
    return archive_path


def format_bytes(bytes_count: int) -> str:
    """Format bytes as human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "45.2 MB")
        
    Example:
        >>> format_bytes(1536)
        '1.5 KB'
        >>> format_bytes(1048576)
        '1.0 MB'
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"
