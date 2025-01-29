import streamlit as st
import sqlite3
import pandas as pd
import json
from typing import Dict, Optional

# Initialize Streamlit page
st.set_page_config(
    page_title="NLP to SQL Converter",
    page_icon="🔍",
    layout="wide"
)

class SimpleNLP2SQL:
    def __init__(self):
        self.system_message = """
        Generate a SQL query based on the natural language input and database schema.
        Only generate SELECT queries. Ensure the query is safe and valid.
        Return the response in this format:
        {
            "query": "The SQL query",
            "explanation": "Explanation of the query"
        }
        """

    def generate_query(self, user_input: str, schema: Dict) -> Dict:
        """
        This is a placeholder for the actual LLM query generation.
        In a real implementation, this would call your LLM service.
        """
        
        return {
            "query": f"-- Generated from: {user_input}\nSELECT * FROM table_name LIMIT 5;",
            "explanation": "This is a basic query that selects all columns from the specified table."
        }

def load_database(uploaded_file) -> Optional[sqlite3.Connection]:
    """Load an SQLite database from an uploaded file."""
    if uploaded_file is None:
        return None

    # Save uploaded file temporarily
    with open("temp_db.sqlite", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Connect to the database
    return sqlite3.connect("temp_db.sqlite")

def get_schema(conn: sqlite3.Connection) -> Dict:
    """Extract schema information from the database."""
    schema = {}
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        schema[table_name] = {
            'columns': {col[1]: {'type': col[2]} for col in columns},
            'primary_keys': [col[1] for col in columns if col[5]]
        }

    return schema

def main():
    st.title("💬 Natural Language to SQL Converter")
    st.markdown("Upload your SQLite database and type your query in natural language.")

    # File uploader for database
    uploaded_file = st.file_uploader("Upload SQLite Database", type=['db', 'sqlite', 'sqlite3'])

    if uploaded_file:
        # Load database and schema
        conn = load_database(uploaded_file)
        if conn is not None:
            schema = get_schema(conn)

            # Display available tables
            st.subheader("Available Tables")
            for table_name, table_info in schema.items():
                with st.expander(f"Table: {table_name}"):
                    st.json(table_info)

            # Natural language input
            user_input = st.text_input("Enter your query in natural language",
                                     placeholder="e.g., Show me all users who joined last month")

            if user_input:
                with st.spinner("Generating SQL query..."):
                    # Generate SQL query
                    nlp2sql = SimpleNLP2SQL()
                    result = nlp2sql.generate_query(user_input, schema)

                    # Display results
                    st.subheader("Generated SQL Query")
                    st.code(result["query"], language="sql")

                    st.subheader("Explanation")
                    st.write(result["explanation"])

                    # Execute query button
                    if st.button("Execute Query"):
                        try:
                            df = pd.read_sql_query(result["query"], conn)
                            st.subheader("Query Results")
                            st.dataframe(df)
                        except Exception as e:
                            st.error(f"Error executing query: {str(e)}")

        else:
            st.error("Error loading database. Please make sure it's a valid SQLite database.")

    else:
        st.info("👆 Please upload a SQLite database file to begin.")

if __name__ == "__main__":
    main()
