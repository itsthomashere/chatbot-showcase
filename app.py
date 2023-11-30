import os

import openai
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text

def customize_streamlit_ui() -> None:
    st.set_page_config(
        page_title="→ 🤖 → 🕸️ IdeaVault!",
        page_icon="💡",
        layout="centered"
        )

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

customize_streamlit_ui()

title = "Woolworths Food Donations"
title = st.markdown(
    f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True
)

options = option_menu(None, ["Donation History", "Barcode Scanner", "Dataset"], 
    icons=['house', 'cloud-upload', "list-task"], 
    menu_icon="cast", default_index=1, orientation="horizontal")

def create_tables() -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        # Create the 'users' table with a timestamp column
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                    ID SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE,
                    timestamp TIMESTAMPTZ);"""))
        
        # Create the 'submissions' table with a foreign key relation to 'users'
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS submissions (
                    ID SERIAL PRIMARY KEY,
                    uuid VARCHAR(36),
                    timestamp TIMESTAMPTZ,
                    role VARCHAR(9) CHECK (LENGTH(role) >= 4),
                    content TEXT,
                    FOREIGN KEY (uuid) REFERENCES users(uuid));"""))
        s.commit()

def save_to_sql(user_id: str, role: str, content: str) -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn.session as s:
        # Insert user_id and timestamp into 'users' table if it doesn't already exist
        s.execute(
            text('INSERT INTO users (uuid, timestamp) VALUES (:uuid, :timestamp) ON CONFLICT (uuid) DO NOTHING;'),
            params=dict(uuid=user_id, timestamp=timestamp)
        )
        
        # Insert into 'submissions' table
        s.execute(
            text('INSERT INTO submissions (uuid, timestamp, role, content) VALUES (:uuid, :timestamp, :role, :content);'),
            params=dict(uuid=user_id, timestamp=timestamp, role=role, content=content)
        )
        s.commit()

def get_sql_dataframe(table_name: str, uuid: str) -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    query = f'select * from {table_name} where uuid = :uuid order by timestamp'
    messages = conn.query(query, ttl=timedelta(minutes=1), params={"uuid": uuid})
    st.dataframe(messages)

try:
    create_tables()
except Exception:
    pass

# --- USER INTERACTION ---
user_input = st.text_input("Enter a barcode")
if user_input:
    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    st.write(user_input)

