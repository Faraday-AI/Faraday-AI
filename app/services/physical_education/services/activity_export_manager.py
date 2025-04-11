from typing import Dict, List, Optional, Union
import os
import json
import pandas as pd
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches
from docx import Document
import csv
import openpyxl
from io import BytesIO
import base64

class ActivityExportManager:
    def __init__(self):
        self.export_formats = [
            'png', 'svg', 'pdf', 'html', 'json',
            'pptx', 'docx', 'xlsx', 'csv', 'latex', 'md'
        ]
        
        # Configure export settings
        self.export_settings = {
            'default_format': 'png',
            'image_quality': 300,
            'compression_level': 9,
            'max_file_size': 10 * 1024 * 1024  # 10MB
        }
        
        # Set up export directories
        self.export_dirs = {
            'visualizations': 'exports/visualizations',
            'reports': 'exports/reports',
            'data': 'exports/data'
        }
        
        for dir_path in self.export_dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    async def export_visualization(self, visualization: Dict, format: str, 
                                 student_id: str, **kwargs) -> str:
        """Export visualization in various formats."""
        if format not in self.export_formats:
            raise ValueError(f"Unsupported export format: {format}")
            
        if format == 'pptx':
            return await self._export_to_pptx(visualization, student_id, **kwargs)
        elif format == 'docx':
            return await self._export_to_docx(visualization, student_id, **kwargs)
        elif format == 'xlsx':
            return await self._export_to_excel(visualization, student_id, **kwargs)
        elif format == 'csv':
            return await self._export_to_csv(visualization, student_id, **kwargs)
        elif format == 'latex':
            return await self._export_to_latex(visualization, student_id, **kwargs)
        elif format == 'md':
            return await self._export_to_markdown(visualization, student_id, **kwargs)
        else:
            return await self._export_to_image(visualization, format, student_id, **kwargs)

    async def _export_to_pptx(self, visualization: Dict, student_id: str, **kwargs) -> str:
        """Export visualization to PowerPoint format."""
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        
        # Add title
        title = slide.shapes.title
        title.text = f"Performance Analysis for {student_id}"
        
        # Add content
        content = slide.placeholders[1]
        content.text = visualization.get('description', '')
        
        # Add visualization
        if 'image_path' in visualization:
            slide.shapes.add_picture(
                visualization['image_path'],
                left=Inches(1),
                top=Inches(2),
                width=Inches(8)
            )
        
        # Save presentation
        output_path = os.path.join(self.export_dirs['reports'], 
                                 f"{student_id}/presentation.pptx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        prs.save(output_path)
        
        return output_path

    async def _export_to_docx(self, visualization: Dict, student_id: str, **kwargs) -> str:
        """Export visualization to Word format."""
        doc = Document()
        
        # Add title
        doc.add_heading(f"Performance Analysis for {student_id}", 0)
        
        # Add description
        doc.add_paragraph(visualization.get('description', ''))
        
        # Add metrics
        if 'metrics' in visualization:
            doc.add_heading('Performance Metrics', level=1)
            for metric, value in visualization['metrics'].items():
                doc.add_paragraph(f"{metric}: {value}")
        
        # Add visualization
        if 'image_path' in visualization:
            doc.add_picture(
                visualization['image_path'],
                width=Inches(6)
            )
        
        # Save document
        output_path = os.path.join(self.export_dirs['reports'],
                                 f"{student_id}/report.docx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        
        return output_path

    async def _export_to_excel(self, visualization: Dict, student_id: str, **kwargs) -> str:
        """Export visualization data to Excel format."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Performance Data"
        
        # Add metadata
        ws['A1'] = f"Performance Analysis for {student_id}"
        ws['A2'] = f"Generated on: {datetime.now().isoformat()}"
        
        # Add data
        if 'data' in visualization:
            df = pd.DataFrame(visualization['data'])
            for r_idx, row in enumerate(df.itertuples(), start=4):
                for c_idx, value in enumerate(row[1:], start=1):
                    ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Save workbook
        output_path = os.path.join(self.export_dirs['data'],
                                 f"{student_id}/data.xlsx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        wb.save(output_path)
        
        return output_path

    async def _export_to_csv(self, visualization: Dict, student_id: str, **kwargs) -> str:
        """Export visualization data to CSV format."""
        if 'data' not in visualization:
            raise ValueError("No data available for CSV export")
            
        output_path = os.path.join(self.export_dirs['data'],
                                 f"{student_id}/data.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df = pd.DataFrame(visualization['data'])
        df.to_csv(output_path, index=False)
        
        return output_path

    async def _export_to_latex(self, visualization: Dict, student_id: str, **kwargs) -> str:
        """Export visualization to LaTeX format."""
        latex_content = [
            "\\documentclass{article}",
            "\\usepackage{graphicx}",
            "\\begin{document}",
            f"\\title{{Performance Analysis for {student_id}}}",
            "\\maketitle",
            f"\\section{{Description}}\n{visualization.get('description', '')}",
        ]
        
        if 'metrics' in visualization:
            latex_content.append("\\section{Metrics}")
            latex_content.append("\\begin{itemize}")
            for metric, value in visualization['metrics'].items():
                latex_content.append(f"\\item {metric}: {value}")
            latex_content.append("\\end{itemize}")
        
        if 'image_path' in visualization:
            latex_content.append("\\section{Visualization}")
            latex_content.append(f"\\includegraphics[width=\\textwidth]{{{visualization['image_path']}}}")
        
        latex_content.append("\\end{document}")
        
        output_path = os.path.join(self.export_dirs['reports'],
                                 f"{student_id}/report.tex")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(latex_content))
            
        return output_path

    async def _export_to_markdown(self, visualization: Dict, student_id: str, **kwargs) -> str:
        """Export visualization to Markdown format."""
        markdown_content = [
            f"# Performance Analysis for {student_id}",
            f"*Generated on: {datetime.now().isoformat()}*",
            "",
            "## Description",
            visualization.get('description', ''),
            ""
        ]
        
        if 'metrics' in visualization:
            markdown_content.append("## Metrics")
            for metric, value in visualization['metrics'].items():
                markdown_content.append(f"- **{metric}**: {value}")
            markdown_content.append("")
        
        if 'image_path' in visualization:
            markdown_content.append("## Visualization")
            markdown_content.append(f"![Performance Visualization]({visualization['image_path']})")
        
        output_path = os.path.join(self.export_dirs['reports'],
                                 f"{student_id}/report.md")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(markdown_content))
            
        return output_path

    async def _export_to_image(self, visualization: Dict, format: str, 
                             student_id: str, **kwargs) -> str:
        """Export visualization to image format."""
        if 'image_path' not in visualization:
            raise ValueError("No image available for export")
            
        output_path = os.path.join(self.export_dirs['visualizations'],
                                 f"{student_id}/visualization.{format}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert image to specified format
        # Implementation depends on the image processing library used
        # This is a placeholder for the actual conversion logic
        
        return output_path 