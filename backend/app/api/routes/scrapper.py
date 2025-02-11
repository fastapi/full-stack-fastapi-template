from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
import json
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, time
import httpx
from app.api.deps import SessionDep, get_business_user
from app.models.user import UserBusiness
from app.schema.venue import RestaurantCreate, VenueCreate
from app.schema.menu import (
    MenuCreate, 
    MenuCategoryCreate, 
    MenuSubCategoryCreate,
    MenuItemCreate
)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

class ZomatoUrl(BaseModel):
    url: HttpUrl

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
        json_str = json_str.strip('"').replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '')
        
        return json.loads(json_str)
        
    except Exception as e:
        logger.error(f"Error parsing page: {str(e)}")
        raise

def extract_menu_data(json_data: dict) -> dict:
    try:
        logger.debug("Starting menu data extraction...")
        restaurant_data = json_data.get('pages', {}).get('current', {})
        restaurant_details = json_data.get('pages', {}).get('restaurant', {})
        
        restaurant_id = next(iter(restaurant_details)) if restaurant_details else None
        if not restaurant_id:
            raise ValueError("No restaurant ID found")
            
        res_info = restaurant_details[restaurant_id].get('sections', {})
        basic_info = res_info.get('SECTION_BASIC_INFO', {})
        
        restaurant_info = {
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
        
        menu_categories = []
        menu_data = res_info.get('SECTION_MENU_WIDGET', {})
        
        for category in menu_data.get('categories', []):
            category_items = {
                'category': category.get('name', ''),
                'items': []
            }
            
            for item in category.get('items', []):
                menu_item = {
                    'name': item.get('name'),
                    'description': item.get('description', ''),
                    'price': float(item.get('price', 0)),
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
        raise

async def create_restaurant(client: httpx.AsyncClient, restaurant_data:
