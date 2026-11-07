"""Normalize VIBES legacy exports and Amar Solution Detail Sale Reports.

The PDF renderers intentionally receive the unchanged five-column contract:
Serial, Invoice, Customer Name, Product Name, Qty.
"""
from pathlib import Path
import pandas as pd

ALIASES = {
    "invoice": ("invoice", "invoice no", "invoice number", "invoice id"),
    "customer": ("customer name", "customer"),
    "product": ("product name", "item name", "product"),
    "qty": ("selling qty", "qty", "quantity", "product qty"),
}
FOOTERS = {"total", "grand total", "subtotal", "summary"}


def _normalize(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().casefold().split())


def _read_raw(path):
    extension = Path(path).suffix.lower()
    if extension == ".csv":
        try:
            return pd.read_csv(path, header=None, dtype=object, encoding="utf-8-sig")
        except UnicodeDecodeError:
            return pd.read_csv(path, header=None, dtype=object, encoding="cp1252")
    if extension in (".xlsx", ".xls"):
        return pd.read_excel(path, header=None, dtype=object)
    raise ValueError("Please upload a CSV, XLSX or XLS sales report.")


def _find_header(raw):
    # Amar Solution exports include a multi-row report title above the real headings.
    for row_index in range(min(len(raw), 40)):
        values = {_normalize(value): index for index, value in enumerate(raw.iloc[row_index])
                  if _normalize(value)}
        columns = {field: next((values[key] for key in choices if key in values), None)
                   for field, choices in ALIASES.items()}
        if all(index is not None for index in columns.values()):
            return row_index, columns
    raise ValueError(
        "Sales columns not found. Expected Invoice, Customer Name, Product Name "
        "and Selling Qty (or Qty). Check that you uploaded a Detail Sale Report."
    )


def _invoice_text(value):
    if isinstance(value, (int, float)) and float(value).is_integer():
        return str(int(value))
    result = str(value).strip()
    if result.endswith(".0") and result[:-2].isdigit():
        return result[:-2]
    return result


def prepare_data(path):
    raw = _read_raw(path)
    if raw.empty:
        raise ValueError("The uploaded sales report is empty.")

    header_row, columns = _find_header(raw)
    rows = raw.iloc[header_row + 1:].reset_index(drop=True)
    if rows.empty:
        raise ValueError("No sales data found after the header.")

    invoice = rows.iloc[:, columns["invoice"]]
    customer = rows.iloc[:, columns["customer"]]
    product = rows.iloc[:, columns["product"]]
    quantity = rows.iloc[:, columns["qty"]]

    # Continuation product lines in Amar Solution have empty invoice/customer cells.
    # Do not mistake the final Total or summary row for a sale.
    invoice_label = invoice.map(_normalize)
    product_label = product.map(_normalize)
    is_footer = invoice_label.isin(FOOTERS) | product_label.isin(FOOTERS)
    is_product = product_label.ne("") & ~is_footer
    selected = rows.index[is_product]

    if len(selected) == 0:
        raise ValueError("No product lines found in the sales report.")

    invoice_filled = invoice.astype(object).ffill()
    customer_filled = customer.astype(object).ffill()
    result = pd.DataFrame({
        "Invoice": invoice_filled.loc[selected].to_numpy(),
        "Customer Name": customer_filled.loc[selected].to_numpy(),
        "Product Name": product.loc[selected].to_numpy(),
        "Qty": pd.to_numeric(quantity.loc[selected], errors="coerce").to_numpy(),
    })

    if result["Invoice"].isna().any() or result["Customer Name"].isna().any():
        raise ValueError("A product line is missing its invoice or customer.")
    if result["Qty"].isna().any() or (result["Qty"] < 0).any():
        raise ValueError("A product line has an invalid or negative Selling Qty.")
    if (result["Qty"] % 1 != 0).any():
        raise ValueError("Selling Qty must be a whole number for these PDFs.")

    result["Qty"] = result["Qty"].astype(int)
    result = result.loc[result["Qty"] > 0].reset_index(drop=True)
    if result.empty:
        raise ValueError("No sold items with positive quantities were found.")

    result["Invoice"] = result["Invoice"].map(_invoice_text)
    result["Customer Name"] = result["Customer Name"].astype(str).str.strip()
    result["Product Name"] = result["Product Name"].astype(str).str.strip()
    result.insert(0, "Serial", range(1, len(result) + 1))
    return result
