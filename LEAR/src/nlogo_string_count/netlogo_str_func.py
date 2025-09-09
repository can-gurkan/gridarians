import re
from enum import Enum

def netlogo_length(code_string, remove_comments=True, count_words=False):
    """
    Calculates the length of a NetLogo program string.
    
    Parameters:
    - code_string (str): NetLogo code
    - remove_comments (bool): remove comments (lines starting with ';') 
    - count_words (bool): If True, count words... if False, count characters
    
    Returns:
    - int: Number of characters or words in the code
    """
    processed_code = code_string
    
    if remove_comments:
        # Remove all comments (lines starting with ';' and anything after it on that line)
        processed_code = re.sub(r';.*?($|\n)', '', processed_code)
    
    # Remove all whitespace, tabs, and newlines --> replace with single character whitespace
    processed_code = re.sub(r'\s+', ' ', processed_code).strip()
    
    if count_words:
        # Split by whitespace and count non-empty elements
        words = [word for word in processed_code.split() if word]
        return len(words)
    else:
        processed_code_without_whitespace = processed_code.replace(' ', '')
        return len(processed_code_without_whitespace)
