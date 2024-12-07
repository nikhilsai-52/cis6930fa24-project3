# cis6930fa24-project3
# Incident Report Analysis Tool

A Python-based web application for processing and analyzing incident report PDFs (NormanPD format). This tool extracts data, stores it in a database, and generates insightful visualizations.

---
## Features

1. **Upload and Process PDFs**
   - Upload multiple incident report PDFs for automated processing.
   - Extracts structured data from PDFs using `PyPDF`.

2. **Data Storage**
   - Stores the extracted data in a SQLite database (`normanpd.db`).

3. **Data Visualization**
   - Generates visualizations including:
     - K-Means clustering with UMAP reduction.
     - Bar charts for incident types.
     - Heatmaps of relationships between locations and incidents.

4. **Web Interface**
   - Simple and user-friendly Flask interface for file uploads and visualization display.

---
## Code Overview

1. **utils.py**
   - Handles PDF processing and database operations:
     - download_pdf_content: Reads the binary content of uploaded PDFs.
     - parse_line: Cleans and parses lines from PDF text.
     - extract_incident_data: Extracts structured data into a pandas DataFrame.
     - store_in_database: Saves data to SQLite.
     - query_database: Executes SQL queries and retrieves data as a DataFrame.

2. **visualizations.py**
   - Generates visual insights from the data:
     - UMAP with K-Means Clustering: Visualizes clusters of incident types.
     - Bar Charts: Displays top incident types by count.
     - Heatmaps: Shows relationships between incident locations and types.

3. **app.py**
   - Flask application that manages the web interface:
     - index: Handles file uploads and data extraction.
     - visualize: Displays visualizations of the data.
---
## External Resources 

This project leverages the following libraries and tools:

PyPDF: For PDF parsing and text extraction.
UMAP: For dimensionality reduction.
SQLite: For lightweight database storage.
Flask: For the web framework.
Matplotlib and Seaborn: For visualizations.
Scikit-learn: For K-Means clustering.

---

## Bugs and Assumptions

### Assumptions

1. PDFs are in NormanPD format, with structured fields.
2. Extracted data aligns consistently with predefined field names.

### Bugs

1. Text extraction may fail for poorly formatted or scanned PDFs.
2. Cluster descriptions may not accurately represent all items in the group.
3. Large datasets may slow down visualization rendering.

---

## Development Process

1. PDF Data Extraction:

    Used PyPDF for text extraction.
    Developed regex-based parsing to handle whitespace-separated fields.

2. Data Storage:

    Stored parsed data in a SQLite database for querying and visualization.

3. Visualization:

    Experimented with UMAP for dimensionality reduction and K-Means clustering.
    Added multiple visualization types to highlight key patterns.

4. Web Application:

    Built a simple Flask interface for uploading PDFs and displaying results.
