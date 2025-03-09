import json
import re
import os
import base64
from mistralai import Mistral
from mistralai.models import TextChunk, ImageURLChunk

# Load the Markdown content
md_file_path = r"C:\Users\suman\DocumentExtraction\ocr_extraction\results\mistral_output.md"
with open(md_file_path, "r", encoding="utf-8") as md_file:
    markdown_content = md_file.read()

# Extract image paths from Markdown
image_pattern = r"!\[.*?\]\((.*?)\)"
image_paths = re.findall(image_pattern, markdown_content)

# Function to convert image file to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return f"data:image/jpg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"

# Convert images to base64
base64_images = [encode_image_to_base64(img) for img in image_paths]

# Set up Mistral API key
api_key = "WKZfiTbEKWHZdi5zESkDrNdzuoKJ6OsI"
client = Mistral(api_key=api_key)

# Function to send a batch of images with text
def process_batch(batch_images):
    message_content = [
        TextChunk(
            text=f"""
            This is OCR-extracted content in Markdown format:
            <BEGIN_OCR_MARKDOWN>
            {markdown_content}
            <END_OCR_MARKDOWN>
            
            The Markdown content contains images. Process them together with the text and extract relevant details into a **structured JSON format**.
            Ensure any text present in images is also considered.

            ### **Required JSON Structure**
            
            1️⃣ **Document Metadata**
               - Document Type (e.g., "Deed of Settlement", "Stamp Duty Receipt", "Non-Traceable Certificate")
               - Date of Execution
               - Location of Execution
               - Reference Number(s) (if any)

            2️⃣ **Parties Involved**
               - **Settlor** (Name, Aadhaar, Address, Relationship to Settlee)
               - **Settlee** (Name, Aadhaar, Address)
            
            3️⃣ **Property Details**
               - Description
               - Survey Numbers
               - Total Area (Sq. ft.)
               - Value of Property
               - Ownership History
            
            4️⃣ **Legal Settlement Details**
               - Encumbrances (Yes/No, with details)
               - Stamp Duty Details (Amount, Section, Sub-Registrar, Date)
            
            5️⃣ **Witness Information**
               - Name, Aadhaar, Address

            6️⃣ **Additional Certificates (If Present)**
               - Non-Traceable Certificate (Issuer, Date, Description)

            Extract data **only from text and images** without adding extra commentary.
            """
        )
    ]

    # Add up to 8 image chunks per batch
    for img_base64 in batch_images:
        message_content.append(ImageURLChunk(image_url=img_base64))

    # Send request to PixTral-12B
    chat_response = client.chat.complete(
        model="pixtral-12b-latest",
        messages=[{"role": "user", "content": message_content}],
        response_format={"type": "json_object"},
        temperature=0
    )

    # Parse JSON response
    return json.loads(chat_response.choices[0].message.content)

# Split images into batches of 8
batch_size = 8
batches = [base64_images[i:i + batch_size] for i in range(0, len(base64_images), batch_size)]

# Process each batch and collect results
combined_results = []
for batch in batches:
    response_data = process_batch(batch)
    combined_results.append(response_data)

# Merge results into a single JSON object
final_json = {"extracted_data": combined_results}

# Save JSON output
output_json_file = "structured_output2.json"
with open(output_json_file, "w", encoding="utf-8") as json_file:
    json.dump(final_json, json_file, indent=4)

print(f"Structured JSON response saved to {output_json_file}")
