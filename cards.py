import os
import fitz  
from PIL import Image
import numpy as np

def is_white(margin, threshold=0.9):
    """Determine if an image area is predominantly white."""
    white_pixels = np.all(margin >= 100, axis=-1)
    white_ratio = np.mean(white_pixels)
    return white_ratio > threshold

def analyze_odd_pages(pdf_path, margin=100):
    """Analyze odd pages to determine if they are predominantly white."""
    document = fitz.open(pdf_path)
    results = {}
    for i in range(0, len(document), 2):
        page = document.load_page(i)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        image_np = np.array(img)

        top_margin = image_np[:margin, :]
        bottom_margin = image_np[-margin:, :]
        left_margin = image_np[:, :margin]
        right_margin = image_np[:, -margin:]

        all_white = all([
            is_white(top_margin),
            is_white(bottom_margin),
            is_white(left_margin),
            is_white(right_margin)
        ])

        results[f'Page {i+1}'] = 'White' if all_white else 'Not White'
    document.close()
    return results

def extract_and_assemble(card_pdf, inner_pdf, outer_pdf, results, white_folder, non_white_folder):
    """Extract and assemble the PDFs based on the analysis results."""
    card_doc = fitz.open(card_pdf)
    inner_doc = fitz.open(inner_pdf)
    outer_doc = fitz.open(outer_pdf)

    for set_number, i in enumerate(range(0, len(card_doc), 2)):
        set_pdf = fitz.open()
        set_pdf.insert_pdf(card_doc, from_page=i, to_page=i+1)

        set_pdf.insert_pdf(inner_doc, from_page=set_number, to_page=set_number)

        set_pdf.insert_pdf(outer_doc, from_page=0, to_page=0)

        save_path = white_folder if results[f'Page {i+1}'] == 'White' else non_white_folder
        filename = os.path.join(save_path, f'set_{set_number + 1}.pdf')
        set_pdf.save(filename)
        set_pdf.close()

    card_doc.close()
    inner_doc.close()
    outer_doc.close()

cards_pdf = './cards-2 (10).pdf'
inner_envelopes_pdf = './inner envelopes-2 (1).pdf'
outer_envelopes_pdf = './outer envelopes-2 (1).pdf'
white_folder = './whiteFolder'
non_white_folder = './nonWhiteFolder'

results = analyze_odd_pages(cards_pdf)
extract_and_assemble(cards_pdf, inner_envelopes_pdf, outer_envelopes_pdf, results, white_folder, non_white_folder)
