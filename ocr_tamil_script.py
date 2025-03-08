from pdf2image import convert_from_path
from ocr_tamil.ocr import OCR

# Set the path to the Poppler 'bin' directory
poppler_path = r'C:\Users\suman\poppler\poppler-24.08.0\Library\bin'  # Replace with your actual path

def extract_text_from_pdf(pdf_path, dpi=300):
    """
    Converts a scanned PDF to images and extracts Tamil text from each image using OCR.
    Adds page dividers and ensures each extracted text appears on a new line.
    """
    print(f"Converting PDF pages from '{pdf_path}' to images...")
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    print(f"Converted {len(pages)} pages.")

    ocr = OCR(detect=True)  # Initialize Tamil OCR
    full_text = ""

    for i, page in enumerate(pages, start=1):
        print(f"Processing page {i}...")
        
        # Save the page as a temporary image file
        temp_image_path = f"page_{i}.jpg"
        page.save(temp_image_path, "JPEG")

        # Extract text using Tamil OCR
        text_list = ocr.predict([temp_image_path])

        # Ensure each extracted sentence/word is on a new line
        page_text = "\n".join(text_list[0]) if text_list else ""

        # Add a page divider before appending the extracted text
        full_text += f"\n==== Page {i} ====\n{page_text}\n"
    
    return full_text

def save_text_to_file(text, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Extracted text written to '{output_file}'.")

if __name__ == "__main__":
    pdf_path = r'C:\Users\suman\DocumentExtraction\CamScanner 10-19-2023 16.47.pdf'
    output_file = 'extracted_tamil_text2.txt'
    
    extracted_text = extract_text_from_pdf(pdf_path, dpi=300)
    save_text_to_file(extracted_text, output_file)
