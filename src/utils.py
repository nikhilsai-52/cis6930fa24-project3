import os
import sqlite3
import pandas as pd
from io import BytesIO
from pypdf import PdfReader
import re


def download_pdf_content(file_data):
    """
    Reads uploaded PDF file and returns its binary content.
    """
    return file_data.read()


def parse_line(line):
    """
    Splits the input string `line` into substrings based on sequences of 
    two or more whitespace characters, then strips any extra whitespace 
    from each substring, and returns the cleaned list of substrings.
    """
    return [item.strip() for item in re.split(r"\s{2,}", line)]


def extract_incident_data(pdf_data):
    """
    Extracts data from a NormanPD-style incident report PDF file 
    and organizes it into a pandas DataFrame.
    """
    reader = PdfReader(BytesIO(pdf_data))
    extracted_lines = []
    is_first_page = True

    for page in reader.pages:
        page_text = page.extract_text(extraction_mode="layout").split("\n")
        
        if is_first_page:
            field_names = parse_line(page_text[2])[1:]  # Ignore first column as it’s empty
            page_text = page_text[2:]
            is_first_page = False
        
        extracted_lines.extend([parse_line(item) for item in page_text])

    # Keep only rows with exactly the correct number of columns (e.g., 5 fields)
    filtered_lines = [line for line in extracted_lines if len(line) == len(field_names)]

    df = pd.DataFrame(filtered_lines, columns=field_names)
    return df


def store_in_database(df, db_path="resources/normanpd.db"):
    """
    Stores the extracted DataFrame into a SQLite database.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure the directory exists
    with sqlite3.connect(db_path) as conn:
        df.to_sql("incidents", conn, if_exists="replace", index=False)


def query_database(query, db_path="resources/normanpd.db"):
    """
    Executes a SQL query on the database and returns the result as a DataFrame.
    """
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)
