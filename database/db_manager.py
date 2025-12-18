import csv
import os
import threading
from typing import List, Dict, Optional

class CSVDatabase:
    """CSV Database Manager với thread-safe operations"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.lock = threading.Lock()
        
        # Tạo data directory nếu chưa tồn tại
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def _get_filepath(self, filename: str) -> str:
        """Lấy đường dẫn đầy đủ đến file"""
        return os.path.join(self.data_dir, filename)
    
    def _ensure_file_exists(self, filename: str, fieldnames: List[str]):
        """Đảm bảo file tồn tại với headers"""
        filepath = self._get_filepath(filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
    
    def read(self, filename: str) -> List[Dict]:
        """Đọc tất cả rows từ CSV file"""
        filepath = self._get_filepath(filename)
        
        if not os.path.exists(filepath):
            return []
        
        with self.lock:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return list(csv.DictReader(f))
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                return []
    
    def write(self, filename: str, data: List[Dict], fieldnames: List[str]):
        """Ghi data vào CSV file (overwrite)"""
        filepath = self._get_filepath(filename)
        
        with self.lock:
            try:
                with open(filepath, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            except Exception as e:
                print(f"Error writing {filename}: {e}")
                raise
    
    def append(self, filename: str, row: Dict, fieldnames: List[str]):
        """Thêm một row vào CSV file"""
        filepath = self._get_filepath(filename)
        
        # Ensure file exists with headers
        self._ensure_file_exists(filename, fieldnames)
        
        with self.lock:
            try:
                with open(filepath, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(row)
            except Exception as e:
                print(f"Error appending to {filename}: {e}")
                raise
    
    def get_next_id(self, filename: str, id_field: str) -> int:
        """Lấy ID tiếp theo (auto-increment)"""
        data = self.read(filename)
        if not data:
            return 1
        
        try:
            max_id = max(int(row[id_field]) for row in data if row.get(id_field))
            return max_id + 1
        except (ValueError, KeyError):
            return 1
    
    def find_by_field(self, filename: str, field: str, value: str) -> Optional[Dict]:
        """Tìm row đầu tiên có field = value"""
        data = self.read(filename)
        for row in data:
            if row.get(field) == value:
                return row
        return None
    
    def find_all_by_field(self, filename: str, field: str, value: str) -> List[Dict]:
        """Tìm tất cả rows có field = value"""
        data = self.read(filename)
        return [row for row in data if row.get(field) == value]
    
    def update_by_field(self, filename: str, field: str, value: str, 
                       updated_row: Dict, fieldnames: List[str]):
        """Cập nhật row đầu tiên có field = value"""
        data = self.read(filename)
        updated = False
        
        for i, row in enumerate(data):
            if row.get(field) == value:
                data[i] = updated_row
                updated = True
                break
        
        if updated:
            self.write(filename, data, fieldnames)
        
        return updated
    
    def delete_by_field(self, filename: str, field: str, value: str, 
                       fieldnames: List[str]):
        """Xóa tất cả rows có field = value"""
        data = self.read(filename)
        filtered_data = [row for row in data if row.get(field) != value]
        
        if len(filtered_data) < len(data):
            self.write(filename, filtered_data, fieldnames)
            return True
        
        return False
