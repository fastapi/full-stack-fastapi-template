def transform_restaurant_data(zomato_data):
    """
    Transform Zomato restaurant data into the specified MenuData format.
    
    Args:
        zomato_data (dict): The Zomato restaurant data in its original format
        
    Returns:
        dict: The transformed data in MenuData format
    """
    try:
        # Extract the menu data from the Zomato data structure
        restaurant = zomato_data.get('pages', {}).get('restaurant', {})

        resId = list(restaurant)[0]
    
        menu_list = zomato_data.get('pages', {}).get('restaurant', {}).get(resId, {}).get('order', {}).get('menuList', {})
                
        if not menu_list:
            menu_list = zomato_data.get('order', {}).get('menuList', {})
        
        menus = menu_list.get('menus', [])
        
        # Initialize the result structure
        result = {
            "menu": []
        }
        
        # Process each menu category

        categories = []
        for menu_entry in menus:




            menu = menu_entry.get('menu', {})
            subcategories = menu.get('categories', [])
            
            for sub_cat_entry in subcategories:
                subcategory = sub_cat_entry.get('category', {})
                subcategory_name = subcategory.get('name', '')
                items = subcategory.get('items', [])
                
                # Check if we need to create a subcategory
                has_subcategories = False
                subcategories_map = {}
                
                # First, scan items to see if they have any group information that could be used as subcategories
                for item_entry in items:
                    item = item_entry.get('item', {})
                    # Look for potential subcategory indicators in the item data
                    # This could be customized based on the actual data structure
                    groups = item.get('groups', [])
                    if groups:
                        has_subcategories = True
                        for group_entry in groups:
                            group = group_entry.get('group', {})
                            subcategory_name = group.get('name', 'Other')
                            if subcategory_name not in subcategories_map:
                                subcategories_map[subcategory_name] = []
                
                # If no subcategories found, create a default one
                if not has_subcategories:
                    subcategories_map['General'] = []
                
                # Process each menu item and assign to appropriate subcategory
                for item_entry in items:
                    item = item_entry.get('item', {})
                    
                    # Transform the item to match the MenuItem interface
                    transformed_item = {
                        "id": item.get('id', ''),
                        "name": item.get('name', ''),
                        "description": item.get('desc', ''),
                        "price": item.get('price', 0),
                        "is_veg": any(tag == "pure_veg" for tag in item.get('tag_slugs', [])),
                        "spice_level": determine_spice_level(item),
                        "image_url": extract_image_url(item)
                    }
                    
                    # Determine which subcategory this item belongs to
                    assigned = False
                    groups = item.get('groups', [])
                    if groups:
                        for group_entry in groups:
                            group = group_entry.get('group', {})
                            subcategory_name = group.get('name', 'Other')
                            if subcategory_name in subcategories_map:
                                subcategories_map[subcategory_name].append(transformed_item)
                                assigned = True
                                break
                    
                    # If no subcategory was assigned, put in the first available subcategory
                    if not assigned:
                        default_subcategory = next(iter(subcategories_map.keys()))
                        subcategories_map[default_subcategory].append(transformed_item)
                
                # Create the category entry with its subcategories
                category_entry = {
                    "category": menu.get('name', ''),
                    "subcategories": [
                        {
                            "subcategory": subcategory_name,
                            "items": items_list
                        }
                        for subcategory_name, items_list in subcategories_map.items()
                    ]
                }
                
                result["menu"].append(category_entry)
        
        return result
    
    except Exception as e:
        print(f"Error transforming data: {e}")
        # Return a minimal valid structure in case of error
        return {"menu": []}

def determine_spice_level(item):
    """
    Determine the spice level of an item based on available tags or description.
    
    Args:
        item (dict): The menu item data
        
    Returns:
        str: One of 'None', 'Mild', 'Medium', 'Spicy', or 'Hot'
    """
    # Check tags for spice indicators
    tags = item.get('tag_slugs', [])
    desc = item.get('desc', '').lower()
    
    # This is a simple heuristic and could be enhanced based on actual data patterns
    if any(spicy_tag in tags for spicy_tag in ['extra_spicy', 'very_hot']):
        return 'Hot'
    elif any(spicy_tag in tags for spicy_tag in ['spicy', 'hot']):
        return 'Spicy'
    elif any(medium_tag in tags for medium_tag in ['medium_spicy', 'medium_hot']):
        return 'Medium'
    elif any(mild_tag in tags for mild_tag in ['mild_spicy', 'slightly_spicy']):
        return 'Mild'
    
    # Check description for spice indicators
    if any(hot_term in desc for hot_term in ['very spicy', 'extra hot', 'extremely spicy']):
        return 'Hot'
    elif any(spicy_term in desc for spicy_term in ['spicy', 'hot']):
        return 'Spicy'
    elif any(medium_term in desc for medium_term in ['medium spicy', 'moderately spiced']):
        return 'Medium'
    elif any(mild_term in desc for mild_term in ['mild spice', 'slightly spicy']):
        return 'Mild'
    
    # Default value
    return 'None'

def extract_image_url(item):
    """
    Extract the image URL from an item.
    
    Args:
        item (dict): The menu item data
        
    Returns:
        str: The image URL, or None if not available
    """
    # First try to get the specific item image URL
    image_url = item.get('item_image_url')
    if image_url:
        return image_url
    
    # Then check the media array for images
    media = item.get('media', [])
    for media_item in media:
        if media_item.get('mediaType') == 'image':
            image_data = media_item.get('image', {})
            if image_data and image_data.get('url'):
                return image_data.get('url')
    
    # If no image found, return None
    return None

# Example usage:
# transformed_data = transform_restaurant_data(zomato_data)
