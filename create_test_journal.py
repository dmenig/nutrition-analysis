import openpyxl


def create_test_journal(filename="test_journal.xlsx"):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Journal"

    # Headers
    headers = [
        "Date",
        "recorded food",
        "ingested weight",
        "sport",
        "Extra Column 1",
        "Extra Column 2",
    ]
    sheet.append(headers)

    # Data with formulas
    sheet.append(["2024-01-01", "Apple", 150, "Running", "Misc1", "MiscA"])
    sheet.append(["2024-01-02", "Banana", "=B2*2", "Swimming", "Misc2", "MiscB"])
    sheet.append(
        ["2024-01-03", "Orange", 200, "=C2+C3", "Misc3", "MiscC"]
    )  # C3 will be "=B2*2"
    sheet.append(
        ["2024-01-04", "Milk", "=SUM(C2:C4)", "Cycling", "Misc4", "MiscD"]
    )  # C2, C3, C4 will be formulas

    workbook.save(filename)
    print(f"Created {filename}")


if __name__ == "__main__":
    create_test_journal()
