import os
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# AWS
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# OCR fallback
from PIL import Image
import pytesseract

# ----------------------------
# App & Config
# ----------------------------
load_dotenv()


client = boto3.client("translate")
print(client.list_languages()['Languages'][:3])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_IMAGE_EXTS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)

# AWS clients (region via AWS_DEFAULT_REGION in env)
translate_client = boto3.client("translate")
textract_client = boto3.client("textract")


# ----------------------------
# Helpers
# ----------------------------
def allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTS


def ocr_with_textract_bytes(image_bytes: bytes) -> str:
    """
    Use Textract DetectDocumentText on image bytes (PNG/JPG/JPEG).
    Returns concatenated detected text.
    """
    try:
        resp = textract_client.detect_document_text(Document={"Bytes": image_bytes})
        lines = []
        for block in resp.get("Blocks", []):
            if block.get("BlockType") == "LINE" and "Text" in block:
                lines.append(block["Text"])
        return "\n".join(lines).strip()
    except (BotoCoreError, ClientError) as e:
        app.logger.warning(f"Textract failed: {e}")
        return ""


def ocr_with_pytesseract(image_bytes: bytes) -> str:
    """
    Fallback OCR using pytesseract. Works locally without AWS.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return (text or "").strip()
    except Exception as e:
        app.logger.warning(f"pytesseract failed: {e}")
        return ""


def translate_text(text: str, target_lang: str) -> str:
    """
    Use AWS Translate. SourceLanguageCode='auto' for auto-detect.
    """
    if not text.strip():
        return ""
    try:
        resp = translate_client.translate_text(
            Text=text,
            SourceLanguageCode="auto",
            TargetLanguageCode=target_lang
        )
        return resp.get("TranslatedText", "").strip()
    except (BotoCoreError, ClientError) as e:
        app.logger.error(f"Translate failed: {e}")
        return ""


# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    error = None

    if request.method == "POST":
        target_lang = (request.form.get("language") or "en").strip()
        typed_text = (request.form.get("text_input") or "").strip()

        # If an image is provided, prefer OCR path; otherwise use typed text
        file = request.files.get("image_file")
        extracted_text = ""

        if file and file.filename:
            filename = secure_filename(file.filename)
            if not allowed_image(filename):
                error = "Unsupported image type. Please upload PNG/JPG/JPEG."
            else:
                # Save to disk 
                save_path = os.path.join(UPLOAD_DIR, filename)
                file.save(save_path)

                # Read bytes for Textract/pytesseract
                with open(save_path, "rb") as f:
                    image_bytes = f.read()

                # First try Textract, then fallback to pytesseract
                extracted_text = ocr_with_textract_bytes(image_bytes)
                if not extracted_text:
                    extracted_text = ocr_with_pytesseract(image_bytes)

        else:
            extracted_text = typed_text

        # Translate if we have text
        if not error:
            if not extracted_text.strip():
                error = "No text found to translate. Provide text or a clear image."
            else:
                translated_text = translate_text(extracted_text, target_lang)
                if not translated_text:
                    error = "Translation failed. Check AWS credentials/region."

    return render_template("index.html", translated_text=translated_text, error=error)


# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    # For local dev; in production use gunicorn/uwsgi + reverse proxy
    app.run(host="0.0.0.0", port=5000, debug=True)
