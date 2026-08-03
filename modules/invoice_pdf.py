from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer
)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors



def create_invoice_pdf(df, output, report_date):


    doc = SimpleDocTemplate(

        str(output),

        pagesize=A4,

        rightMargin=25,

        leftMargin=25,

        topMargin=30,

        bottomMargin=30

    )


    elements = []



    # =========================
    # HEADER SECTION
    # =========================


    header_data = [

        ["Vibes"],

        [report_date]

    ]


    header_table = Table(

        header_data,

        colWidths=[470]

    )


    header_table.setStyle(

        TableStyle([


            (
                "BACKGROUND",
                (0,0),
                (-1,-1),
                colors.HexColor("#BDD7EE")
            ),


            (
                "GRID",
                (0,0),
                (-1,-1),
                0.5,
                colors.black
            ),


            (
                "ALIGN",
                (0,0),
                (-1,-1),
                "CENTER"
            ),


            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE"
            ),


            (
                "FONTNAME",
                (0,0),
                (-1,-1),
                "Helvetica-Bold"
            ),


            (
                "FONTSIZE",
                (0,0),
                (-1,0),
                16
            ),


            (
                "FONTSIZE",
                (0,1),
                (-1,1),
                13
            ),


            (
                "TOPPADDING",
                (0,0),
                (-1,-1),
                8
            ),


            (
                "BOTTOMPADDING",
                (0,0),
                (-1,-1),
                8
            )


        ])

    )


    elements.append(header_table)


    elements.append(
        Spacer(1,12)
    )



    # =========================
    # INVOICE TABLE
    # =========================


    table_data = [

        [
            "Serial",
            "Invoice",
            "Customer Name",
            "Product Name",
            "Qty"
        ]

    ]



    total_qty = 0



    for _, row in df.iterrows():


        table_data.append(

            [

                row["Serial"],

                row["Invoice"],

                row["Customer Name"],

                row["Product Name"],

                row["Qty"]

            ]

        )


        total_qty += row["Qty"]



    # =========================
    # TOTAL ROW
    # =========================


    table_data.append(

        [

            "",

            "",

            "",

            "TOTAL",

            total_qty

        ]

    )



    invoice_table = Table(

        table_data,

        repeatRows=1,

        colWidths=[

            35,

            65,

            95,

            235,

            35

        ]

    )



    invoice_table.setStyle(

        TableStyle([


            # Header colour

            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                colors.HexColor("#BDD7EE")
            ),


            (
                "FONTNAME",
                (0,0),
                (-1,0),
                "Helvetica-Bold"
            ),


            # Center alignment

            (
                "ALIGN",
                (0,0),
                (-1,-1),
                "CENTER"
            ),


            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE"
            ),


            # Borders

            (
                "GRID",
                (0,0),
                (-1,-1),
                0.5,
                colors.black
            ),


            # Font size

            (
                "FONTSIZE",
                (0,0),
                (-1,-1),
                8
            ),


            (
                "TOPPADDING",
                (0,0),
                (-1,-1),
                5
            ),


            (
                "BOTTOMPADDING",
                (0,0),
                (-1,-1),
                5
            ),


            # =========================
            # TOTAL ROW STYLE
            # =========================


            (
                "BACKGROUND",
                (0,-1),
                (-1,-1),
                colors.HexColor("#FFFF00")
            ),


            (
                "FONTNAME",
                (0,-1),
                (-1,-1),
                "Helvetica-Bold"
            )


        ])

    )



    elements.append(invoice_table)



    doc.build(elements)