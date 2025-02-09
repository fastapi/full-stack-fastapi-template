from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
import json
import requests
from bs4 import BeautifulSoup
import logging
from app.api.deps import SessionDep, get_business_user
from app.models.user import UserBusiness, UserVenueAssociation
from app.models.venue import Venue, Restaurant
from app.models.menu import Menu, MenuCategory, MenuItem
from app.util import create_record

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

class ZomatoUrl(BaseModel):
    url: HttpUrl

def parse_price(price_str: str) -> float:
    """Convert price string to float, handling variations"""
    try:
        cleaned_price = price_str.replace('₹', '').replace(',', '').strip()
        return float(cleaned_price)
    except (ValueError, AttributeError):
        return 0.0

def handle_price_variations(price_data: dict) -> tuple[float, str]:
    """Handle half/full price variations"""
    if isinstance(price_data, dict) and ('half' in price_data or 'full' in price_data):
        description = f"Half: ₹{price_data.get('half', 0)}, Full: ₹{price_data.get('full', 0)}"
        price = price_data.get('full', price_data.get('half', 0))
        return parse_price(price), description
    return parse_price(price_data), ""

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
        
        # Restaurant Info
        basic_info = res_info.get('SECTION_BASIC_INFO', {})
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
                'description': basic_info.get('timing', {}).get('timing_desc'),
                'hours': basic_info.get('timing', {}).get('customised_timings', {}).get('opening_hours', [])
            }
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
                price, price_description = handle_price_variations(item.get('price', 0))
                description = item.get('description', '')
                if price_description:
                    description = f"{description}\n{price_description}" if description else price_description
                
                menu_item = {
                    'id': str(item.get('id')),
                    'name': item.get('name'),
                    'description': description,
                    'price': price,
                    'image_url': item.get('imageUrl', ''),
                    'is_veg': item.get('isVeg', True),
                    'spice_level': item.get('spiceLevel', 'None')
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

def fetch_zomato_data(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        logger.info(f"Fetching data from URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise

def parse_zomato_page(html_content: str) -> dict:
    try:
        logger.debug("Starting page parsing...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        scripts = soup.find_all('script')
        target_script = None
        
        for script in scripts:
            if script.string and 'window.__PRELOADED_STATE__' in script.string:
                target_script = script
                break
        
        if not target_script:
            raise ValueError("Could not find PRELOADED_STATE in page")
        
        json_str = target_script.string.split('window.__PRELOADED_STATE__ = JSON.parse(')[1]
        json_str = json_str.split(');')[0].strip()
        
        json_str = json_str.strip('"')
        json_str = json_str.replace('\\"', '"')
        json_str = json_str.replace('\\\\', '\\')
        json_str = json_str.replace('\\n', '')
        
        return json.loads(json_str)
        
    except Exception as e:
        logger.error(f"Error parsing page: {str(e)}")
        raise

@router.get("/")
async def get_scrapper_info():
    return {"message": "Welcome to Zomato Menu Scraper"}

@router.post("/menu")
async def scrape_and_create_menu(
    request: ZomatoUrl,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_business_user)
):
    try:
        if "zomato.com" not in str(request.url):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL. Please provide a valid Zomato restaurant URL"
            )

        # 1. Scrape data
        html_content = fetch_zomato_data(str(request.url))
        json_data = parse_zomato_page(html_content)
        scraped_data = extract_menu_data(json_data)
        
        if not scraped_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract menu data from Zomato"
            )

        # 2. Create venue
        venue_data = {
            "name": scraped_data["restaurant_info"]["name"],
            "address": scraped_data["restaurant_info"]["location"]["locality"],
            "contact": "",  # Add if available
            "cuisines": scraped_data["restaurant_info"]["cuisines"],
            "rating": scraped_data["restaurant_info"]["rating"]["aggregate_rating"],
            "timing": scraped_data["restaurant_info"]["timing"]["description"]
        }
        
        # Create Venue instance
        venue_instance = Venue.from_create_schema(venue_data)
        create_record(session, venue_instance)
        
        # Create Restaurant instance
        restaurant_instance = Restaurant.from_create_schema(venue_instance.id, venue_data)
        create_record(session, restaurant_instance)
        
        # Create user-venue association
        association = UserVenueAssociation(
            user_id=current_user.id,
            venue_id=venue_instance.id
        )
        create_record(session, association)

        # 3. Create main menu
        menu_data = {
            "name": f"{scraped_data['restaurant_info']['name']} Menu",
            "description": f"Menu imported from Zomato",
            "venue_id": venue_instance.id,
            "is_active": True
        }
        menu_instance = Menu(**menu_data)
        create_record(session, menu_instance)

        # 4. Create categories and items
        for category in scraped_data["menu"]:
            category_data = {
                "name": category["category"],
                "description": f"Category for {category['category']}",
                "menu_id": menu_instance.id
            }
            category_instance = MenuCategory(**category_data)
            create_record(session, category_instance)

            for item in category["items"]:
                item_data = {
                    "name": item["name"],
                    "description": item["description"],
                    "price": float(item["price"]),
                    "category_id": category_instance.id,
                    "is_available": True,
                    "is_vegetarian": item["is_veg"],
                    "image_url": item["image_url"] if item["image_url"] else None
                }
                item_instance = MenuItem(**item_data)
                create_record(session, item_instance)

        return {
            "message": "Menu successfully created",
            "venue_id": venue_instance.id,
            "menu_id": menu_instance.id,
            "restaurant_name": scraped_data["restaurant_info"]["name"]
        }

    except Exception as e:
        session.rollback()
        logger.error(f"Menu creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create menu: {str(e)}"
        )
