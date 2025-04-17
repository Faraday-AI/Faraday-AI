import joblib
import os
from pathlib import Path

def check_joblib_file(file_path):
    try:
        print(f"\nChecking {file_path}...")
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size} bytes")
        
        if file_size < 100:  # Very small files might be corrupted
            print("Warning: File size is very small, might be corrupted")
        
        # Try to load the file
        data = joblib.load(file_path)
        print(f"Successfully loaded file. Content type: {type(data)}")
        return True
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return False

if __name__ == "__main__":
    # Get the directory of this script
    current_dir = Path(__file__).parent
    
    # Check both joblib files
    files_to_check = [
        current_dir / "activity_adaptation.joblib",
        current_dir / "skill_assessment.joblib"
    ]
    
    for file_path in files_to_check:
        check_joblib_file(file_path) 