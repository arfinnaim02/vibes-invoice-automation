"""Regression tests for the import contract used by both existing PDF renderers."""
import pandas as pd
import pytest
from modules.sales_cleaner import prepare_data


def test_amar_solution_report_with_title_rows_continuations_and_footer(tmp_path):
    path = tmp_path / "DetailSaleReport.xlsx"
    source = [
        ["Detail Sale Report", None, None, None],
        ["Generated on 07-Nov-2026", None, None, None],
        [None, None, None, None],
        ["Invoice No", "Customer Name", "Product Name", "Selling Qty"],
        [20264423717, "Rafia Tanni", "Polo ( XL - Black ) 91314639", 1],
        [None, None, "Polo ( XL - White ) 91314648", 2],
        [20264423701, "Farzad Bhuiyan", "Hoodie ( L - Beige ) 86589455", 1],
        ["Total", None, None, 4],
    ]
    pd.DataFrame(source).to_excel(path, index=False, header=False)
    actual = prepare_data(path)
    assert list(actual.columns) == ["Serial", "Invoice", "Customer Name", "Product Name", "Qty"]
    assert actual["Invoice"].tolist() == ["20264423717", "20264423717", "20264423701"]
    assert actual["Customer Name"].tolist() == ["Rafia Tanni", "Rafia Tanni", "Farzad Bhuiyan"]
    assert actual["Qty"].tolist() == [1, 2, 1]
    assert actual["Serial"].tolist() == [1, 2, 3]


def test_legacy_csv_still_works(tmp_path):
    path = tmp_path / "sales.csv"
    path.write_text(
        "Invoice,Customer Name,Product Name,Qty\n"
        "V-1,Customer A,Regular Fit - Black - M,2\n",
        encoding="utf-8-sig",
    )
    data = prepare_data(path)
    assert data.iloc[0]["Invoice"] == "V-1"
    assert data.iloc[0]["Qty"] == 2


def test_invalid_quantity_fails_instead_of_generating_wrong_pdf(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "Invoice,Customer Name,Product Name,Selling Qty\n"
        "V-1,Customer A,Polo,not a number\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid or negative"):
        prepare_data(path)


def test_no_product_lines_fails(tmp_path):
    path = tmp_path / "total_only.csv"
    path.write_text(
        "Invoice,Customer Name,Product Name,Selling Qty\n"
        "Total,,,15\n", encoding="utf-8",
    )
    with pytest.raises(ValueError, match="No product lines"):
        prepare_data(path)
