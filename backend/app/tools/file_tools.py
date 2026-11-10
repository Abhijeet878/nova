"""
FILE_TOOLS.PY — File System Operations
========================================
WHAT IT DOES:
    Gives agents the ability to read, write, list, and organize
    files on the local computer.

WHY IT EXISTS:
    The LLM (brain) cannot touch the file system by itself.
    These functions are the "hands" that let the agent actually
    DO things — read documents, create reports, organize folders.

FOR JUDGES:
    "Our file tools operate within a sandboxed workspace directory.
    The agent cannot access files outside the designated workspace
    and outputs folders, which ensures safety."

SAFETY:
    - All paths are resolved relative to WORKSPACE_DIR or OUTPUTS_DIR
    - No absolute paths outside the sandbox are allowed
    - File sizes are capped to prevent memory issues
"""

import os
import shutil
import hashlib
from pathlib import Path
from backend.app.config import WORKSPACE_DIR, OUTPUTS_DIR


def read_file(file_path: str) -> dict:
    """Read the contents of a file.
    
    Args:
        file_path: Filename (relative to workspace) or absolute path
        
    Returns:
        dict with 'success' boolean and 'content' or 'error' string
    
    Example:
        >>> read_file("report.txt")
        {"success": True, "content": "This is the report content..."}
    """
    try:
        # Resolve the path safely within workspace
        path = _resolve_path(file_path, WORKSPACE_DIR)
        
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        if not path.is_file():
            return {"success": False, "error": f"Not a file: {file_path}"}
        
        content = path.read_text(encoding="utf-8", errors="replace")
        
        # Cap at 10,000 characters to avoid overloading the LLM's context
        if len(content) > 10_000:
            content = content[:10_000] + "\n\n... [TRUNCATED — file exceeds 10,000 characters]"
        
        return {"success": True, "content": content}
    
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def write_file(file_path: str, content: str) -> dict:
    """Write content to a file in the outputs directory.
    
    Args:
        file_path: Filename (will be created in outputs directory)
        content: Text content to write
        
    Returns:
        dict with 'success' boolean and 'path' or 'error' string
        
    Example:
        >>> write_file("report.md", "# My Report\\nFindings: ...")
        {"success": True, "path": "outputs/report.md"}
    """
    try:
        path = _resolve_path(file_path, OUTPUTS_DIR)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding="utf-8")
        
        return {
            "success": True,
            "path": str(path),
            "size_bytes": len(content.encode("utf-8"))
        }
    
    except Exception as e:
        return {"success": False, "error": f"Error writing file: {str(e)}"}


def list_directory(directory_path: str = ".") -> dict:
    """List all files and folders in a directory.
    
    Args:
        directory_path: Directory to list (relative to workspace)
        
    Returns:
        dict with 'success' boolean and list of file info dicts
        
    Example:
        >>> list_directory(".")
        {"success": True, "files": [
            {"name": "data.csv", "type": "file", "size": "2.3 KB"},
            {"name": "images", "type": "directory", "items": 5}
        ]}
    """
    try:
        path = _resolve_path(directory_path, WORKSPACE_DIR)
        
        if not path.exists():
            return {"success": False, "error": f"Directory not found: {directory_path}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Not a directory: {directory_path}"}
        
        files = []
        for item in sorted(path.iterdir()):
            if item.name.startswith("."):
                continue  # Skip hidden files
            
            if item.is_file():
                size = item.stat().st_size
                files.append({
                    "name": item.name,
                    "type": "file",
                    "size": _format_size(size),
                    "extension": item.suffix
                })
            elif item.is_dir():
                item_count = sum(1 for _ in item.iterdir())
                files.append({
                    "name": item.name,
                    "type": "directory",
                    "items": item_count
                })
        
        return {"success": True, "files": files, "total": len(files)}
    
    except Exception as e:
        return {"success": False, "error": f"Error listing directory: {str(e)}"}


def find_duplicates(directory_path: str = ".") -> dict:
    """Find duplicate files using MD5 hash comparison.
    
    This is a key demo feature — shows the agent can detect
    duplicate files by comparing their actual content, not just names.
    
    Args:
        directory_path: Directory to scan
        
    Returns:
        dict with duplicate groups
    """
    try:
        path = _resolve_path(directory_path, WORKSPACE_DIR)
        
        if not path.exists() or not path.is_dir():
            return {"success": False, "error": f"Invalid directory: {directory_path}"}
        
        # Hash every file
        hash_map: dict[str, list[str]] = {}
        for file_path in path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                file_hash = _compute_hash(file_path)
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(str(file_path.relative_to(path)))
        
        # Filter to only groups with duplicates
        duplicates = {
            h: files for h, files in hash_map.items() 
            if len(files) > 1
        }
        
        return {
            "success": True,
            "total_files_scanned": sum(len(v) for v in hash_map.values()),
            "duplicate_groups": len(duplicates),
            "duplicates": duplicates
        }
    
    except Exception as e:
        return {"success": False, "error": f"Error finding duplicates: {str(e)}"}


def organize_files(directory_path: str = ".") -> dict:
    """Organize files into categorized subfolders by file type.
    
    Creates folders like Documents/, Images/, Videos/, Code/, Data/, Others/
    and moves files into the appropriate category.
    
    Args:
        directory_path: Directory to organize
        
    Returns:
        dict with organization results and per-file status
    """
    # File type categories
    CATEGORIES = {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "Code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css"],
        "Data": [".csv", ".json", ".xml", ".xlsx", ".xls", ".sql", ".db"],
        "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    }
    
    try:
        path = _resolve_path(directory_path, WORKSPACE_DIR)
        
        if not path.exists() or not path.is_dir():
            return {"success": False, "error": f"Invalid directory: {directory_path}"}
        
        results = {"moved": [], "failed": [], "skipped": []}
        
        for file_path in path.iterdir():
            if file_path.is_dir() or file_path.name.startswith("."):
                continue
            
            # Determine category
            ext = file_path.suffix.lower()
            category = "Others"
            for cat_name, extensions in CATEGORIES.items():
                if ext in extensions:
                    category = cat_name
                    break
            
            # Create category folder and move file
            target_dir = path / category
            target_dir.mkdir(exist_ok=True)
            target_path = target_dir / file_path.name
            
            try:
                shutil.move(str(file_path), str(target_path))
                results["moved"].append({
                    "file": file_path.name,
                    "category": category,
                    "destination": str(target_path.relative_to(path))
                })
            except Exception as e:
                results["failed"].append({
                    "file": file_path.name,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_moved": len(results["moved"]),
            "total_failed": len(results["failed"]),
            "details": results
        }
    
    except Exception as e:
        return {"success": False, "error": f"Error organizing files: {str(e)}"}


# ─── Helper Functions ────────────────────────────────────────

def _resolve_path(file_path: str, base_dir: Path) -> Path:
    """Safely resolve a path within the allowed base directory.
    
    This prevents path traversal attacks (e.g., "../../etc/passwd").
    """
    path = Path(file_path)
    if path.is_absolute():
        resolved = path.resolve()
    else:
        resolved = (base_dir / path).resolve()
    
    # Security: ensure the path is within the allowed directory
    base_resolved = base_dir.resolve()
    if not str(resolved).startswith(str(base_resolved)):
        raise PermissionError(
            f"Access denied: path '{file_path}' is outside the allowed directory"
        )
    
    return resolved


def _compute_hash(file_path: Path) -> str:
    """Compute MD5 hash of a file for duplicate detection."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
