
import pandas as pd

def prepare_data(path):
    if str(path).lower().endswith(".csv"):
        df = pd.read_csv(path, encoding="utf-8-sig")
    else:
        df = pd.read_excel(path)

    df.columns = [str(c).strip().lower() for c in df.columns]

    def find(options):
        for x in options:
            if x in df.columns:
                return x
        return None

    invoice = find(["invoice","invoice no","invoice number"])
    customer = find(["customer name","customer"])
    product = find(["product name","item name","product"])
    qty = find(["qty","quantity","product qty"])

    if not all([invoice, customer, product, qty]):
        raise Exception("Required columns not found")

    out = df[[invoice, customer, product, qty]].copy()
    out.columns = ["Invoice","Customer Name","Product Name","Qty"]
    out = out.dropna(subset=["Product Name"])
    out.insert(0,"Serial",range(1,len(out)+1))

    return out
