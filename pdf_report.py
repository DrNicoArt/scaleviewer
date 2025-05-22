import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus import PageBreak
from reportlab.lib.units import inch
from PyQt5.QtCore import QTemporaryFile, QTemporaryDir
from PyQt5.QtGui import QPixmap

from utils.constants import APP_NAME, APP_VERSION


class PDFReportGenerator:
    """
    Class for generating PDF reports with screenshots, object data and analysis.
    """
    
    def __init__(self):
        # Create a temporary directory for storing images
        self.temp_dir = QTemporaryDir()
        if not self.temp_dir.isValid():
            raise Exception("Could not create temporary directory for report generation")
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        
        # Create custom styles
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading1',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='ScaleHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkgreen
        ))
        
        self.styles.add(ParagraphStyle(
            name='ObjectName',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            textColor=colors.gray,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='TimeCrystalCandidate',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, filename, objects, screenshots=None):
        """
        Generate a PDF report with the provided objects and screenshots.
        
        Args:
            filename: Path where to save the PDF report
            objects: List of objects to include in the report
            screenshots: Dictionary of visualization screenshots (key: view_name, value: QPixmap)
        """
        # Create the document
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Container for report elements
        elements = []
        
        # Add report header
        self._add_header(elements)
        
        # Add date and summary
        elements.append(Paragraph(
            f"Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            self.styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph(
            f"This report contains data for {len(objects)} objects across multiple scales.",
            self.styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        # Add visualization screenshots if provided
        if screenshots:
            self._add_screenshots(elements, screenshots)
        
        # Group objects by scale for better organization
        objects_by_scale = self._group_by_scale(objects)
        
        # Process each scale group
        for scale, scale_objects in objects_by_scale.items():
            elements.append(Paragraph(f"{scale.capitalize()} Scale", self.styles["ScaleHeading"]))
            
            # Process objects in this scale
            for obj in scale_objects:
                self._add_object_section(elements, obj)
            
            elements.append(Spacer(1, 0.2 * inch))
        
        # Add interpretation and analysis
        self._add_analysis_section(elements, objects)
        
        # Build the PDF
        doc.build(elements)
    
    def _add_header(self, elements):
        """Add the report header."""
        elements.append(Paragraph(f"{APP_NAME} - Data Analysis Report", self.styles["Title"]))
        elements.append(Paragraph(f"Version {APP_VERSION}", self.styles["Normal"]))
        elements.append(Spacer(1, 0.25 * inch))
    
    def _add_screenshots(self, elements, screenshots):
        """Add visualization screenshots to the report."""
        elements.append(Paragraph("Visualizations", self.styles["Heading1"]))
        elements.append(Spacer(1, 0.1 * inch))
        
        if not screenshots:
            elements.append(Paragraph("No screenshots available for this report.", self.styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(PageBreak())
            return
            
        try:
            # Save screenshots to temporary files
            image_paths = {}
            for view_name, pixmap in screenshots.items():
                if pixmap and not pixmap.isNull():
                    try:
                        # Utwórz folder tymczasowy jeśli nie istnieje
                        temp_dir_path = self.temp_dir.path()
                        if not os.path.exists(temp_dir_path):
                            os.makedirs(temp_dir_path)
                            
                        # Create a temporary file for the image
                        image_path = f"{temp_dir_path}/cosmic_analyzer_{view_name.replace(' ', '_')}.png"
                        
                        # Save the pixmap to the temporary file
                        if pixmap.save(image_path, "PNG"):
                            image_paths[view_name] = image_path
                        else:
                            print(f"Failed to save screenshot for {view_name}")
                    except Exception as e:
                        print(f"Error saving screenshot: {e}")
            
            # Add screenshots to the report
            for view_name, image_path in image_paths.items():
                try:
                    # Add view name as heading
                    elements.append(Paragraph(f"{view_name.title()} View", self.styles["Heading2"]))
                    
                    # Add the image if file exists
                    if os.path.exists(image_path):
                        try:
                            img = Image(image_path, width=6 * inch, height=4 * inch)
                            elements.append(img)
                            
                            # Add caption
                            elements.append(Paragraph(f"Screenshot of {view_name} visualization", self.styles["Caption"]))
                        except Exception as e:
                            print(f"Error adding image to report: {e}")
                            elements.append(Paragraph(f"Error adding image: {str(e)}", self.styles["Normal"]))
                    else:
                        elements.append(Paragraph(f"Screenshot image not available", self.styles["Normal"]))
                    
                    elements.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    print(f"Error processing screenshot {view_name}: {e}")
        except Exception as e:
            print(f"Error in _add_screenshots: {e}")
            elements.append(Paragraph(f"Error processing screenshots: {str(e)}", self.styles["Normal"]))
        
        elements.append(PageBreak())
    
    def _add_object_section(self, elements, obj):
        """Add a section for an individual object."""
        # Add object name
        elements.append(Paragraph(obj.get("name", "Unknown Object"), self.styles["ObjectName"]))
        
        # Create a table for object data
        data = [["ID:", obj.get("id", "")]]
        obj_data = obj.get("data", {})
        
        # Add all data fields
        for key, value in sorted(obj_data.items()):
            data.append([f"{key}:", str(value)])
        
        # Create and style the table
        table = Table(data, colWidths=[1.5 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.1 * inch))
    
    def _add_analysis_section(self, elements, objects):
        """Add analysis and interpretation section."""
        elements.append(PageBreak())
        elements.append(Paragraph("Analysis and Interpretation", self.styles["Heading1"]))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Add time crystal candidate analysis
        elements.append(Paragraph("Time Crystal Candidate Analysis", self.styles["Heading2"]))
        
        # Identify potential time crystal candidates
        from analysis.crystal_detection import CrystalDetector
        detector = CrystalDetector()
        candidates = detector.find_candidates(objects)
        
        if candidates:
            # Add explanation of what time crystals are
            elements.append(Paragraph(
                "Time crystals are phases of matter that break time-translation symmetry. Unlike "
                "conventional crystals that exhibit spatial periodicity, time crystals exhibit "
                "temporal periodicity and can maintain oscillations without energy input.",
                self.styles["Normal"]))
            
            elements.append(Spacer(1, 0.1 * inch))
            
            # List candidates with their scores
            elements.append(Paragraph("Potential candidates:", self.styles["Normal"]))
            
            for candidate in candidates:
                obj = candidate["object"]
                score = candidate["score"]
                explanation = candidate["explanation"]
                
                elements.append(Paragraph(
                    f"• <b>{obj.get('name', 'Unknown')}</b> (Score: {score}/10)",
                    self.styles["TimeCrystalCandidate"]))
                
                elements.append(Paragraph(explanation, self.styles["Normal"]))
        else:
            elements.append(Paragraph(
                "No strong time crystal candidates were identified in the provided data set.",
                self.styles["Normal"]))
        
        elements.append(Spacer(1, 0.2 * inch))
        
        # Add cross-scale comparison
        elements.append(Paragraph("Cross-Scale Observations", self.styles["Heading2"]))
        
        # Add some general observations about the data across scales
        scale_counts = self._count_objects_by_scale(objects)
        
        elements.append(Paragraph(
            "This dataset contains objects spanning multiple scales of existence. "
            "Below is a summary of the distribution across scales:",
            self.styles["Normal"]))
        
        # Create a table for scale distribution
        scale_data = [["Scale", "Count"]]
        
        for scale, count in scale_counts.items():
            scale_data.append([scale.capitalize(), str(count)])
        
        # Create and style the table
        scale_table = Table(scale_data, colWidths=[2 * inch, 1 * inch])
        scale_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(scale_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Closing notes
        elements.append(Paragraph(
            "The diversity of objects across these scales demonstrates the vastly different "
            "physical laws and properties governing systems from the quantum to the cosmic scale. "
            "While these scales operate under different regimes, many patterns and similarities "
            "can be observed in their organization and behavior.",
            self.styles["Normal"]))
    
    def _group_by_scale(self, objects):
        """Group objects by scale for organized presentation."""
        grouped = {}
        
        for obj in objects:
            scale = obj.get("scale", "unknown")
            
            if scale not in grouped:
                grouped[scale] = []
            
            grouped[scale].append(obj)
        
        return grouped
    
    def _count_objects_by_scale(self, objects):
        """Count objects by scale."""
        counts = {}
        
        for obj in objects:
            scale = obj.get("scale", "unknown")
            
            if scale not in counts:
                counts[scale] = 0
            
            counts[scale] += 1
        
        return counts
