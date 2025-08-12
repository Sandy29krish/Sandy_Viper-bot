"""
File utility functions for Sandy Viper Bot
Handles file operations, data persistence, and backup management
"""

import os
import json
import csv
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pickle


class FileUtils:
    """File operation utilities"""
    
    @staticmethod
    def ensure_directory(directory_path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if it doesn't"""
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def read_json(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Read JSON file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Error reading JSON file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_json(data: Dict[str, Any], file_path: Union[str, Path], 
                   indent: int = 2, ensure_dir: bool = True) -> bool:
        """Write data to JSON file safely"""
        try:
            path = Path(file_path)
            
            if ensure_dir:
                FileUtils.ensure_directory(path.parent)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
            
            return True
            
        except (IOError, TypeError) as e:
            print(f"Error writing JSON file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_csv(file_path: Union[str, Path], has_header: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Read CSV file to list of dictionaries"""
        try:
            data = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if has_header:
                    reader = csv.DictReader(f)
                    data = list(reader)
                else:
                    reader = csv.reader(f)
                    data = [{'col_' + str(i): value for i, value in enumerate(row)} 
                           for row in reader]
            
            return data
            
        except (FileNotFoundError, IOError) as e:
            print(f"Error reading CSV file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_csv(data: List[Dict[str, Any]], file_path: Union[str, Path], 
                  fieldnames: Optional[List[str]] = None, ensure_dir: bool = True) -> bool:
        """Write data to CSV file"""
        try:
            if not data:
                return False
            
            path = Path(file_path)
            
            if ensure_dir:
                FileUtils.ensure_directory(path.parent)
            
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True
            
        except (IOError, TypeError) as e:
            print(f"Error writing CSV file {file_path}: {e}")
            return False
    
    @staticmethod
    def append_csv(data: Dict[str, Any], file_path: Union[str, Path], 
                   fieldnames: Optional[List[str]] = None, ensure_dir: bool = True) -> bool:
        """Append data to CSV file"""
        try:
            path = Path(file_path)
            
            if ensure_dir:
                FileUtils.ensure_directory(path.parent)
            
            # Check if file exists to write header
            file_exists = path.exists()
            
            if fieldnames is None:
                fieldnames = list(data.keys())
            
            with open(path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(data)
            
            return True
            
        except (IOError, TypeError) as e:
            print(f"Error appending to CSV file {file_path}: {e}")
            return False
    
    @staticmethod
    def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Optional[Path]:
        """Create backup of a file"""
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                return None
            
            if backup_dir is None:
                backup_dir = source_path.parent / "backups"
            
            backup_dir = Path(backup_dir)
            FileUtils.ensure_directory(backup_dir)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(source_path, backup_path)
            return backup_path
            
        except (IOError, OSError) as e:
            print(f"Error creating backup of {file_path}: {e}")
            return None
    
    @staticmethod
    def save_pickle(obj: Any, file_path: Union[str, Path], ensure_dir: bool = True) -> bool:
        """Save object using pickle"""
        try:
            path = Path(file_path)
            
            if ensure_dir:
                FileUtils.ensure_directory(path.parent)
            
            with open(path, 'wb') as f:
                pickle.dump(obj, f)
            
            return True
            
        except (IOError, pickle.PickleError) as e:
            print(f"Error saving pickle file {file_path}: {e}")
            return False
    
    @staticmethod
    def load_pickle(file_path: Union[str, Path]) -> Any:
        """Load object from pickle file"""
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
                
        except (FileNotFoundError, IOError, pickle.PickleError) as e:
            print(f"Error loading pickle file {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except (FileNotFoundError, OSError):
            return 0
    
    @staticmethod
    def get_file_modified_time(file_path: Union[str, Path]) -> Optional[datetime]:
        """Get file last modified time"""
        try:
            timestamp = Path(file_path).stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        except (FileNotFoundError, OSError):
            return None
    
    @staticmethod
    def clean_old_files(directory: Union[str, Path], max_age_days: int = 30, 
                       pattern: str = "*") -> int:
        """Clean old files from directory"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except (OSError, IOError) as e:
            print(f"Error cleaning old files: {e}")
            return 0
    
    @staticmethod
    def create_zip_archive(source_dir: Union[str, Path], archive_path: Union[str, Path],
                          include_patterns: Optional[List[str]] = None) -> bool:
        """Create zip archive of directory"""
        try:
            source_path = Path(source_dir)
            archive_path = Path(archive_path)
            
            FileUtils.ensure_directory(archive_path.parent)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if include_patterns:
                    # Include specific patterns
                    for pattern in include_patterns:
                        for file_path in source_path.rglob(pattern):
                            if file_path.is_file():
                                arcname = file_path.relative_to(source_path)
                                zipf.write(file_path, arcname)
                else:
                    # Include all files
                    for file_path in source_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_path)
                            zipf.write(file_path, arcname)
            
            return True
            
        except (IOError, OSError, zipfile.BadZipFile) as e:
            print(f"Error creating zip archive: {e}")
            return False
    
    @staticmethod
    def extract_zip_archive(archive_path: Union[str, Path], extract_to: Union[str, Path]) -> bool:
        """Extract zip archive"""
        try:
            archive_path = Path(archive_path)
            extract_path = Path(extract_to)
            
            FileUtils.ensure_directory(extract_path)
            
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(extract_path)
            
            return True
            
        except (IOError, zipfile.BadZipFile) as e:
            print(f"Error extracting zip archive: {e}")
            return False
    
    @staticmethod
    def rotate_log_files(log_file: Union[str, Path], max_files: int = 5) -> bool:
        """Rotate log files (log.txt -> log.1.txt -> log.2.txt, etc.)"""
        try:
            log_path = Path(log_file)
            
            if not log_path.exists():
                return True
            
            # Remove oldest log file if it exists
            oldest_log = log_path.with_suffix(f'.{max_files}{log_path.suffix}')
            if oldest_log.exists():
                oldest_log.unlink()
            
            # Rotate existing log files
            for i in range(max_files - 1, 0, -1):
                current_log = log_path.with_suffix(f'.{i}{log_path.suffix}')
                next_log = log_path.with_suffix(f'.{i + 1}{log_path.suffix}')
                
                if current_log.exists():
                    current_log.rename(next_log)
            
            # Move current log to .1
            if log_path.exists():
                rotated_log = log_path.with_suffix(f'.1{log_path.suffix}')
                log_path.rename(rotated_log)
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Error rotating log files: {e}")
            return False
    
    @staticmethod
    def safe_delete_file(file_path: Union[str, Path]) -> bool:
        """Safely delete a file"""
        try:
            path = Path(file_path)
            
            if path.exists() and path.is_file():
                path.unlink()
                return True
            
            return False
            
        except (OSError, IOError) as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_directory_size(directory: Union[str, Path]) -> int:
        """Get total size of directory in bytes"""
        try:
            total_size = 0
            dir_path = Path(directory)
            
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except (OSError, IOError):
            return 0
    
    @staticmethod
    def copy_file_with_backup(source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy file with automatic backup of destination"""
        try:
            dest_path = Path(destination)
            
            # Create backup if destination exists
            if dest_path.exists():
                FileUtils.backup_file(dest_path)
            
            # Ensure destination directory exists
            FileUtils.ensure_directory(dest_path.parent)
            
            # Copy file
            shutil.copy2(source, destination)
            return True
            
        except (IOError, OSError) as e:
            print(f"Error copying file: {e}")
            return False
