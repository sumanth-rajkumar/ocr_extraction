import json
from mistralai import Mistral
from mistralai.models import TextChunk

# Load Markdown content from the previously generated file
with open(r"C:\Users\suman\DocumentExtraction\ocr_extraction\results\mistral_output.md", "r", encoding="utf-8") as md_file:
    markdown_content = md_file.read()

# Set up Mistral API key
api_key = "WKZfiTbEKWHZdi5zESkDrNdzuoKJ6OsI"
client = Mistral(api_key=api_key)

# Send the Markdown content to PixTral-12B for structured JSON conversion
chat_response = client.chat.complete(
    model="pixtral-12b-latest",
    messages=[
        {
            "role": "user",
            "content": [
                TextChunk(
                    text=f"This is OCR-extracted content in Markdown:\n<BEGIN_OCR_MARKDOWN>\n{markdown_content}\n<END_OCR_MARKDOWN>.\nConvert this into a structured JSON format representing the extracted information. The output should strictly be JSON with no extra commentary."
                )
            ],
        },
    ],
    response_format={"type": "json_object"},
    temperature=0
)

# Parse the JSON response from the model
response_dict = json.loads(chat_response.choices[0].message.content)

# Save the structured JSON to a file
output_json_file = "structured_output.json"
with open(output_json_file, "w", encoding="utf-8") as json_file:
    json.dump(response_dict, json_file, indent=4)

print(f"Structured JSON response saved to {output_json_file}")
