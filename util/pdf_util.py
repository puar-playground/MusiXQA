import fitz
from PIL import Image
from tqdm import tqdm
import os

def get_pdf_page_count(pdf_path):
    doc = fitz.open(pdf_path)
    return len(doc)

def pdf_to_images(pdf_path, output_folder, image_name=None, num_pages=None):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    if num_pages is None:
        num_pages = pdf_document.page_count

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = []
    for page_num in range(num_pages):
        # Get the page
        page = pdf_document.load_page(page_num)
        
        # Get the page's dimensions
        mat = fitz.Matrix(2, 2)  # Increase the resolution
        pix = page.get_pixmap(matrix=mat)

        # Save the image
        if image_name is None:
            output_image_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
        else:
            output_image_path = os.path.join(output_folder, f'{image_name}.png')
        pix.save(output_image_path)
        images.append(output_image_path)

    return images

