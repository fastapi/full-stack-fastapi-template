from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
import json
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, time
from app.api.deps import SessionDep, get_business_user
from app.models.user import UserBusiness, UserVenueAssociation
from app.models.venue import Venue, Restaurant
from app.models.menu import Menu, MenuCategory, MenuSubCategory, MenuItem
from app.util import create_record
from app.schema.venue import RestaurantCreate, VenueCreate
from app.schema.menu import (
    MenuCreate, 
    MenuCategoryCreate, 
    MenuSubCategoryCreate,
    MenuItemCreate
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

class ZomatoUrl(BaseModel):
    url: HttpUrl

def parse_time(time_str: str) -> time:
    """Convert time string to time object"""
    try:
        # Assuming format like "9am – 11:15pm"
        opening_time = time_str.split('–')[0].strip()
        return datetime.strptime(opening_time, '%I%p').time()
    except:
        return None

def extract_menu_data(json_data: dict) -> dict:
    try:
        logger.debug("Starting menu data extraction...")
        restaurant_data = json_data.get('pages', {}).get('current', {})
        restaurant_details = json_data.get('pages', {}).get('restaurant', {})
        
        restaurant_id = next(iter(restaurant_details)) if restaurant_details else None
        
        if not restaurant_id:
            logger.error("No restaurant ID found")
            return {}
            
        res_info = restaurant_details[restaurant_id].get('sections', {})
        basic_info = res_info.get('SECTION_BASIC_INFO', {})

        # Extract timing
        timing_desc = basic_info.get('timing', {}).get('timing_desc', '')
        opening_time = parse_time(timing_desc) if timing_desc else None

        # Restaurant Info
        restaurant_info = {
            'restaurant_id': basic_info.get('res_id'),
            'name': basic_info.get('name'),
            'cuisines': basic_info.get('cuisine_string'),
            'rating': {
                'aggregate_rating': basic_info.get('rating', {}).get('aggregate_rating'),
                'votes': basic_info.get('rating', {}).get('votes'),
                'rating_text': basic_info.get('rating', {}).get('rating_text')
            },
            'location': {
                'locality': restaurant_data.get('pageDescription', ''),
                'url': basic_info.get('resUrl')
            },
            'timing': {
                'description': timing_desc,
                'opening_time': opening_time,
                'hours': basic_info.get('timing', {}).get('customised_timings', {}).get('opening_hours', [])
            },
            'avg_cost_for_two': basic_info.get('costText', {}).get('text', '0').replace('₹', '').replace(',', '').strip()
        }
        
        # Menu Items
        menu_data = res_info.get('SECTION_MENU_WIDGET', {})
        menu_categories = []
        
        for category in menu_data.get('categories', []):
            category_items = {
                'category': category.get('name', ''),
                'items': []
            }
            
            for item in category.get('items', []):
                price_str = str(item.get('price', '0')).replace('₹', '').replace(',', '').strip()
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0
                    
                menu_item = {
                    'id': str(item.get('id')),
                    'name': item.get('name'),
                    'description': item.get('description', ''),
                    'price': price,
                    'image_url': item.get('imageUrl', ''),
                    'is_veg': item.get('isVeg', True),
                }
                category_items['items'].append(menu_item)
            
            if category_items['items']:
                menu_categories.append(category_items)
        
        return {
            'restaurant_info': restaurant_info,
            'menu': menu_categories
        }

    except Exception as e:
        logger.error(f"Error extracting menu data: {str(e)}")
        return {}

# ... keep your existing fetch_zomato_data and parse_zomato_page functions ...

@router.post("/menu")
async def scrape_and_create_menu(
    request: ZomatoUrl,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_business_user)
):
    try:
        # 1. Scrape data
        html_content = fetch_zomato_data(str(request.url))
        json_data = parse_zomato_page(html_content)
        scraped_data = extract_menu_data(json_data)
        
        if not scraped_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract menu data from Zomato"
            )

        # 2. Create Restaurant with Venue
        venue_data = VenueCreate(
            name=scraped_data['restaurant_info']['name'],
            description=f"Restaurant imported from Zomato",
            mobile_number=None,  # Add if available in scraped data
            email=None,  # Add if available
            opening_time=scraped_data['restaurant_info']['timing']['opening_time'],
            avg_expense_for_two=float(scraped_data['restaurant_info']['avg_cost_for_two']),
            zomato_link=str(request.url)
        )

        restaurant_data = RestaurantCreate(
            venue=venue_data,
            cuisine_type=scraped_data['restaurant_info']['cuisines']
        )

        # Create venue and restaurant
        venue_instance = Venue.from_create_schema(restaurant_data.venue)
        create_record(session, venue_instance)
        
        restaurant_instance = Restaurant.from_create_schema(venue_instance.id, restaurant_data)
        create_record(session, restaurant_instance)
        
        # Create association
        association = UserVenueAssociation(
            user_id=current_user.id,
            venue_id=venue_instance.id
        )
        create_record(session, association)

        # 3. Create Menu
        menu_data = MenuCreate(
            name=f"{scraped_data['restaurant_info']['name']} Menu",
            description="Imported from Zomato",
            venue_id=venue_instance.id,
            menu_type="Food"
        )
        menu_instance = Menu(**menu_data.dict())
        create_record(session, menu_instance)

        # 4. Create Categories, Subcategories, and Items
        for category in scraped_data['menu']:
            # Create Category
            category_data = MenuCategoryCreate(
                name=category['category'],
                menu_id=menu_instance.id
            )
            category_instance = MenuCategory(**category_data.dict())
            create_record(session, category_instance)

            # Create default subcategory for each category
            subcategory_data = MenuSubCategoryCreate(
                name=f"{category['category']} Items",
                category_id=category_instance.id,
                is_alcoholic=False  # Default value
            )
            subcategory_instance = MenuSubCategory(**subcategory_data.dict())
            create_record(session, subcategory_instance)

            # Create items under subcategory
            for item in category['items']:
                item_data = MenuItemCreate(
                    name=item['name'],
                    description=item['description'],
                    price=float(item['price']),
                    subcategory_id=subcategory_instance.id,
                    is_veg=item['is_veg'],
                    image_url=item['image_url'] if item['image_url'] else None
                )
                item_instance = MenuItem(**item_data.dict())
                create_record(session, item_instance)

        return {
            "message": "Menu successfully created",
            "venue_id": str(venue_instance.id),
            "menu_id": str(menu_instance.id),
            "restaurant_name": scraped_data['restaurant_info']['name']
        }

    except Exception as e:
        session.rollback()
        logger.error(f"Menu creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create menu: {str(e)}"
        )
