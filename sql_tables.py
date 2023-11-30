import streamlit as st
from sqlalchemy import create_engine, text

def get_sql_dataframe(table_name: str) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f'select * from {table_name} order by category'
    messages = conn.query(query)
    st.dataframe(messages, use_container_width=True, hide_index=False)


def update_table(table_name, donation_data):
    """Update a SQL table with donation data."""
    # Define the SQL query with placeholders
    query = f"""
    INSERT INTO {table_name} (date_received, product_code, product_name, category, price, weight, quantity, total_price, total_weight)
    VALUES (:date_received, :product_code, :product_name, :category, :price, :weight, :quantity, :total_price, :total_weight);
    """
    # Connect to the database
    conn = st.connection("digitalocean", type="sql")

    # Check if donation_data keys match the query placeholders
    expected_keys = {'date_received', 'product_code', 'product_name', 'category', 'price', 'weight', 'quantity', 'total_price', 'total_weight'}
    if not expected_keys.issubset(donation_data.keys()):
        raise ValueError(f"donation_data keys do not match expected keys: {expected_keys}")

    # Execute the query using the donation data
    with conn.session as s:
        s.execute(text(query), **donation_data)
        s.commit()


def donations_dataset():
    product_details = {
        'date_received': '2023-11-30',
        'product_code': '20000370',
        'product_name': 'Pork Bangers 500 g',
        'category': 'Mixed Groceries',
        'price': 59.99,
        'weight': 0.5,
        'quantity': 1,
        'total_price': 59.99,
        'total_weight': 0.5
    }

    get_sql_dataframe('donation_history')
    dummy_data = st.button("Send dummy data...")
    if dummy_data:
        update_table('donation_history', product_details)


def food_dataset():
    st.write("Hello from Woolworths Dataset")
    get_sql_dataframe('dataset')

