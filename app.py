import os

import openai
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text

from sql_tables import food_dataset, donations_dataset
from scanner import receive_barcodes


def create_tables() -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        # Create the 'donation_history' table with specified columns
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS donation_history (
                    product_code VARCHAR(13),
                    product_name VARCHAR(255),
                    category VARCHAR(255),
                    price NUMERIC(10, 2),
                    weight NUMERIC(10, 2),
                    quantity INT,
                    total_price NUMERIC(10, 2),
                    total_weight NUMERIC(10, 2));"""))
        s.commit()


def check_existing_entry(table_name: str, product_code: str) -> tuple | None:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT product_code, product_name, category, price, weight FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result


def get_sql_dataframe(table_name: str) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f'select * from {table_name} order by category'
    messages = conn.query(query, ttl=timedelta(minutes=1))
    st.dataframe(messages)


def customize_streamlit_ui() -> None:
    st.set_page_config(
        page_title="→ 🤖 → 🕸️ IdeaVault!",
        page_icon="💡",
        layout="wide"
        )

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


# ---------------------------------

customize_streamlit_ui()

title = "Woolworths Food Donations"
title = st.markdown(
    f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True
)

options = option_menu(None, 
                      ["Donations", "Barcode Scanner", "Dataset"], 
                      icons=['clipboard-data', 'upc-scan', "database-add"], 
                      menu_icon="cast", 
                      default_index=1, 
                      orientation="horizontal"
                      )
st.write(options)

#pages = [receive_barcodes, food_dataset, donations_dataset]
pages = {
    'Donations': donations_dataset,
    'Barcode Scanner': receive_barcodes,
    'Dataset': food_dataset
}
pages[options]()

try:
    create_tables()
except Exception as e:
    st.error(e)

# --- USER INTERACTION ---
user_input = st.text_input("Enter a barcode")
if user_input:
    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    st.write(user_input)


