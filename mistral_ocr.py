import os
import base64
from mistralai import Mistral, DocumentURLChunk
from mistralai.models import OCRResponse
from pathlib import Path

# Path to the PDF file
pdf_file = Path(r"C:\Users\suman\DocumentExtraction\CamScanner 10-19-2023 16.47.pdf")

# Set up Mistral API key
api_key = "WKZfiTbEKWHZdi5zESkDrNdzuoKJ6OsI"  # Replace with your actual API key
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


def save_image(image_id: str, base64_str: str, output_dir: str) -> str:
    """
    Saves a base64-encoded image to a file and returns the relative file path.
    Ensures the file is correctly decoded and saved.
    """
    try:
        # Ensure the base64 string starts correctly
        if not base64_str.startswith("data:image"):
            print(f"⚠ Warning: Image {image_id} might have an invalid base64 format.")
            return ""

        # Extract actual base64 data (strip metadata)
        base64_data = base64_str.split(",")[-1]  # Only keep the base64 content

        # Decode base64
        img_data = base64.b64decode(base64_data)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the image
        img_path = os.path.join(output_dir, f"{image_id}.jpg")
        with open(img_path, "wb") as img_file:
            img_file.write(img_data)

        print(f"✅ Saved image: {img_path}")
        return img_path  # Return relative path for Markdown

    except Exception as e:
        print(f"❌ Error saving image {image_id}: {e}")
        return ""


def replace_images_in_markdown(markdown_str: str, images_dict: dict, output_dir: str) -> str:
    """
    Saves images as separate files and updates the Markdown file to reference them.
    """
    for img_name, base64_str in images_dict.items():
        img_path = save_image(img_name, base64_str, output_dir)  # Save image and get path
        if img_path:
            markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({img_path})")

    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse, output_dir: str) -> str:
    """
    Processes the OCR response and outputs a Markdown file with extracted images referenced correctly.
    """
    markdowns = []
    
    for page_num, page in enumerate(ocr_response.pages, start=1):
        print(f"Processing Page {page_num}...")
        image_data = {img.id: img.image_base64 for img in page.images} if page.images else {}
        markdowns.append(replace_images_in_markdown(page.markdown, image_data, output_dir))

    return "\n\n".join(markdowns)

# Generate the Markdown text with properly saved image references
ocr_text_markdown = get_combined_markdown(pdf_response, output_images_dir)

# Save the OCR result to a Markdown file
output_file = "mistral_output.md"
with open(output_file, "w", encoding="utf-8") as md_file:
    md_file.write(ocr_text_markdown)

print(f"\n✅ OCR result saved to: {output_file}")
print(f"✅ Extracted images saved in: {output_images_dir}")
