from typing import List, Optional

from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Border, Side

from .agent import FillInValues


def _write_main_data(ws: Worksheet, fill_in_values: List[FillInValues], header_font, header_fill, border, get_confidence_fill):
    """Write the main data table to the worksheet.

    Args:
        ws: The worksheet object.
        fill_in_values: A list of FillInValues objects.
        header_font, header_fill, border, get_confidence_fill: Formatting helpers.
    """
    # Flatten all FillInValue objects from all FillInValues in the list
    all_fill_values = []
    for fill_group in fill_in_values:
        all_fill_values.extend(fill_group.values)

    # Determine the table dimensions
    max_row = max((fv.row_index for fv in all_fill_values), default=0)
    columns = sorted(set(fv.column_indice for fv in all_fill_values))

    # Write headers
    ws.cell(row=1, column=1, value="Row").font = header_font
    ws.cell(row=1, column=1).fill = header_fill
    ws.cell(row=1, column=1).border = border

    for col_idx, col_name in enumerate(columns, start=2):
        ws.cell(row=1, column=col_idx, value=col_name).font = header_font
        ws.cell(row=1, column=col_idx).fill = header_fill
        ws.cell(row=1, column=col_idx).border = border

    # Create a mapping for quick lookup
    value_map = {(fv.row_index, fv.column_indice): fv for fv in all_fill_values}

    # Write data rows
    for row_idx in range(1, max_row + 1):
        # Write row index
        ws.cell(row=row_idx + 1, column=1, value=row_idx).border = border

        # Write data for each column
        for col_idx, col_name in enumerate(columns, start=2):
            cell = ws.cell(row=row_idx + 1, column=col_idx)
            cell.border = border

            if (row_idx, col_name) in value_map:
                fill_value = value_map[(row_idx, col_name)]
                cell.value = fill_value.result.final_result.value

                # Apply confidence-based coloring
                confidence = fill_value.result.final_result.score
                confidence_fill = get_confidence_fill(confidence)
                if confidence_fill:
                    cell.fill = confidence_fill

                # Add comment with metadata
                comment_text = (
                    f"Source: {fill_value.result.final_result.file_name}\n"
                    f"Page: {fill_value.result.final_result.page}\n"
                    f"Score: {confidence}\n"
                    f"Reason: {fill_value.result.reason}\n"
                    f"Candidates: {len(fill_value.result.candidates)}"
                )
                cell.comment = Comment(comment_text, "System")

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width


def write_fill_in_values_to_worksheet(
    fill_in_values: List[FillInValues],
    ws: Worksheet,
    overwrite: bool = False,
    color_code_confidence: bool = True
) -> None:
    """
    Update the given Excel worksheet with a list of FillInValues data.

    Args:
        fill_in_values: The data to write to the worksheet
        ws: The worksheet object to update
        overwrite: If True, overwrite existing values in target cells
        color_code_confidence: If True, color-code cells based on confidence scores
    """
    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Confidence color mapping function
    def get_confidence_fill(confidence: Optional[float]) -> Optional[PatternFill]:
        if not color_code_confidence or confidence is None:
            return None
        if confidence >= 0.8:
            return PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Light green
        elif confidence >= 0.6:
            return PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Light yellow
        else:
            return PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Light red

    # Write main data to worksheet
    _write_main_data(ws, fill_in_values, header_font, header_fill, border, get_confidence_fill)
