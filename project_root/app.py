from flask import Flask, request, render_template, jsonify
from scraper.king import KingScraper
from scraper.kitsap import KitsapScraper
from scraper.pierce import PierceScraper
from utils.export_word import generate_word_report
from flask import send_file
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    assessor_url = request.form.get("assessorurl")
    parcel_input = request.form.get("parcel_numbers", "") 

    # Split and clean parcel numbers (comma-separated, ignores spaces)
    parcel_list = [p.strip() for p in parcel_input.split(",") if p.strip()]

    # Validate inputs
    if not assessor_url or not parcel_list:
        return jsonify({"error": "Assessor URL and parcel number(s) are required"}), 400

    results = []

    # Loop through each parcel
    for parcel_number in parcel_list:
        url_lower = assessor_url.lower()
        if "kingcounty" in url_lower:
            scraper = KingScraper(parcel_number)
        elif "kitsap.gov" in url_lower:
            scraper = KitsapScraper(parcel_number)
        elif "piercecountywa" in url_lower:
            scraper = PierceScraper(parcel_number)
        else:
            results.append({"parcel_number": parcel_number, "error": "County not supported"})
            continue

        # Scrape data for this parcel
        try:
            data = scraper.scrape()

            # Only for Pierce: rename Tax Description to Legal Description
            if "piercecountywa" in url_lower and "Tax Description" in data:
                data["Legal Description"] = data.pop("Tax Description")

            results.append({"parcel_number": parcel_number, "data": data})
        except Exception as e:
            results.append({"parcel_number": parcel_number, "error": str(e)})

    # Return results without report_title
    return jsonify({"results": results})

@app.route("/export_word", methods=["POST"])
def export_word():
    parcel_numbers = request.form.get("parcel_numbers")  # plural
    assessor_url = request.form.get("assessorurl")

    if not parcel_numbers or not assessor_url:
        return "Parcel numbers and assessor URL are required", 400
    
    # Convert comma-separated list to Python list
    parcel_list = [p.strip() for p in parcel_numbers.split(",") if p.strip()]

    file_stream, error, data = generate_word_report(parcel_list, assessor_url, app.root_path)

    if error:
        return error, 400

    # Collect all addresses for filename
    addresses = []
    for parcel in parcel_list:
        address = data.get(parcel, {}).get("Site Address", parcel)
        safe_address = address.replace(" ", "_")
        addresses.append(safe_address)

    # Join all addresses with underscores
    combined_name = "_".join(addresses)

    # Prevent overly long filenames (Windows max ~255 chars)
    if len(combined_name) > 150:
        combined_name = combined_name[:150] + "_etc"

    return send_file(
        file_stream,
        as_attachment=True,
        download_name=f"{combined_name}_Property_Summary.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")
    app.run(debug=debug)