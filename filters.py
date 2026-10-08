import re

def extract_filters(message):
    """
    Extract filters from user message
    Returns a dict of filters like max_price, switch_type, connectivity, etc.
    """
    filters = {}
    
    # Extract max price: look for "$" or "under/below/less than X"
    price_pattern = r'(?:under|below|less than)\s*\$?(\d+)'
    price_match = re.search(price_pattern, message, re.IGNORECASE)
    
    if price_match:
        filters['max_price'] = float(price_match.group(1))
    
    # Extract keywords for specific features
    message_lower = message.lower()
    
    if 'silent' in message_lower:
        filters['switch_type'] = 'silent'
    
    if 'wireless' in message_lower:
        filters['connectivity'] = 'wireless'
    
    if 'bluetooth' in message_lower:
        filters['connectivity'] = 'bluetooth'
    
    if 'mechanical' in message_lower:
        filters['keyboard_type'] = 'mechanical'
    
    if 'gaming' in message_lower:
        filters['category'] = 'gaming'
    
    if 'rgb' in message_lower:
        filters['lighting'] = 'rgb'
    
    return filters