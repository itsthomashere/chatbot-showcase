import streamlit as st

def get_sql_dataframe(table_name: str) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f'select * from {table_name} order by category'
    messages = conn.query(query, ttl=timedelta(minutes=1))
    st.dataframe(messages)

def food_dataset():
    st.write("Hello from Woolworths Dataset")
    get_sql_dataframe('dataset')

def donations_dataset():
    st.write("Hello from Donations")
    get_sql_dataframe('donation_history')


