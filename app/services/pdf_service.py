from pdfminer.high_level import extract_text
import re
from flask import current_app
import json
import tempfile

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file: A file-like object containing the PDF
    
    Returns:
        The extracted text
    """
    # Create a temporary file to save the PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as temp:
        # Write the PDF content to the temporary file
        pdf_file.seek(0)
        temp.write(pdf_file.read())
        temp.flush()
        
        # Extract text from the PDF
        text = extract_text(temp.name)
    
    return text

def extract_menu_from_pdf(pdf_file):
    """
    Extract menu information from a PDF file.
    
    Args:
        pdf_file: A file-like object containing the PDF
    
    Returns:
        A dictionary containing menu information
    """
    text = extract_text_from_pdf(pdf_file)
    
    # Dictionary to store the extracted menu
    menu = {
        "dishes": [],
        "menu_restrictions": []
    }
    
    # Look for price patterns
    price_pattern = r"(\d+[.,]\d{2})[\s€$]"
    prices = re.findall(price_pattern, text)
    
    # Look for menu restrictions
    restriction_patterns = {
        "vegetarian": r"vegetari[ao]n[ao]?s?",
        "vegan": r"vegan[ao]?s?",
        "gluten-free": r"(sin gluten|gluten[ -]free)",
        "lactose-free": r"(sin lactosa|lactose[ -]free)"
    }
    
    for restriction, pattern in restriction_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            menu["menu_restrictions"].append(restriction)
    
    # Extract dishes using some heuristics
    lines = text.split('\n')
    current_category = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a category header
        if line.isupper() or (len(line) < 30 and not re.search(price_pattern, line)):
            current_category = line
            continue
        
        # Look for dish patterns (name followed by price)
        dish_match = re.search(r"(.*?)(\d+[.,]\d{2})[\s€$]", line)
        if dish_match:
            dish_name = dish_match.group(1).strip()
            dish_price = float(dish_match.group(2).replace(',', '.'))
            
            # Add to dishes list
            menu["dishes"].append({
                "name": dish_name,
                "price": dish_price,
                "category": current_category
            })
    
    # If no dish was found, try a more general approach
    if not menu["dishes"]:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip very short lines and lines with only numbers or punctuation
            if len(line) < 3 or re.match(r"^[\d\s,.;:!?]+$", line):
                continue
            
            menu["dishes"].append({
                "name": line,
                "price": None,
                "category": None
            })
    
    return menu