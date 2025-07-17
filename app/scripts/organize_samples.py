import os
import shutil
import json
from datetime import datetime
from typing import Dict, List

class SampleOrganizer:
    def __init__(self):
        self.test_data_dir = os.path.join('data', 'test_data')
        self.organized_dir = os.path.join('data', 'organized_samples')
        
    def organize_samples(self):
        """Organize samples into a more structured format."""
        # Create organized directory if it doesn't exist
        os.makedirs(self.organized_dir, exist_ok=True)
        
        # Process each category
        for category in os.listdir(self.test_data_dir):
            category_path = os.path.join(self.test_data_dir, category)
            if not os.path.isdir(category_path):
                continue
                
            print(f"\nProcessing {category} samples...")
            
            # Process each movement in the category
            for movement in os.listdir(category_path):
                movement_path = os.path.join(category_path, movement)
                if not os.path.isdir(movement_path):
                    continue
                    
                print(f"  Organizing {movement} samples...")
                
                # Create organized movement directory
                organized_movement_dir = os.path.join(self.organized_dir, category, movement)
                os.makedirs(organized_movement_dir, exist_ok=True)
                
                # Process each sample file
                for sample_file in os.listdir(movement_path):
                    if not sample_file.endswith('.json'):
                        continue
                        
                    sample_path = os.path.join(movement_path, sample_file)
                    
                    # Read the sample data
                    with open(sample_path, 'r') as f:
                        data = json.load(f)
                    
                    # Create organized sample directory
                    sample_name = os.path.splitext(sample_file)[0]
                    organized_sample_dir = os.path.join(organized_movement_dir, sample_name)
                    os.makedirs(organized_sample_dir, exist_ok=True)
                    
                    # Split data into separate files
                    self._split_sample_data(data, organized_sample_dir)
                    
                    print(f"    Organized {sample_file}")
        
        print("\nSample organization completed successfully!")
    
    def _split_sample_data(self, data: Dict, output_dir: str):
        """Split sample data into separate files for better organization."""
        # Save base metrics
        with open(os.path.join(output_dir, 'base_metrics.json'), 'w') as f:
            json.dump(data['base_metrics'], f, indent=2)
        
        # Save enhanced metrics
        with open(os.path.join(output_dir, 'enhanced_metrics.json'), 'w') as f:
            json.dump(data['enhanced_metrics'], f, indent=2)
        
        # Save metadata
        metadata = {
            'movement_type': data['movement_type'],
            'category': data['category'],
            'timestamp': data['timestamp']
        }
        with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

def main():
    organizer = SampleOrganizer()
    organizer.organize_samples()

if __name__ == '__main__':
    main() 