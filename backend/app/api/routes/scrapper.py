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
from app.api.routes.utils import transform_restaurant_data

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

class ZomatoUrl(BaseModel):
    url: HttpUrl

def fetch_zomato_data(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
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
        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and 'window.__PRELOADED_STATE__' in script.string:
                json_str = script.string.split('window.__PRELOADED_STATE__ = JSON.parse(')[1]
                json_str = json_str.split(');')[0].strip()
                json_str = json_str.strip('"').replace('\\"', '"').replace('\\\\', '\\')
                return json.loads(json_str)
                
        raise ValueError("Could not find PRELOADED_STATE in page")
    except Exception as e:
        logger.error(f"Error parsing page: {str(e)}")
        raise

def extract_menu_data(json_data: dict) -> dict:
    try:
        with open('data.json', 'w') as f:
            json.dump(json_data, f, indent=4)
        restaurant_data = json_data.get('pages', {}).get('current', {})
        restaurant_details = json_data.get('pages', {}).get('restaurant', {})
        
        restaurant_id = next(iter(restaurant_details)) if restaurant_details else None
        if not restaurant_id:
            raise ValueError("No restaurant ID found")
            
        res_info = restaurant_details[restaurant_id].get('sections', {})
        basic_info = res_info.get('SECTION_BASIC_INFO', {})
        menu_widget = res_info.get('SECTION_MENU_WIDGET', {})


        # Validate required name field
        if not basic_info.get('name'):
            raise ValueError("Restaurant name is required")

        restaurant_info = {
            'cuisine_type': basic_info.get('cuisine_string', ''),
            'venue': {
                'name': basic_info.get('name', ''),
                'address': basic_info.get('address', ''),
                'locality': basic_info.get('locality_verbose', ''),
                'city': basic_info.get('city', ''),
                'latitude': basic_info.get('latitude', '0'),
                'longitude': basic_info.get('longitude', '0'),
                'zipcode': basic_info.get('zipcode', ''),
                'rating': basic_info.get('rating', {}).get('aggregate_rating', '0'),
                'timing': basic_info.get('timing', {}).get('timing', ''),
                'avg_cost_for_two': basic_info.get('average_cost_for_two', 0)
            }
        }


        menu_categories = []
        print("Catorgies", menu_widget.get('menu', {}).get('categories', []))
        for category in menu_widget.get('menu', {}).get('categories', []):
            print("category", category)
            category_data = {
                'name': category.get('name', ''),
                'description': category.get('description', ''),
                'subcategories': []
            }
            
            # Group items by subcategory
            subcategories = {}
            for item in category.get('items', []):
                subcategory_name = item.get('category', 'Other')
                
                if subcategory_name not in subcategories:
                    subcategories[subcategory_name] = {
                        'name': subcategory_name,
                        'description': '',
                        'items': []
                    }
                
                menu_item = {
                    'name': item.get('name', ''),
                    'description': item.get('desc', ''),
                    'is_veg': item.get('isVeg', True),
                    'image_url': item.get('itemImage', ''),
                    'variants': []
                }
                
                # Handle variants
                if item.get('variantsV2'):
                    for variant in item['variantsV2']:
                        menu_item['variants'].append({
                            'name': variant.get('variantName', ''),
                            'price': float(variant.get('price', 0)) / 100,
                            'is_default': variant.get('isDefault', False)
                        })
                else:
                    menu_item['variants'].append({
                        'name': 'Regular',
                        'price': float(item.get('defaultPrice', 0)) / 100,
                        'is_default': True
                    })
                
                subcategories[subcategory_name]['items'].append(menu_item)
            
            # Add non-empty subcategories to category
            category_data['subcategories'] = [
                subcat for subcat in subcategories.values()
                if subcat['items']
            ]
            
            if category_data['subcategories']:
                menu_categories.append(category_data)

        return {
            'status': 'success',
            'restaurant_info': restaurant_info,
            'menu': menu_categories
        }
        
    except Exception as e:
        logger.error(f"Error extracting menu data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract menu data: {str(e)}"
        )


async def create_restaurant(client: httpx.AsyncClient, restaurant_data: RestaurantCreate):
    response = await client.post("/venue/restaurants/", json=restaurant_data.dict())
    response.raise_for_status()
    return response.json()["id"]

async def create_menu(client: httpx.AsyncClient, menu_data: MenuCreate):
    response = await client.post("/menu/", json=menu_data.dict())
    response.raise_for_status()
    return response.json()["menu_id"]

async def create_category(client: httpx.AsyncClient, category_data: MenuCategoryCreate):
    response = await client.post("/menu/category/", json=category_data.dict())
    response.raise_for_status()
    return response.json()["category_id"]

async def create_subcategory(client: httpx.AsyncClient, subcategory_data: MenuSubCategoryCreate):
    response = await client.post("/menu/subcategory/", json=subcategory_data.dict())
    response.raise_for_status()
    return response.json()["subcategory_id"]

async def create_menu_item(client: httpx.AsyncClient, item_data: MenuItemCreate):
    response = await client.post("/menu/item/", json=item_data.dict())
    response.raise_for_status()

@router.post("/menu")
async def scrape_and_create_menu(
    request: ZomatoUrl,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_business_user)
):
    try:
        # 1. Scrape and log data
        html_content = fetch_zomato_data(str(request.url))
        json_data = parse_zomato_page(html_content)
        scraped_data = extract_menu_data(json_data)
        
        logger.info("Scraped Restaurant Info:")
        logger.info(f"Name: {scraped_data['restaurant_info']['name']}")
        logger.info(f"Cuisines: {scraped_data['restaurant_info']['cuisines']}")

        async with httpx.AsyncClient() as client:
            # 2. Create Restaurant
            venue_data = VenueCreate(
                name=scraped_data['restaurant_info']['name'],
                description="Restaurant imported from Zomato",
                avg_expense_for_two=scraped_data['restaurant_info']['avg_cost_for_two'],
                zomato_link=str(request.url)
            )

            restaurant_data = RestaurantCreate(
                venue=venue_data,
                cuisine_type=scraped_data['restaurant_info']['cuisines']
            )

            venue_id = await create_restaurant(client, restaurant_data)
            logger.info(f"Created restaurant with venue_id: {venue_id}")

            # 3. Create Menu
            menu_data = MenuCreate(
                name=f"{scraped_data['restaurant_info']['name']} Menu",
                description="Imported from Zomato",
                venue_id=venue_id,
                menu_type="Food"
            )
            menu_id = await create_menu(client, menu_data)
            logger.info(f"Created menu with menu_id: {menu_id}")

            # 4. Create Categories, Subcategories, and Items sequentially
            for category in scraped_data['menu']:
                category_data = MenuCategoryCreate(
                    name=category['category'],
                    menu_id=menu_id
                )
                category_id = await create_category(client, category_data)
                logger.info(f"Created category: {category['category']}")

                subcategory_data = MenuSubCategoryCreate(
                    name=f"{category['category']} Items",
                    category_id=category_id,
                    is_alcoholic=False
                )
                subcategory_id = await create_subcategory(client, subcategory_data)
                logger.info(f"Created subcategory for {category['category']}")

                for item in category['items']:
                    item_data = MenuItemCreate(
                        name=item['name'],
                        description=item['description'],
                        price=float(item['price']),
                        subcategory_id=subcategory_id,
                        is_veg=item['is_veg'],
                        image_url=item.get('image_url')
                    )
                    await create_menu_item(client, item_data)
                    logger.info(f"Created item: {item['name']}")

            return {
                "message": "Menu successfully created",
                "venue_id": str(venue_id),
                "menu_id": str(menu_id),
                "restaurant_name": scraped_data['restaurant_info']['name'],
                "scraped_data": scraped_data
            }

    except Exception as e:
        logger.error(f"Menu creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create menu: {str(e)}")


@router.get("/menu/scrape")
async def get_scraped_menu(url: str):
    try:
        # Validate URL
        zomato_url = ZomatoUrl(url=url)
        
        # Scrape data using existing functions
        html_content = fetch_zomato_data(str(zomato_url.url))
        json_data = parse_zomato_page(html_content)
        # print(json_data)
        # scraped_data = extract_menu_data(json_data)
        print("==== cleaning the data ====")
        scraped_data = transform_restaurant_data(json_data)
        print(scraped_data)
        
        return {
            "status": "success",
            "restaurant_info": scraped_data,
            "menu": scraped_data['menu']
        }
        
    except ValueError as ve:
        logger.error(f"Invalid URL format: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Zomato URL: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape menu data: {str(e)}"
        )
