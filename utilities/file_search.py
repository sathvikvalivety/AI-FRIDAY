# utilities/file_search.py
import os
import fnmatch
from pathlib import Path

class FileSearchManager:
    def __init__(self):
        self.search_results = []
        self.is_searching = False
        
    def search_files_by_content(self, keyword, file_types=None):
        """Search for keyword in file contents"""
        if not file_types:
            file_types = ['*.txt', '*.pdf', '*.docx', '*.doc', '*.xlsx', '*.xls', '*.pptx', '*.ppt']
        
        self.search_results = []
        self.is_searching = True
        
        # Get all user directories to search
        search_paths = [
            str(Path.home()),  # Home directory
            "/Users",          # macOS
            "/home",           # Linux
            "C:\\Users"        # Windows
        ]
        
        # Filter to existing paths
        valid_paths = [path for path in search_paths if os.path.exists(path)]
        
        print(f"🔍 Searching for '{keyword}' in {len(valid_paths)} locations...")
        
        # Search in each path
        for search_path in valid_paths:
            if not self.is_searching:
                break
            self._search_in_directory(search_path, keyword, file_types)
        
        self.is_searching = False
        return self.search_results
    
    def _search_in_directory(self, directory, keyword, file_types):
        """Recursively search directory for files containing keyword"""
        try:
            for root, dirs, files in os.walk(directory):
                # Skip system directories for faster searching
                skip_dirs = ['.git', 'node_modules', '__pycache__', '.cache', 'Library']
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                for file in files:
                    if not self.is_searching:
                        return
                    
                    # Check if file matches our types
                    if any(fnmatch.fnmatch(file.lower(), pattern.lower()) for pattern in file_types):
                        file_path = os.path.join(root, file)
                        if self._file_contains_keyword(file_path, keyword):
                            self.search_results.append({
                                'path': file_path,
                                'name': file,
                                'folder': root
                            })
                            
        except (PermissionError, OSError):
            pass  # Skip directories we can't access
    
    def _file_contains_keyword(self, file_path, keyword):
        """Check if file contains the keyword (basic text files only for now)"""
        try:
            # For text-based files
            if file_path.lower().endswith(('.txt', '.py', '.java', '.js', '.html', '.css', '.md')):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    return keyword.lower() in content
            
            # For PDF, DOCX, etc. we'd need libraries like PyPDF2, python-docx
            # For now, search in filename as fallback
            return keyword.lower() in os.path.basename(file_path).lower()
            
        except:
            return False
    
    def stop_search(self):
        """Stop the current search"""
        self.is_searching = False
    
    def open_file(self, file_path):
        """Open file with default application"""
        try:
            os.startfile(file_path)  # Windows
            return True
        except AttributeError:
            try:
                os.system(f'open "{file_path}"')  # macOS
                return True
            except:
                try:
                    os.system(f'xdg-open "{file_path}"')  # Linux
                    return True
                except:
                    return False
