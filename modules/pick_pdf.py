"""VIBES picking report: one row per product category, all sizes/colors combined."""
import re
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

_VARIANT_SUFFIX = re.compile(r"\s*\(\s*[^()]+\s*\)\s*(?:\d{6,})?\s*$")
_OLD_VARIANTS = re.compile(r"\s+-\s+[^-]+\s+-\s+[^-]+\s*$")


def category_from_product(product_name):
    """Strip Amar Solution '( XL - Black ) 91314639' or legacy '- Black - XL'."""
    name = " ".join(str(product_name).split())
    name = _VARIANT_SUFFIX.sub("", name)
    name = _OLD_VARIANTS.sub("", name)
    return name.strip() or str(product_name).strip()


def summarize_picking(df):
    if df.empty:
        raise ValueError("No products available for the picking list.")
    working = df[["Product Name", "Qty"]].copy()
    working["Category"] = working["Product Name"].map(category_from_product)
    working["Qty"] = pd.to_numeric(working["Qty"], errors="raise")
    if working["Qty"].isna().any() or (working["Qty"] < 0).any():
        raise ValueError("Invalid quantity in picking list.")
    return working.groupby("Category", as_index=False, sort=True)["Qty"].sum()


def create_pick_pdf(df, output, report_date):
    summary = summarize_picking(df)
    doc = SimpleDocTemplate(str(output), pagesize=A4,
        rightMargin=35, leftMargin=35, topMargin=30, bottomMargin=30)
    header = Table([["Vibes"], [f"{report_date} Pick"]], colWidths=[430])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#BDD7EE")),
        ("GRID", (0, 0), (-1, -1), .5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 16),
        ("FONTSIZE", (0, 1), (-1, 1), 13),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    data = [["Product Category", "Qty"]]
    data.extend([[row.Category, int(row.Qty)] for row in summary.itertuples(index=False)])
    data.append(["TOTAL", int(summary["Qty"].sum())])
    table = Table(data, repeatRows=1, colWidths=[360, 50])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#BDD7EE")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), .5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FFFF00")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    doc.build([header, Spacer(1, 15), table])
