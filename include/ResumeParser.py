def extract_phone_number(self):
    items = re.finditer(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}', resume)
    return [(resume[item.span()[0]:item.span()[1]], item.span()) for item in items]
    
    
    
        