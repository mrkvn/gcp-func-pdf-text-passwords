import base64
import os

import functions_framework  # gcp specific
from flask import jsonify
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFPasswordIncorrect


@functions_framework.http
def main(request):
    payload = request.get_json()

    # Decode the base64 PDF file
    try:
        file_data = base64.b64decode(payload["file"])
    except Exception:
        return jsonify({"detail": "Invalid base64 file encoding"}), 400

    passwords = payload["passwords"]
    pdf_path = f"/tmp/{payload['filename']}"

    # Write the file to disk
    try:
        with open(pdf_path, "wb") as f:
            f.write(file_data)
    except Exception:
        return jsonify({"detail": "Failed to write file to disk"}), 500

    # Extract text from the PDF
    try:
        with open(pdf_path, "rb") as file:
            text = try_passwords(file, passwords)

            if not text:
                text = "No text found in the PDF."

            return jsonify({"content": text})

    except Exception as e:
        return jsonify({"detail": f"Error processing PDF: {e}"}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass


def try_passwords(file, passwords):
    for password in passwords:
        try:
            text = extract_text(file, password=password)
            return text
        except PDFPasswordIncorrect:
            continue
    return None
