import json
import cv2
import numpy as np
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def draw_stick_figure(frame, key_points, width, height):
    """Draw a stick figure based on key points."""
    # Define connections between key points
    connections = [
        ('shoulders', 'elbows'),
        ('elbows', 'wrists'),
        ('shoulders', 'hips'),
        ('hips', 'knees'),
        ('knees', 'ankles')
    ]
    
    # Scale and draw points
    points = {}
    for point_name, coords in key_points.items():
        # Scale coordinates to image dimensions
        x = int((coords[0] + 0.5) * width)  # Center around 0
        y = int((0.5 - coords[1]) * height)  # Flip Y axis
        points[point_name] = (x, y)
        
        # Draw point
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(frame, point_name, (x + 10, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Draw connections
    for start, end in connections:
        if start in points and end in points:
            cv2.line(frame, points[start], points[end], (0, 255, 0), 2)

def draw_bar_chart(frame, data, x, y, width, height, title):
    """Draw a bar chart for metrics."""
    if not data:
        return
    
    # Draw title
    cv2.putText(frame, title, (x, y - 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Calculate bar dimensions
    num_bars = len(data)
    bar_width = width // (num_bars + 1)
    spacing = bar_width // 2
    
    # Draw bars
    for i, (label, value) in enumerate(data.items()):
        bar_x = x + spacing + i * (bar_width + spacing)
        bar_height = int(value * height)
        bar_y = y + height - bar_height
        
        # Draw bar
        color = (0, int(255 * value), 0)  # Green based on value
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, y + height), color, -1)
        
        # Draw label
        cv2.putText(frame, f"{label}: {value:.2f}", (bar_x, y + height + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

def create_video_from_json(json_path, output_path, width=640, height=480, fps=30, duration=3):
    """Create a video from JSON movement data."""
    try:
        # Read JSON data
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Create frames
        num_frames = fps * duration
        for frame_idx in range(num_frames):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame.fill(255)  # White background
            
            # Calculate progress through the movement (0 to 1)
            progress = frame_idx / num_frames
            
            # Draw based on file type
            if 'key_points' in data:
                # Base metrics visualization
                draw_stick_figure(frame, data['key_points'], width, height)
                
                # Draw angles
                if 'angles' in data:
                    angle_text = "Angles: "
                    for joint, angle in data['angles'].items():
                        angle_text += f"{joint}: {angle:.1f}° "
                    cv2.putText(frame, angle_text, (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                
                # Draw analysis scores
                if 'analysis_scores' in data:
                    draw_bar_chart(frame, data['analysis_scores'],
                                 width // 2, height // 2, width // 2, height // 2,
                                 "Analysis Scores")
            
            elif 'power_generation' in data:
                # Enhanced metrics visualization
                # Draw power generation metrics
                draw_bar_chart(frame, data['power_generation'],
                             10, 50, width // 3, height // 3,
                             "Power Generation")
                
                # Draw technical metrics
                draw_bar_chart(frame, data['technical_metrics'],
                             width // 3 + 20, 50, width // 3, height // 3,
                             "Technical Metrics")
                
                # Draw biomechanical metrics
                draw_bar_chart(frame, data['biomechanical_metrics'],
                             2 * width // 3 + 30, 50, width // 3, height // 3,
                             "Biomechanical Metrics")
            
            else:
                # Metadata visualization
                if 'movement_type' in data:
                    cv2.putText(frame, f"Movement: {data['movement_type']}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                if 'category' in data:
                    cv2.putText(frame, f"Category: {data['category']}", (10, 70),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                if 'timestamp' in data:
                    cv2.putText(frame, f"Time: {data['timestamp']}", (10, 110),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Draw progress bar
            bar_width = int(width * 0.8)
            bar_height = 20
            bar_x = int((width - bar_width) / 2)
            bar_y = height - 50
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), -1)
            progress_width = int(bar_width * progress)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        logger.info(f"Successfully created video: {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing {json_path}: {str(e)}")
        raise

def process_directory(input_dir, output_dir):
    """Process all JSON files in a directory."""
    json_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                json_files.append(json_path)
    
    total_files = len(json_files)
    logger.info(f"Found {total_files} JSON files to process")
    
    for i, json_path in enumerate(json_files, 1):
        try:
            # Create output path maintaining directory structure
            rel_path = os.path.relpath(os.path.dirname(json_path), input_dir)
            output_subdir = os.path.join(output_dir, rel_path)
            video_name = os.path.splitext(os.path.basename(json_path))[0] + '.mp4'
            output_path = os.path.join(output_subdir, video_name)
            
            logger.info(f"Processing file {i}/{total_files}: {json_path}")
            create_video_from_json(json_path, output_path)
            
        except Exception as e:
            logger.error(f"Failed to process {json_path}: {str(e)}")
            continue

if __name__ == '__main__':
    input_dir = 'data/organized_samples'
    output_dir = 'data/movement_videos_processed'
    process_directory(input_dir, output_dir) 