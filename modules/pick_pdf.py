from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer
)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors



def create_pick_pdf(df, output, report_date):


    doc = SimpleDocTemplate(

        str(output),

        pagesize=A4,

        rightMargin=35,

        leftMargin=35,

        topMargin=30,

        bottomMargin=30

    )


    elements = []



    # =========================
    # HEADER SECTION
    # =========================


    header_data = [

        ["Vibes"],

        [f"{report_date} Pick"]

    ]



    header_table = Table(

        header_data,

        colWidths=[430]

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


    elements.append(
        header_table
    )


    elements.append(
        Spacer(1,15)
    )



    # =========================
    # PRODUCT GROUPING
    # =========================


    df = df.copy()



    # Extract base category

    df["Base Product"] = (

        df["Product Name"]

        .str.rsplit(
            "-",
            n=2
        )

        .str[0]

        .str.strip()

    )



    # Sort category and product

    df = df.sort_values(

        [
            "Base Product",
            "Product Name"
        ]

    )



    # =========================
    # CREATE TABLE DATA
    # =========================


    table_data = [

        [
            "Product Name",
            "Qty"
        ]

    ]



    subtotal_rows = []

    current_row = 1


    grand_total = 0



    for category, group in df.groupby(

        "Base Product",

        sort=True

    ):



        category_total = 0



        for _, row in group.iterrows():


            table_data.append(

                [

                    row["Product Name"],

                    row["Qty"]

                ]

            )


            category_total += row["Qty"]

            current_row += 1



        # Add category subtotal row


        table_data.append(

            [

                "",

                category_total

            ]

        )


        subtotal_rows.append(

            current_row

        )


        current_row += 1



        grand_total += category_total



    # =========================
    # FINAL TOTAL
    # =========================


    table_data.append(

        [

            "TOTAL",

            grand_total

        ]

    )


    final_total_row = len(table_data)-1



    # =========================
    # CREATE TABLE
    # =========================


    pick_table = Table(

        table_data,

        repeatRows=1,

        colWidths=[360,50]

    )



    style_list = [


        # Header background

        (
            "BACKGROUND",
            (0,0),
            (-1,0),
            colors.HexColor("#BDD7EE")
        ),



        # Header font

        (
            "FONTNAME",
            (0,0),
            (-1,0),
            "Helvetica-Bold"
        ),



        # Alignment

        (
            "ALIGN",
            (1,0),
            (1,-1),
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
            9
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
        )

    ]



    # =========================
    # CATEGORY SUBTOTAL STYLE
    # =========================


    for row in subtotal_rows:


        style_list.append(

            (

                "BACKGROUND",

                (0,row),

                (-1,row),

                colors.HexColor("#FFFF00")

            )

        )


        style_list.append(

            (

                "FONTNAME",

                (0,row),

                (-1,row),

                "Helvetica-Bold"

            )

        )



    # =========================
    # FINAL TOTAL STYLE
    # =========================


    style_list.append(

        (

            "BACKGROUND",

            (0,final_total_row),

            (-1,final_total_row),

            colors.HexColor("#FFFF00")

        )

    )


    style_list.append(

        (

            "FONTNAME",

            (0,final_total_row),

            (-1,final_total_row),

            "Helvetica-Bold"

        )

    )



    pick_table.setStyle(

        TableStyle(style_list)

    )



    elements.append(

        pick_table

    )



    doc.build(elements)