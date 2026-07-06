import pandas as pd
import json
import re
from collections import defaultdict
from tabulate import tabulate  

def extract_lookup_values_with_table_format(excel_file):
    xls = pd.ExcelFile(excel_file)

    lookup_data = defaultdict(lambda: defaultdict(lambda: {"date": None, "rows": []}))

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Identify Request and Request Url
        request_col = next((col for col in df.columns if col.strip().lower() == "request"), None)
        request_url_col = next((col for col in df.columns if col.strip().lower() == "request url"), None)

        if not request_col or not request_url_col:
            print(f"❌ Missing 'Request' or 'Request Url' in {sheet_name}, skipping...")
            continue

        for idx, row in df.iterrows():
            request_data = row.get(request_col)
            request_url = row.get(request_url_col)

            if not isinstance(request_data, str):
                continue

            try:
                json_data = json.loads(request_data)

                lookup_value = json_data.get("lookupValue")
                if not lookup_value:
                    continue

                # Determine sheet name
                target_sheet = json_data.get("sheetId")
                if not target_sheet and isinstance(request_url, str):
                    url_match = re.search(r'values/([^:]+):', request_url)
                    if url_match:
                        target_sheet = url_match.group(1).strip()
                    else:
                        target_sheet = "Unknown"

                # Extract row data and date
                date = None
                row_data = []

                if "row" in json_data:
                    row_data = json_data["row"]
                    if len(row_data) > 0 and re.match(r"\d{4}-\d{2}-\d{2}", str(row_data[0])):
                        date = row_data[0]

                elif "values" in json_data:
                    for val in json_data["values"]:
                        if not val:
                            continue
                        row_data = val
                        date_candidate = str(val[0])
                        if re.match(r"\d{4}-\d{2}-\d{2}", date_candidate):
                            date = date_candidate
                        lookup_value = val[-1]  # override if needed

                if lookup_value and row_data:
                    if not lookup_data[lookup_value][target_sheet]["date"] and date:
                        lookup_data[lookup_value][target_sheet]["date"] = date
                    lookup_data[lookup_value][target_sheet]["rows"].append(row_data)

            except json.JSONDecodeError:
                continue

    # ✅ Print the final table output
    if not lookup_data:
        print("⚠️ No lookup values found.")
        return

    for lookup_value, sheets in lookup_data.items():
        for sheet, data in sheets.items():
            date_str = data["date"] or "No Date Found"
            print(f"\n📄 Sheet: {sheet} | 🔍 LookupValue: {lookup_value} | 📅 Date: {date_str}")

            all_rows = data["rows"]
            if not all_rows:
                print("⚠️ No data rows.")
                continue

            # Normalize row lengths
            max_cols = max(len(row) for row in all_rows)
            normalized_rows = [
                row + [""] * (max_cols - len(row)) for row in all_rows
            ]

            # Prepare header and formatted table
            headers = [f"Column {i+1}" for i in range(max_cols)]
            indexed_rows = [[f"Row {i+1}"] + r for i, r in enumerate(normalized_rows)]

            table = tabulate(indexed_rows, headers=["Row\\Col"] + headers, tablefmt="fancy_grid")
            print(table)

# Usage
file_path = "excel.xlsx"
extract_lookup_values_with_table_format(file_path)
