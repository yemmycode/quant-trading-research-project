
from io import BytesIO
from datetime import datetime

import pandas as pd


def generate_excel_strategy_report(
    summary,
    data,
    trade_log,
    strategy_settings
):
    """
    Generate an Excel strategy report in memory.

    Sheets included:
    - Strategy Settings
    - Performance Summary
    - Trade Log
    - Backtest Data
    - Risk Disclaimer
    """

    output = BytesIO()

    summary_df = summary.copy()
    data_df = data.copy()
    trade_log_df = trade_log.copy()

    # Convert index to column if the data index is a date
    if data_df.index.name is None:
        data_df.index.name = "Date"

    data_df = data_df.reset_index()

    # Round numeric columns for clean reporting
    for df in [summary_df, data_df, trade_log_df]:
        if not df.empty:
            numeric_columns = df.select_dtypes(include="number").columns
            df[numeric_columns] = df[numeric_columns].round(4)

    settings_df = pd.DataFrame(
        list(strategy_settings.items()),
        columns=["Setting", "Value"]
    )

    disclaimer_df = pd.DataFrame({
        "Risk Disclaimer": [
            "This report is for educational and research purposes only.",
            "Backtested results do not guarantee future performance.",
            "No live trades are placed by this report.",
            "Trading involves risk, including possible loss of capital.",
            "This report should not be treated as financial advice."
        ]
    })

    generated_df = pd.DataFrame({
        "Report Information": [
            f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Project: Quant Trading Research Dashboard",
            "Mode: Backtesting / Research"
        ]
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        generated_df.to_excel(writer, sheet_name="Report Info", index=False)
        settings_df.to_excel(writer, sheet_name="Strategy Settings", index=False)
        summary_df.to_excel(writer, sheet_name="Performance Summary", index=False)

        if trade_log_df.empty:
            empty_trade_df = pd.DataFrame({
                "Message": ["No completed trades found for this strategy setup."]
            })
            empty_trade_df.to_excel(writer, sheet_name="Trade Log", index=False)
        else:
            trade_log_df.to_excel(writer, sheet_name="Trade Log", index=False)

        data_df.to_excel(writer, sheet_name="Backtest Data", index=False)
        disclaimer_df.to_excel(writer, sheet_name="Risk Disclaimer", index=False)

        # Apply basic formatting
        workbook = writer.book

        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]

            # Freeze top row
            worksheet.freeze_panes = "A2"

            # Adjust column widths
            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    try:
                        cell_value = str(cell.value)
                        if len(cell_value) > max_length:
                            max_length = len(cell_value)
                    except Exception:
                        pass

                adjusted_width = min(max_length + 2, 40)
                worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)

    return output
