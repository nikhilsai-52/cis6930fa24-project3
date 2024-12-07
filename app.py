from flask import Flask, render_template, request, redirect, url_for, flash
import os
from src.utils import extract_incident_data, store_in_database
from src.visualizations import generate_visualizations

app = Flask(__name__, static_folder="static")
app.secret_key = "secret_key"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "files" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        files = request.files.getlist("files")
        
        # Check if any file was selected
        if len(files) == 0 or files[0].filename == "":
            flash("No selected files")
            return redirect(request.url)
        
        for file in files:
            if file.filename == "":
                continue
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            # Extract data from the PDF
            with open(file_path, "rb") as f:
                data = extract_incident_data(f.read())
            store_in_database(data)

        return redirect(url_for("visualize"))

    return render_template("index.html")

@app.route("/visualize")
def visualize():
    generate_visualizations()  # Generate charts
    bar = "bar_chart.png"
    # If you have multiple charts, you can add them here
    return render_template("visualize.html", bar=bar)

if __name__ == "__main__":
    app.run(debug=True)
