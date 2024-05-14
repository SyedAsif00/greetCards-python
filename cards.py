import fitz  
from PIL import Image
import numpy as np

def is_white(margin, threshold=0.9):
    white_pixels = np.all(margin >= 100, axis=-1)
    white_ratio = np.mean(white_pixels)
    return white_ratio > threshold

def analyze_odd_pages(pdf_path, margin=100):
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

pdf_path = "./cards-2 (10).pdf"

results = analyze_odd_pages(pdf_path)
print(results)
