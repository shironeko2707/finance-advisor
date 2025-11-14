"""
PDF Converter Service for converting Excel files to PDF
"""
import os
import logging
from typing import Optional, Tuple
from openpyxl import load_workbook
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

class PDFConverterService:
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls']

    def is_convertible_to_pdf(self, file_path: str) -> bool:
        """
        Check if the file format can be converted to PDF
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats

    async def convert_to_pdf(self, source_file_path: str, output_dir: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Convert an Excel file to PDF format

        Args:
            source_file_path: Path to the Excel file
            output_dir: Directory to save the converted PDF (optional)

        Returns:
            Tuple of (success, pdf_file_path, error_message)
        """
        try:
            if not os.path.exists(source_file_path):
                return False, "", "Source file not found"

            _, ext = os.path.splitext(source_file_path.lower())

            if ext not in ['.xlsx', '.xls']:
                return False, "", f"File format {ext} is not supported. Only Excel files (.xlsx, .xls) can be converted to PDF"

            # Determine output directory
            if output_dir is None:
                output_dir = os.path.dirname(source_file_path)

            # Generate PDF filename
            base_name = os.path.splitext(os.path.basename(source_file_path))[0]
            pdf_filename = f"{base_name}_converted.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)

            # Convert Excel to PDF
            success, error = await self._convert_excel_to_pdf(source_file_path, pdf_path)

            if success:
                return True, pdf_path, None
            else:
                return False, "", error

        except Exception as e:
            logger.error(f"Error converting {source_file_path} to PDF: {str(e)}")
            return False, "", f"Conversion failed: {str(e)}"

    async def _convert_excel_to_pdf(self, excel_path: str, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        Convert Excel file to PDF with formatted tables
        """
        try:
            # Load workbook
            workbook = load_workbook(excel_path, data_only=True)

            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                  leftMargin=0.5*inch, rightMargin=0.5*inch,
                                  topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()

            # Title style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=1  # Center alignment
            )

            # Add title
            story.append(Paragraph(f"Report: {os.path.basename(excel_path)}", title_style))
            story.append(Spacer(1, 12))

            # Process each worksheet
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]

                # Add sheet title
                sheet_title_style = ParagraphStyle(
                    'SheetTitle',
                    parent=styles['Heading2'],
                    fontSize=14,
                    spaceAfter=10
                )
                story.append(Paragraph(f"Sheet: {sheet_name}", sheet_title_style))

                # Get data from worksheet
                data = []
                max_row = min(worksheet.max_row, 200)  # Limit to first 200 rows
                max_col = min(worksheet.max_column, 15)  # Limit to first 15 columns

                # Check if sheet has data
                has_data = False
                for row in worksheet.iter_rows(min_row=1, max_row=max_row,
                                             min_col=1, max_col=max_col, values_only=True):
                    # Convert None values to empty strings and limit cell content
                    row_data = []
                    row_has_content = False
                    for cell in row:
                        if cell is None:
                            row_data.append("")
                        else:
                            # Convert to string and limit length
                            cell_str = str(cell)
                            if len(cell_str) > 50:
                                cell_str = cell_str[:47] + "..."
                            row_data.append(cell_str)
                            row_has_content = True

                    if row_has_content:
                        data.append(row_data)
                        has_data = True

                if has_data and data:
                    # Create table with dynamic column widths
                    table = Table(data)

                    # Apply table styling
                    table_style = [
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]

                    # Add alternating row colors
                    for i in range(1, len(data)):
                        if i % 2 == 0:
                            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))

                    table.setStyle(TableStyle(table_style))
                    story.append(table)
                    story.append(Spacer(1, 20))
                else:
                    story.append(Paragraph("No data found in this sheet", styles['Normal']))
                    story.append(Spacer(1, 10))

            # Build PDF
            doc.build(story)
            return True, None

        except Exception as e:
            logger.error(f"Error converting Excel to PDF: {str(e)}")
            return False, str(e)
