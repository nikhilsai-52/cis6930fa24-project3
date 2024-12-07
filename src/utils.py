import os
import sqlite3
import pandas as pd
from io import BytesIO
from pypdf import PdfReader
import re


def download_pdf_content(file_data):
    return file_data.read()


def parse_line(line):
    return [item.strip() for item in re.split(r"\s{2,}", line)]


def extract_incident_data(pdf_data):
    reader = PdfReader(BytesIO(pdf_data))
    extracted_lines = []
    is_first_page = True

    for page in reader.pages:
        page_text = page.extract_text(extraction_mode="layout").split("\n")
        
        if is_first_page:
            field_names = parse_line(page_text[2])[1:]  
            page_text = page_text[2:]
            is_first_page = False
        
        extracted_lines.extend([parse_line(item) for item in page_text])

    
    filtered_lines = [line for line in extracted_lines if len(line) == len(field_names)]

    df = pd.DataFrame(filtered_lines, columns=field_names)
    return df


def store_in_database(df, db_path="resources/normanpd.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  
    with sqlite3.connect(db_path) as conn:
        df.to_sql("incidents", conn, if_exists="replace", index=False)


def query_database(query, db_path="resources/normanpd.db"):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)
