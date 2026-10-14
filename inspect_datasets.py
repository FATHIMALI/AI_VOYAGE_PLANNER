import os
import pandas as pd

DATA_FOLDER = "data"
OUTPUT_FILE = "dataset_report.txt"

with open(OUTPUT_FILE, "w", encoding="utf-8") as report:

    for root, dirs, files in os.walk(DATA_FOLDER):

        for file in files:

            if file.lower().endswith((".csv", ".xlsx", ".xls")):

                path = os.path.join(root, file)

                report.write("\n" + "=" * 80 + "\n")
                report.write(f"FILE: {path}\n")
                report.write("=" * 80 + "\n")

                try:
                    if file.lower().endswith(".csv"):
                        df = pd.read_csv(path, nrows=5)

                        report.write(f"TYPE: CSV\n")
                        report.write(f"COLUMNS: {list(df.columns)}\n")
                        report.write("\nFIRST 5 ROWS:\n")
                        report.write(df.to_string(index=False))

                    else:
                        excel = pd.ExcelFile(path)

                        report.write(f"TYPE: EXCEL\n")
                        report.write(f"SHEETS: {excel.sheet_names}\n")

                        for sheet in excel.sheet_names:
                            report.write(f"\n--- SHEET: {sheet} ---\n")

                            df = pd.read_excel(
                                path,
                                sheet_name=sheet,
                                nrows=5
                            )

                            report.write(f"COLUMNS: {list(df.columns)}\n")
                            report.write("\nFIRST 5 ROWS:\n")
                            report.write(df.to_string(index=False))

                except Exception as e:
                    report.write(f"ERROR: {e}\n")

print("Done!")
print(f"Report created: {OUTPUT_FILE}")