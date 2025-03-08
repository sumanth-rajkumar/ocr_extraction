import os
import base64
from mistralai import Mistral, DocumentURLChunk
from mistralai.models import OCRResponse
from pathlib import Path

# Path to the PDF file
pdf_file = Path(r"C:\Users\suman\DocumentExtraction\CamScanner 10-19-2023 16.47.pdf")

# Set up Mistral API key
api_key = "WKZfiTbEKWHZdi5zESkDrNdzuoKJ6OsI"
client = Mistral(api_key=api_key)

# Upload the file to Mistral OCR
uploaded_file = client.files.upload(
    file={
        "file_name": pdf_file.stem,
        "content": pdf_file.read_bytes(),
    },
    purpose="ocr",
)

# Get signed URL for processing
signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

# Process the document using Mistral OCR
pdf_response = client.ocr.process(
    document=DocumentURLChunk(document_url=signed_url.url),
    model="mistral-ocr-latest",
    include_image_base64=True
)

# Directory for extracted images
output_images_dir = "extracted_images"
os.makedirs(output_images_dir, exist_ok=True)

def replace_images_in_markdown(markdown_str: str, images_dict: dict, output_dir: str) -> str:
    """
    Saves images as separate files and updates the Markdown file to reference them.
    """
    for img_name, base64_str in images_dict.items():
        img_path = os.path.join(output_dir, f"{img_name}.jpg")

        # Decode and save the image file
        with open(img_path, "wb") as img_file:
            img_file.write(base64.b64decode(base64_str))

        # Update the Markdown image link to reference the saved file
        markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({img_path})")

    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse, output_dir: str) -> str:
    """
    Processes the OCR response and outputs a Markdown file with extracted images referenced correctly.
    """
    markdowns = []

    for page in ocr_response.pages:
        image_data = {img.id: img.image_base64 for img in page.images}
        markdowns.append(replace_images_in_markdown(page.markdown, image_data, output_dir))

    return "\n\n".join(markdowns)

# Generate the Markdown text with properly saved image references
ocr_text_markdown = get_combined_markdown(pdf_response, output_images_dir)

# Save the OCR result to a Markdown file
output_file = "output.md"
with open(output_file, "w", encoding="utf-8") as md_file:
    md_file.write(ocr_text_markdown)

print(f"OCR result saved to {output_file}")
print(f"Extracted images saved in {output_images_dir}")
