from app.schema.menu import MenuCategoryRead, MenuItemRead, NightclubMenuCreate, NightclubMenuRead, MenuCategoryCreate, MenuItemCreate, QSRMenuCreate, QSRMenuRead, RestaurantMenuCreate, RestaurantMenuRead
from app.models.menu import NightclubMenu, QSRMenu, RestaurantMenu
from app.models.menu_category import MenuCategory
from app.models.menu_item import MenuItem
from sqlmodel import select
from fastapi import APIRouter
from typing import List
from app.api.deps import SessionDep
from app.crud import (
    get_record_by_id,
    create_record,
    update_record,
    patch_record,
    delete_record
)

router = APIRouter()

# Get all menus for a nightclub
@router.get("/nightclubs/{nightclub_id}/menus/", response_model=List[NightclubMenuRead])
def read_nightclub_menus(nightclub_id: int, session: SessionDep):
    """
    Retrieve all menus for a specific nightclub.
    """
    menus = session.exec(select(NightclubMenu).where(NightclubMenu.nightclub_id == nightclub_id)).all()
    return menus

# Get a specific menu
@router.get("/nightclubs/menus/{menu_id}", response_model=NightclubMenuRead)
def read_nightclub_menu(menu_id: int, session: SessionDep):
    """
    Retrieve a specific menu by ID for a nightclub.
    """
    return get_record_by_id(session, NightclubMenu, menu_id)

# Create a new menu
@router.post("/nightclubs/menus/", response_model=NightclubMenuRead)
def create_nightclub_menu( menu: NightclubMenuCreate, session: SessionDep):
    """
    Create a new menu for a nightclub.
    """
    return create_record(session, NightclubMenu, menu)

# Update a menu
@router.put("/nightclubs/menus/{menu_id}", response_model=NightclubMenuRead)
def update_nightclub_menu(menu_id: int, updated_menu: NightclubMenuCreate, session: SessionDep):
    """
    Update an existing menu for a nightclub.
    """
    return update_record(session, NightclubMenu, menu_id, updated_menu)

# PATCH a menu for partial updates
@router.patch("/nightclubs/menus/{menu_id}", response_model=NightclubMenuRead)
def patch_nightclub_menu(menu_id: int, updated_menu: NightclubMenuCreate, session: SessionDep):
    """
    Partially update an existing menu for a venue (Nightclub, Restaurant, QSR).
    """
    return patch_record(session, NightclubMenu, menu_id, updated_menu)

# Delete a menu
@router.delete("/nightclubs/menus/{menu_id}", response_model=None)
def delete_nightclub_menu(menu_id: int, session: SessionDep):
    """
    Delete a menu by ID for a nightclub.
    """
    return delete_record(session, NightclubMenu, menu_id)

# Get all menus for a qsr
@router.get("/qsrs/{qsr_id}/menus/", response_model=List[QSRMenuRead])
def read_qsr_menus(qsr_id: int, session: SessionDep):
    """
    Retrieve all menus for a specific qsr.
    """
    menus = session.exec(select(QSRMenu).where(QSRMenu.qsr_id == qsr_id)).all()
    return menus

# Get a specific menu
@router.get("/qsrs/menus/{menu_id}", response_model=QSRMenuRead)
def read_qsr_menu(menu_id: int, session: SessionDep):
    """
    Retrieve a specific menu by ID for a qsr.
    """
    return get_record_by_id(session, QSRMenu, menu_id)

# Create a new menu
@router.post("/qsrs/menus/", response_model=QSRMenuRead)
def create_qsr_menu( menu: QSRMenuCreate, session: SessionDep):
    """
    Create a new menu for a qsr.
    """
    return create_record(session, QSRMenu, menu)

# Update a menu
@router.put("/qsrs/menus/{menu_id}", response_model=QSRMenuRead)
def update_qsr_menu(menu_id: int, updated_menu: QSRMenuCreate, session: SessionDep):
    """
    Update an existing menu for a qsr.
    """
    return update_record(session, QSRMenu, menu_id, updated_menu)

# PATCH a menu for partial updates
@router.patch("/qsrs/menus/{menu_id}", response_model=QSRMenuRead)
def patch_qsr_menu(menu_id: int, updated_menu: QSRMenuCreate, session: SessionDep):
    """
    Partially update an existing menu for a venue (QSR, Restaurant, QSR).
    """
    return patch_record(session, QSRMenu, menu_id, updated_menu)

# Delete a menu
@router.delete("/qsrs/menus/{menu_id}", response_model=None)
def delete_qsr_menu(menu_id: int, session: SessionDep):
    """
    Delete a menu by ID for a qsr.
    """
    return delete_record(session, QSRMenu, menu_id)

# Get all menus for a restaurant
@router.get("/restaurants/{restaurant_id}/menus/", response_model=List[RestaurantMenuRead])
def read_restaurant_menus(restaurant_id: int, session: SessionDep):
    """
    Retrieve all menus for a specific restaurant.
    """
    menus = session.exec(select(RestaurantMenu).where(RestaurantMenu.restaurant_id == restaurant_id)).all()
    return menus

# Get a specific menu
@router.get("/restaurants/menus/{menu_id}", response_model=RestaurantMenuRead)
def read_restaurant_menu(menu_id: int, session: SessionDep):
    """
    Retrieve a specific menu by ID for a restaurant.
    """
    return get_record_by_id(session, RestaurantMenu, menu_id)

# Create a new menu
@router.post("/restaurants/menus/", response_model=RestaurantMenuRead)
def create_restaurant_menu( menu: RestaurantMenuCreate, session: SessionDep):
    """
    Create a new menu for a restaurant.
    """
    return create_record(session, RestaurantMenu, menu)

# Update a menu
@router.put("/restaurants/menus/{menu_id}", response_model=RestaurantMenuRead)
def update_restaurant_menu(menu_id: int, updated_menu: RestaurantMenuCreate, session: SessionDep):
    """
    Update an existing menu for a restaurant.
    """
    return update_record(session, RestaurantMenu, menu_id, updated_menu)

# PATCH a menu for partial updates
@router.patch("/restaurants/menus/{menu_id}", response_model=RestaurantMenuRead)
def patch_restaurant_menu(menu_id: int, updated_menu: RestaurantMenuCreate, session: SessionDep):
    """
    Partially update an existing menu for a venue (Restaurant, Restaurant, QSR).
    """
    return patch_record(session, RestaurantMenu, menu_id, updated_menu)

# Delete a menu
@router.delete("/restaurants/menus/{menu_id}", response_model=None)
def delete_restaurant_menu(menu_id: int, session: SessionDep):
    """
    Delete a menu by ID for a restaurant.
    """
    return delete_record(session, RestaurantMenu, menu_id)

# CRUD operations for Menu Categories

# Create a new category
@router.post("/nightclubs/menus/categories/", response_model=MenuCategoryRead)
def create_menu_category(category: MenuCategoryCreate, session: SessionDep):
    return create_record(session, MenuCategory, category)

# Update a category
@router.put("/nightclubs/menus/categories/{category_id}", response_model=MenuCategoryRead)
def update_menu_category(category_id: int, updated_category: MenuCategoryCreate, session: SessionDep):
    """
    Update an existing category for a specific menu.
    """
    return update_record(session, MenuCategory, category_id, updated_category)

# Delete a category
@router.delete("/nightclubs/menus/categories/{category_id}", response_model=None)
def delete_menu_category(category_id: int, session: SessionDep):
    """
    Delete a category by ID from a specific menu.
    """
    return delete_record(session, MenuCategory, category_id)

# CRUD operations for Menu Items

# Create a new item
@router.post("/nightclubs/menus/categories/items/", response_model=MenuItemRead)
def create_menu_item(item: MenuItemCreate, session: SessionDep):
    return create_record(session, MenuItem, item)

# Update an item
@router.put("/nightclubs/menus/categories/items/{item_id}", response_model=MenuItemRead)
def update_menu_item(item_id: int, updated_item: MenuItemCreate, session: SessionDep):
    """
    Update an existing item under a specific category of a menu.
    """
    return update_record(session, MenuItem, item_id, updated_item)

# Delete an item
@router.delete("/nightclubs/menus/categories/items/{item_id}", response_model=None)
def delete_menu_item(item_id: int, session: SessionDep):
    """
    Delete an item by ID from a specific category of a menu.
    """
    return delete_record(session, MenuItem, item_id)