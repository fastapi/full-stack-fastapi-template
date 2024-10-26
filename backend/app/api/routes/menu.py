import uuid
from app.schema.menu import MenuCategoryCreate, MenuCategoryRead, MenuCategoryUpdate, MenuCreate, MenuItemCreate, MenuItemRead, MenuItemUpdate, MenuRead, MenuSubCategoryCreate, MenuSubCategoryRead, MenuSubCategoryUpdate, MenuUpdate
from app.models.menu import Menu, MenuCategory, MenuItem, MenuSubCategory
from app.models.venue import Venue
from app.models.user import UserBusiness, UserPublic, UserVenueAssociation
from sqlmodel import Session,select
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import SessionDep, get_current_user
from app.util import (
    get_record_by_id,
    create_record,
    update_record,
    delete_record,
    check_user_permission
)
from app.api.deps import get_db 
router = APIRouter()

# Get all menus of a specific venue
@router.get("/all/{venue_id}", response_model=List[MenuRead])
async def read_menus(venue_id: uuid.UUID, db: Session = Depends(get_db),
                     current_user: UserPublic = Depends(get_current_user)):
    """
    Retrieve all menus for a specific venue.
    """
    # Query the Menu table for menus associated with the specified venue
    statement = select(Menu).where(Menu.venue_id == venue_id)
    menus = db.execute(statement).scalars().all()  # Execute the query
    
    if not menus:
        raise HTTPException(status_code=404, detail="No menus found for this venue.")
    
    return [Menu.to_read_schema(menu) for menu in menus]

@router.get("/menu/{menu_id}", response_model=MenuRead)
async def read_menu(menu_id: uuid.UUID, db: Session = Depends(get_db),
                    current_user: UserPublic = Depends(get_current_user)):
    """
    Retrieve a specific menu by its ID.
    """
    menu = get_record_by_id(db, Menu, menu_id)
    ret =  Menu.to_read_schema(menu)
    return ret


@router.post("/", response_model=MenuRead)
async def create_menu(menu_create: MenuCreate, db: Session = Depends(get_db),
                      current_user: UserBusiness = Depends(get_current_user)):
    """
    Create a new menu for a specific venue.
    """
    # Check if the venue exists
    venue = get_record_by_id(db, Venue, menu_create.venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found.")
    
    # Check if the user has permission to create a menu for this venue
    check_user_permission(db, current_user, menu_create.venue_id)
    
    try:
        # Create the Menu object
        menu_instance = Menu.from_create_schema(menu_create)

        # Use the create_record helper to save the menu to the database
        created_menu = create_record(db, menu_instance)

        return Menu.to_read_schema(created_menu)
    
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=400, detail=f"Error creating menu: {str(e)}")

@router.patch("/{menu_id}", response_model=MenuRead)
async def update_menu(
    menu_id: uuid.UUID, 
    menu_update: MenuUpdate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)
):
    """
    Update an existing menu's details using a partial update (PATCH).
    
    :param menu_id: The ID of the menu to update.
    :param menu_update: The fields to update, provided as a Pydantic model.
    :param db: Active database session.
    :return: The updated Menu as a response.
    """
    # Retrieve the menu by its ID
    menu_instance = get_record_by_id(db, Menu, menu_id)
    # Check if the user has permission to update a menu for this venue
    check_user_permission(db, current_user, menu_instance.venue_id)
    
    if not menu_instance:
        raise HTTPException(status_code=404, detail="Menu not found.")
    
    # Update the menu using the validated fields from MenuUpdate
    updated_menu = update_record(db, menu_instance, menu_update)
    
    return Menu.to_read_schema(updated_menu)

@router.delete("/{menu_id}", response_model=dict)
async def delete_menu(menu_id: uuid.UUID, db: Session = Depends(get_db),
                      current_user: UserBusiness = Depends(get_current_user)):
    """
    Delete a menu by its ID.

    :param menu_id: The ID of the menu to delete.
    :param db: Active database session.
    :return: Confirmation message on successful deletion.
    """
    menu_instance = get_record_by_id(db, Menu, menu_id)
    if not menu_instance:
        raise HTTPException(status_code=404, detail="Menu not found.")

    # Check if the user has permission to delete a menu for this venue
    check_user_permission(db, current_user, menu_instance.venue_id)

    delete_record(db, menu_instance)
    
    return {"detail": "Menu deleted successfully."}

##############################################################################################################

@router.post("/category", response_model=MenuCategoryRead)
async def create_menu_category(
    category_create: MenuCategoryCreate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)):
    """
    Create a new menu category associated with a menu.
    
    :param category_create: The details for the new menu category, provided as a Pydantic model.
    :param db: Active database session.
    :return: The created MenuCategory as a response.
    """
    # Check if the menu exists
    menu = get_record_by_id(db, Menu, category_create.menu_id)
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")
    # Check if the user has permission to update a menu for this venue
    check_user_permission(db, current_user, menu.venue_id)
    
    # Create a new MenuCategory instance from the provided data
    category_instance = MenuCategory.from_create_schema(category_create)
    
    # Persist the new category in the database
    created_category = create_record(db, category_instance)
    
    return MenuCategory.to_read_schema(created_category)

@router.patch("/category/{category_id}", response_model=MenuCategoryRead)
async def update_menu_category(
    category_id: uuid.UUID, 
    category_update: MenuCategoryUpdate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)):
    
    """
    Update an existing menu category's details using a partial update (PATCH).
    
    :param category_id: The ID of the menu category to update.
    :param category_update: The fields to update, provided as a Pydantic model.
    :param db: Active database session.
    :return: The updated MenuCategory as a response.
    """
    # Retrieve the category by its ID
    category_instance = get_record_by_id(db, MenuCategory, category_id)
    
    if not category_instance:
        raise HTTPException(status_code=404, detail="Menu category not found.")
    
    check_user_permission(db, current_user, category_instance.menu.venue_id)

    # Update the category using the validated fields from MenuCategoryUpdate
    updated_category = update_record(db, category_instance, category_update)
    
    return MenuCategory.to_read_schema(updated_category)

@router.delete("/category/{category_id}", response_model=dict)
async def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db),
                          current_user: UserBusiness = Depends(get_current_user)):
    """
    Delete a menu category by its ID.

    :param category_id: The ID of the category to delete.
    :param db: Active database session.
    :return: Confirmation message on successful deletion.
    """
    category = get_record_by_id(db, MenuCategory, category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    check_user_permission(db, current_user, category.menu.venue_id)

    delete_record(db, category)
    
    return {"detail": "Category deleted successfully."}

##############################################################################################################

@router.post("/subcategory/", response_model=MenuSubCategoryRead)
async def create_menu_subcategory(
    subcategory_create: MenuSubCategoryCreate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)):
    """
    Create a new menu subcategory associated with a category.
    
    :param subcategory_create: The details for the new menu subcategory, provided as a Pydantic model.
    :param db: Active database session.
    :return: The created MenuSubCategory as a response.
    """
    # Check if the category exists
    category = get_record_by_id(db, MenuCategory, subcategory_create.category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    check_user_permission(db, current_user, category.menu.venue_id)

    # Create a new MenuSubCategory instance from the provided data
    subcategory_instance = MenuSubCategory.from_create_schema(subcategory_create)
    
    # Persist the new subcategory in the database
    created_subcategory = create_record(db, subcategory_instance)
    
    return MenuSubCategory.to_read_schema(created_subcategory)

@router.patch("/subcategory/{subcategory_id}", response_model=MenuSubCategoryRead)
async def update_menu_subcategory(
    subcategory_id: uuid.UUID, 
    subcategory_update: MenuSubCategoryUpdate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)):
    """
    Update an existing menu subcategory.

    :param subcategory_id: The unique identifier for the subcategory to update.
    :param subcategory_update: The details to update, provided as a Pydantic model.
    :param db: Active database session.
    :return: The updated MenuSubCategory as a response.
    """
    # Check if the subcategory exists
    subcategory = get_record_by_id(db, MenuSubCategory, subcategory_id)
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found.")

    check_user_permission(db, current_user, subcategory.category.menu.venue_id)
    
    # Update the subcategory with provided data
    update_data = subcategory_update.dict(exclude_unset=True)  # Exclude unset fields for partial update
    updated_subcategory = update_record(db, subcategory, update_data)
    
    return MenuSubCategory.to_read_schema(updated_subcategory)

@router.delete("/subcategory/{subcategory_id}", response_model=dict)
async def delete_subcategory(subcategory_id: uuid.UUID, db: Session = Depends(get_db),
                             current_user: UserBusiness = Depends(get_current_user)):
    """
    Delete a menu subcategory by its ID.

    :param subcategory_id: The ID of the subcategory to delete.
    :param db: Active database session.
    :return: Confirmation message on successful deletion.
    """
    subcategory = get_record_by_id(db, MenuSubCategory, subcategory_id)
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found.")
    
    check_user_permission(db, current_user, subcategory.category.menu.venue_id)

    delete_record(db, subcategory)
    
    return {"detail": "Subcategory deleted successfully."}

##############################################################################################################

@router.post("/item/", response_model=MenuItemRead)
async def create_menu_item(
    item_create: MenuItemCreate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)):
    """
    Create a new menu item associated with a subcategory.

    :param item_create: The details for the new menu item, provided as a Pydantic model.
    :param db: Active database session.
    :return: The created MenuItem as a response.
    """
    # Check if the subcategory exists
    subcategory = get_record_by_id(db, MenuSubCategory, item_create.subcategory_id)
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found.")
    
    check_user_permission(db, current_user, subcategory.category.menu.venue_id)

    # Create a new MenuItem instance from the provided data
    item_instance = MenuItem.from_create_schema(item_create)
    
    # Persist the new item in the database
    created_item = create_record(db, item_instance)
    
    return MenuItem.to_read_schema(created_item)

@router.patch("/item/{item_id}", response_model=MenuItemRead)
async def update_menu_item(
    item_id: uuid.UUID, 
    item_update: MenuItemUpdate, 
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user)):
    """
    Update an existing menu item.

    :param item_id: The unique identifier for the item to update.
    :param item_update: The details to update, provided as a Pydantic model.
    :param db: Active database session.
    :return: The updated MenuItem as a response.
    """
    # Check if the item exists
    item = get_record_by_id(db, MenuItem, item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found.")

    check_user_permission(db, current_user, item.subcategory.category.menu.venue_id)

    # Update the item with provided data
    updated_item = update_record(db, item, item_update)
    
    return MenuItem.to_read_schema(updated_item)

@router.delete("/item/{item_id}", response_model=dict)
async def delete_menu_item(item_id: uuid.UUID, db: Session = Depends(get_db),
                           current_user: UserBusiness = Depends(get_current_user)):
    """
    Delete a menu item by its ID.

    :param item_id: The ID of the item to delete.
    :param db: Active database session.
    :return: Confirmation message on successful deletion.
    """
    item = get_record_by_id(db, MenuItem, item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found.")

    check_user_permission(db, current_user, item.subcategory.category.menu.venue_id)

    delete_record(db, item)
    
    return {"detail": "Menu item deleted successfully."}

#########################################################################################################