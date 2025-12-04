"""Operation logger module for recording and managing file operations."""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from .classifier import FileCategory


@dataclass
class FileOperation:
    """Record of a single file operation."""
    source_path: str
    dest_path: str
    category: str
    timestamp: str
    conflict_resolved: bool


@dataclass
class OperationLog:
    """Log of all operations in a sorting session."""
    log_path: Path
    operations: list[FileOperation]
    start_time: datetime
    end_time: Optional[datetime] = None


def create_operation_log(source_path: Path) -> OperationLog:
    """Initialize a new operation log.
    
    Args:
        source_path: The source directory being sorted
        
    Returns:
        OperationLog: A new operation log instance
    """
    start_time = datetime.now()
    log_path = get_log_path(source_path, start_time)
    
    # Ensure log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    return OperationLog(
        log_path=log_path,
        operations=[],
        start_time=start_time,
        end_time=None
    )


def log_file_movement(log: OperationLog, src: Path, dest: Path, 
                     category: FileCategory, conflict_resolved: bool = False) -> None:
    """Record a file movement operation.
    
    Args:
        log: The operation log to record to
        src: Source file path
        dest: Destination file path
        category: File category
        conflict_resolved: Whether a naming conflict was resolved
    """
    operation = FileOperation(
        source_path=str(src),
        dest_path=str(dest),
        category=category.value,
        timestamp=datetime.now().isoformat(),
        conflict_resolved=conflict_resolved
    )
    log.operations.append(operation)


def finalize_log(log: OperationLog) -> None:
    """Save the operation log to disk as JSON.
    
    Args:
        log: The operation log to finalize
    """
    log.end_time = datetime.now()
    
    # Convert to dictionary for JSON serialization
    log_data = {
        "start_time": log.start_time.isoformat(),
        "end_time": log.end_time.isoformat(),
        "operations": [
            {
                "source": op.source_path,
                "destination": op.dest_path,
                "category": op.category,
                "timestamp": op.timestamp,
                "conflict_resolved": op.conflict_resolved
            }
            for op in log.operations
        ]
    }
    
    # Write to file
    with open(log.log_path, 'w') as f:
        json.dump(log_data, f, indent=2)


def read_latest_log(source_path: Path) -> Optional[OperationLog]:
    """Load the most recent operation log.
    
    Args:
        source_path: The source directory that was sorted
        
    Returns:
        OperationLog or None: The most recent log, or None if no logs exist
    """
    log_dir = Path.home() / '.sik_sort' / 'logs'
    
    if not log_dir.exists():
        return None
    
    # Find all log files
    log_files = list(log_dir.glob('operation_log_*.json'))
    
    if not log_files:
        return None
    
    # Sort by modification time and get the most recent
    latest_log_file = max(log_files, key=lambda p: p.stat().st_mtime)
    
    # Read and parse the log file
    try:
        with open(latest_log_file, 'r') as f:
            log_data = json.load(f)
        
        # Convert back to OperationLog
        operations = [
            FileOperation(
                source_path=op["source"],
                dest_path=op["destination"],
                category=op["category"],
                timestamp=op["timestamp"],
                conflict_resolved=op["conflict_resolved"]
            )
            for op in log_data["operations"]
        ]
        
        return OperationLog(
            log_path=latest_log_file,
            operations=operations,
            start_time=datetime.fromisoformat(log_data["start_time"]),
            end_time=datetime.fromisoformat(log_data["end_time"]) if log_data.get("end_time") else None
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def get_log_path(source_path: Path, timestamp: datetime) -> Path:
    """Generate a timestamped log file path.
    
    Args:
        source_path: The source directory being sorted
        timestamp: Timestamp for the log file
        
    Returns:
        Path: Path to the log file
    """
    log_dir = Path.home() / '.sik_sort' / 'logs'
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    log_filename = f'operation_log_{timestamp_str}.json'
    return log_dir / log_filename
