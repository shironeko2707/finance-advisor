"""
Service for integrating Qlib predictions into generated reports.

This service provides functionality to enhance generated reports
with prediction data from the Qlib service.
"""
import os
import logging
from typing import Optional, Dict, Any
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from sqlalchemy.orm import Session
from .prediction_repository import PredictionRepository
from .prediction_formatter import PredictionFormatter
from module.report.GeneratedReportModel import GeneratedReport

logger = logging.getLogger(__name__)


class PredictionReportService:
    """Service for adding prediction data to generated reports."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = PredictionRepository(db)
        self.formatter = PredictionFormatter()

    def get_prediction_data_for_report(self, report_id: int) -> Optional[Dict[str, Any]]:
        """
        Get formatted prediction data for a report.

        Args:
            report_id: Generated report ID

        Returns:
            Formatted prediction data or None if not found
        """
        try:
            # Get prediction request by report ID
            prediction_request = self.repository.get_prediction_request_by_report_id(report_id)

            if not prediction_request:
                logger.info(f"No predictions found for report ID: {report_id}")
                return None

            # Check if prediction is complete
            if prediction_request.status != "success":
                logger.warning(
                    f"Predictions for report {report_id} are not complete. "
                    f"Status: {prediction_request.status}"
                )
                return None

            # Format prediction data
            formatted_data = self.formatter.format_predictions_for_json(prediction_request)

            return formatted_data

        except Exception as e:
            logger.error(f"Error getting prediction data for report {report_id}: {e}", exc_info=True)
            return None

    def enhance_excel_report_with_predictions(
        self,
        report_file_path: str,
        report_id: int,
        output_path: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Enhance an Excel report by adding prediction data.

        Args:
            report_file_path: Path to the existing Excel report
            report_id: Report ID to get predictions for
            output_path: Optional output path (defaults to original file)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get prediction data
            prediction_data = self.get_prediction_data_for_report(report_id)

            if not prediction_data:
                return False, "No prediction data available for this report"

            # Check if file exists
            if not os.path.exists(report_file_path):
                return False, f"Report file not found: {report_file_path}"

            # Check if it's an Excel file
            if not report_file_path.endswith(('.xlsx', '.xls')):
                return False, "Only Excel files can be enhanced with predictions"

            # Load workbook
            try:
                workbook = load_workbook(report_file_path)
            except Exception as e:
                return False, f"Failed to load Excel file: {str(e)}"

            # Add prediction sheets
            self._add_market_regime_sheet(workbook, prediction_data)
            self._add_stock_predictions_sheet(workbook, prediction_data)
            self._add_recommendations_sheet(workbook, prediction_data)
            self._add_portfolio_analysis_sheet(workbook, prediction_data)

            # Save enhanced workbook
            output_file = output_path or report_file_path
            workbook.save(output_file)

            logger.info(f"Successfully enhanced report {report_id} with predictions")
            return True, f"Report enhanced with {prediction_data['summary']['stock_count']} stock predictions"

        except Exception as e:
            logger.error(f"Error enhancing report with predictions: {e}", exc_info=True)
            return False, f"Error: {str(e)}"

    def _add_market_regime_sheet(self, workbook, prediction_data: Dict[str, Any]):
        """Add market regime analysis sheet."""
        if not prediction_data.get("market_regime"):
            return

        # Create or get sheet
        if "Market Regime" in workbook.sheetnames:
            ws = workbook["Market Regime"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = workbook.create_sheet("Market Regime")

        market_regime = prediction_data["market_regime"]

        # Header
        ws["A1"] = "Market Regime Analysis"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:B1")

        # Data
        row = 3
        for key, value in market_regime.items():
            ws[f"A{row}"] = key
            ws[f"B{row}"] = value
            ws[f"A{row}"].font = Font(bold=True)
            row += 1

        # Metadata
        if "summary" in prediction_data:
            ws[f"A{row+1}"] = "Generated At"
            ws[f"B{row+1}"] = prediction_data["summary"]["metadata"]["generated_at"]
            ws[f"A{row+1}"].font = Font(bold=True)

        # Adjust column widths
        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 50

    def _add_stock_predictions_sheet(self, workbook, prediction_data: Dict[str, Any]):
        """Add stock predictions sheet."""
        if not prediction_data.get("stock_predictions"):
            return

        # Create or get sheet
        if "Stock Predictions" in workbook.sheetnames:
            ws = workbook["Stock Predictions"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = workbook.create_sheet("Stock Predictions")

        stock_predictions = prediction_data["stock_predictions"]

        # Header
        ws["A1"] = "Stock Price Forecasts"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:J1")

        # Column headers
        headers = list(stock_predictions[0].keys()) if stock_predictions else []
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        # Data rows
        for row_idx, stock in enumerate(stock_predictions, start=4):
            for col_idx, (key, value) in enumerate(stock.items(), start=1):
                ws.cell(row=row_idx, column=col_idx, value=value)

        # Auto-adjust column widths
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15

    def _add_recommendations_sheet(self, workbook, prediction_data: Dict[str, Any]):
        """Add recommendations sheet."""
        if not prediction_data.get("recommendations"):
            return

        # Create or get sheet
        if "Recommendations" in workbook.sheetnames:
            ws = workbook["Recommendations"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = workbook.create_sheet("Recommendations")

        recommendations = prediction_data["recommendations"]

        # Header
        ws["A1"] = "Investment Recommendations"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:J1")

        # Column headers
        headers = list(recommendations[0].keys()) if recommendations else []
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        # Data rows with color coding
        for row_idx, rec in enumerate(recommendations, start=4):
            for col_idx, (key, value) in enumerate(rec.items(), start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)

                # Color code recommendations
                if key == "Recommendation":
                    if "BUY" in value.upper():
                        cell.fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                    elif "SELL" in value.upper():
                        cell.fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
                    elif "HOLD" in value.upper():
                        cell.fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")

        # Auto-adjust column widths
        for col in range(1, len(headers) + 1):
            column_letter = get_column_letter(col)
            if col == len(headers):  # Rationale column
                ws.column_dimensions[column_letter].width = 50
            else:
                ws.column_dimensions[column_letter].width = 15

    def _add_portfolio_analysis_sheet(self, workbook, prediction_data: Dict[str, Any]):
        """Add portfolio analysis sheet."""
        if not prediction_data.get("portfolio_analysis"):
            return

        # Create or get sheet
        if "Portfolio Analysis" in workbook.sheetnames:
            ws = workbook["Portfolio Analysis"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = workbook.create_sheet("Portfolio Analysis")

        portfolio_analysis = prediction_data["portfolio_analysis"]

        # Header
        ws["A1"] = "Portfolio Risk & Performance Analysis"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:B1")

        # Risk Metrics Section
        ws["A3"] = "Risk Metrics"
        ws["A3"].font = Font(bold=True, size=12)
        ws["A3"].fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
        ws.merge_cells("A3:B3")

        row = 4
        risk_metrics = [
            "Risk Level", "Sharpe Ratio", "Max Drawdown", "Volatility",
            "Value at Risk (95%)", "Beta", "Alpha", "Diversification Score"
        ]

        for metric in risk_metrics:
            if metric in portfolio_analysis:
                ws[f"A{row}"] = metric
                ws[f"B{row}"] = portfolio_analysis[metric]
                ws[f"A{row}"].font = Font(bold=True)
                row += 1

        # Performance Forecasts Section
        row += 1
        ws[f"A{row}"] = "Performance Forecasts"
        ws[f"A{row}"].font = Font(bold=True, size=12)
        ws[f"A{row}"].fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
        ws.merge_cells(f"A{row}:B{row}")

        row += 1
        performance_metrics = [
            "Expected Return (1-Day)", "Expected Return (5-Day)", "Expected Return (30-Day)"
        ]

        for metric in performance_metrics:
            if metric in portfolio_analysis:
                ws[f"A{row}"] = metric
                ws[f"B{row}"] = portfolio_analysis[metric]
                ws[f"A{row}"].font = Font(bold=True)

                # Color code based on value
                value_str = portfolio_analysis[metric]
                if "%" in value_str:
                    try:
                        value = float(value_str.replace("%", ""))
                        if value > 0:
                            ws[f"B{row}"].fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                        elif value < 0:
                            ws[f"B{row}"].fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
                    except:
                        pass

                row += 1

        # Adjust column widths
        ws.column_dimensions["A"].width = 30
        ws.column_dimensions["B"].width = 20
