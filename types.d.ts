interface RestaurantMenuResponse {
    status: 'success' | 'error';
    restaurant_info: {
      cuisine_type: string;
      venue: {
        name: string;
        address: string;
        locality: string;
        city: string;
        latitude: string;
        longitude: string;
        zipcode: string;
        rating: string;
        timing: string;
        avg_cost_for_two: number;
      };
    };
    menu: Array<{
      name: string;
      description: string;
      subcategories: Array<{
        name: string;
        description: string;
        items: Array<{
          name: string;
          description: string;
          is_veg: boolean;
          image_url: string;
          variants: Array<{
            name: string;
            price: number;
            is_default: boolean;
          }>;
        }>;
      }>;
    }>;
  }
  



  interface MenuItem {
    id: string;
    name: string;
    description: string;
    price: number;
    is_veg: boolean;
    spice_level: 'None' | 'Mild' | 'Medium' | 'Spicy' | 'Hot';
    image_url: any; // Using 'any' for image imports, could be refined based on your setup
  }
  
  interface MenuSubcategory {
    subcategory: string;
    items: MenuItem[];
  }
  
  interface MenuCategory {
    category: string;
    subcategories: MenuSubcategory[];
  }
  
  interface MenuData {
    menu: MenuCategory[];
  }
  
  // Assuming isWeb is defined elsewhere in your codebase
  declare const isWeb: boolean;