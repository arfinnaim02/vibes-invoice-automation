import streamlit as st
from pathlib import Path
from datetime import date
import tempfile

from modules.sales_cleaner import prepare_data
from modules.invoice_pdf import create_invoice_pdf
from modules.pick_pdf import create_pick_pdf


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Vibes Automation",
    page_icon="✨",
    layout="centered"
)


# =========================
# CSS
# =========================

st.markdown(
    """
    <style>

    .stApp {
        background:#F6F7FB;
    }

    /* Main container */

    .block-container {
        max-width:720px;
        padding-top:40px;
    }

    /* Header */

    .brand {
        text-align:center;
        margin-bottom:40px;
    }

    .brand h1 {
        font-size:48px;
        font-weight:900;
        letter-spacing:5px;
        color:#111827;
        margin:0;
    }

    .brand p {
        color:#6B7280;
        font-size:18px;
        margin-top:5px;
    }

    /* Cards */

    .card {
        background:white;
        padding:25px;
        border-radius:20px;
        box-shadow:0 10px 30px rgba(0,0,0,0.06);
        margin-bottom:20px;
    }

    .card-title {
        font-size:18px;
        font-weight:700;
        color:#111827;
        margin-bottom:15px;
    }

    /* Buttons */

    .stButton button {
        height:52px;
        border-radius:14px;
        background:#111827;
        color:white;
        font-size:16px;
        font-weight:700;
        border:none;
    }

    .stButton button:hover {
        background:#000;
    }

    /* Uploader */

    [data-testid="stFileUploader"] {
        background:#ffffff;
        padding:15px;
        border-radius:16px;
        box-shadow:0 5px 20px rgba(0,0,0,.05);
    }

    /* Date */

    [data-testid="stDateInput"] {
        background:white;
        padding:15px;
        border-radius:16px;
    }

    /* Download */

    .stDownloadButton button {
        background:#2563EB;
        color:white;
    }

    .stDownloadButton button:hover {
        background:#1D4ED8;
    }

    /* Hide footer */

    footer {
        visibility:hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# HEADER
# =========================

st.markdown(
    """
    <div class="brand">
        <h1>VIBES</h1>
        <p>Sales Automation</p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# UPLOAD
# =========================

st.markdown(
    """
    <div class="card">
        <div class="card-title">
            Upload Sales File
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded = st.file_uploader(
    "Upload",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)


# =========================
# DATE
# =========================

st.markdown(
    """
    <div class="card">
        <div class="card-title">
            Report Date
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

report_date = st.date_input(
    "Date",
    value=date.today(),
    label_visibility="collapsed"
)


# =========================
# GENERATE
# =========================

if uploaded:

    st.write("")

    if st.button(
        "Generate Reports",
        use_container_width=True
    ):

        try:

            suffix = Path(uploaded.name).suffix.lower()

            with tempfile.TemporaryDirectory() as temp_dir:

                temp_dir = Path(temp_dir)

                input_file = temp_dir / f"sales_input{suffix}"

                input_file.write_bytes(
                    uploaded.getbuffer()
                )

                df = prepare_data(input_file)

                date_text = report_date.strftime(
                    "%d-%b-%y"
                )

                invoice_name = (
                    f"Vibes_Invoice_{date_text}.pdf"
                )

                pick_name = (
                    f"Vibes_Pick_{date_text}.pdf"
                )

                invoice_file = temp_dir / invoice_name
                pick_file = temp_dir / pick_name

                create_invoice_pdf(
                    df,
                    invoice_file,
                    date_text
                )

                create_pick_pdf(
                    df,
                    pick_file,
                    date_text
                )

                st.session_state.invoice_bytes = (
                    invoice_file.read_bytes()
                )

                st.session_state.pick_bytes = (
                    pick_file.read_bytes()
                )

                st.session_state.invoice_name = invoice_name
                st.session_state.pick_name = pick_name

            st.success(
                "Reports Ready ✓"
            )

        except Exception as e:

            st.error(
                f"Unable to generate reports: {e}"
            )


# =========================
# DOWNLOAD
# =========================

if "invoice_bytes" in st.session_state:

    st.markdown(
        """
        <br>

        <div class="card">
            <div class="card-title">
                Generated Reports
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            ### 📄 Invoice
            """,
            unsafe_allow_html=True
        )

        st.download_button(
            label="Download PDF",
            data=st.session_state.invoice_bytes,
            file_name=st.session_state.invoice_name,
            mime="application/pdf",
            use_container_width=True
        )

    with col2:

        st.markdown(
            """
            ### 📦 Pick List
            """,
            unsafe_allow_html=True
        )

        st.download_button(
            label="Download PDF",
            data=st.session_state.pick_bytes,
            file_name=st.session_state.pick_name,
            mime="application/pdf",
            use_container_width=True
        )