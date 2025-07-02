// Types for Property Management System
// Comprehensive TypeScript interfaces for GENIUS INDUSTRIES CRM

export type PropertyType = 
  | 'apartment' 
  | 'house' 
  | 'commercial' 
  | 'land' 
  | 'office' 
  | 'warehouse' 
  | 'local' 
  | 'penthouse' 
  | 'studio';

export type PropertyStatus = 
  | 'available' 
  | 'reserved' 
  | 'sold' 
  | 'rented' 
  | 'under_construction' 
  | 'maintenance' 
  | 'off_market';

export type Currency = 'COP' | 'USD' | 'EUR';

export type OwnerType = 'own' | 'third_party';

export type TransactionType = 'sale' | 'rent' | 'lease' | 'commission';

export interface Address {
  id: string;
  street: string;
  number: string;
  complement?: string;
  neighborhood: string;
  city: string;
  state: string;
  country: string;
  postal_code?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

export interface Price {
  id: string;
  amount: number;
  currency: Currency;
  type: 'sale' | 'rent_monthly' | 'rent_daily';
  includes_utilities?: boolean;
  includes_admin?: boolean;
  admin_fee?: number;
  negotiable: boolean;
  last_updated: string;
}

export interface PropertyFeatures {
  area_total: number;
  area_built: number;
  bedrooms: number;
  bathrooms: number;
  parking_spaces: number;
  storage_rooms: number;
  balconies: number;
  terraces: number;
  floor_number?: number;
  total_floors?: number;
  stratum: number;
  construction_year: number;
  furnished: boolean;
  pet_friendly: boolean;
  has_elevator: boolean;
  has_pool: boolean;
  has_gym: boolean;
  has_garden: boolean;
  has_bbq_area: boolean;
  has_playground: boolean;
  has_security: boolean;
  has_concierge: boolean;
}

export interface PropertyDocuments {
  id: string;
  property_id: string;
  type: 'deed' | 'tax_certificate' | 'utility_bills' | 'rental_contract' | 'photos' | 'floor_plan' | 'legal_study';
  name: string;
  url: string;
  uploaded_at: string;
  uploaded_by: string;
  verified: boolean;
  verification_date?: string;
}

export interface PropertyOwner {
  id: string;
  type: OwnerType;
  // Personal/Company Info
  name: string;
  email: string;
  phone: string;
  document_type: 'CC' | 'CE' | 'NIT' | 'Passport';
  document_number: string;
  address?: Address;
  
  // Business Info (for third party)
  company_name?: string;
  contact_person?: string;
  commission_rate?: number; // Porcentaje de comisión para terceros
  
  // Financial Info
  bank_account?: {
    bank_name: string;
    account_type: 'savings' | 'checking';
    account_number: string;
  };
  
  // Metadata
  created_at: string;
  updated_at: string;
  active: boolean;
  notes?: string;
}

export interface PropertyTransaction {
  id: string;
  property_id: string;
  type: TransactionType;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  
  // Parties
  buyer_client_id?: string;
  seller_owner_id: string;
  agent_id: string;
  lawyer_id?: string;
  
  // Financial Details
  agreed_price: Price;
  commission_rate: number;
  commission_amount: number;
  down_payment?: number;
  financing_amount?: number;
  
  // Important Dates
  start_date: string;
  expected_closing_date: string;
  actual_closing_date?: string;
  key_delivery_date?: string;
  
  // Documentation
  contract_signed: boolean;
  contract_date?: string;
  documents: PropertyDocuments[];
  
  // Notes and Updates
  notes?: string;
  status_history: Array<{
    status: string;
    date: string;
    notes?: string;
    updated_by: string;
  }>;
  
  created_at: string;
  updated_at: string;
}

export interface Property {
  id: string;
  title: string;
  description: string;
  type: PropertyType;
  status: PropertyStatus;
  
  // Location
  address: Address;
  
  // Owner Information
  owner: PropertyOwner;
  
  // Features and Details
  features: PropertyFeatures;
  
  // Pricing
  prices: Price[];
  current_price: Price;
  
  // Media
  images: Array<{
    id: string;
    url: string;
    alt_text: string;
    is_primary: boolean;
    order: number;
  }>;
  virtual_tour_url?: string;
  video_url?: string;
  
  // Documentation
  documents: PropertyDocuments[];
  
  // Legal and Financial
  property_tax_annual: number;
  administration_fee?: number;
  utilities_included: string[];
  rental_conditions?: {
    minimum_stay_months: number;
    deposit_months: number;
    advance_payment_months: number;
    guarantor_required: boolean;
    income_verification_required: boolean;
  };
  
  // Marketing
  highlighted: boolean;
  featured: boolean;
  published: boolean;
  publication_date?: string;
  expiration_date?: string;
  views_count: number;
  favorites_count: number;
  
  // Agent/Management
  assigned_agent_id: string;
  listing_agent_id: string;
  created_by: string;
  
  // Metadata
  created_at: string;
  updated_at: string;
  last_modified_by: string;
  
  // Relations
  transactions: PropertyTransaction[];
  visits_scheduled: number;
  inquiries_count: number;
}

export interface PropertyFilters {
  // Basic Filters
  type?: PropertyType[];
  status?: PropertyStatus[];
  price_min?: number;
  price_max?: number;
  currency?: Currency;
  
  // Location
  city?: string[];
  neighborhood?: string[];
  stratum?: number[];
  
  // Features
  bedrooms_min?: number;
  bedrooms_max?: number;
  bathrooms_min?: number;
  bathrooms_max?: number;
  parking_min?: number;
  area_min?: number;
  area_max?: number;
  
  // Owner
  owner_type?: OwnerType[];
  owner_id?: string;
  
  // Amenities
  has_pool?: boolean;
  has_gym?: boolean;
  has_elevator?: boolean;
  pet_friendly?: boolean;
  furnished?: boolean;
  
  // Business
  highlighted?: boolean;
  featured?: boolean;
  assigned_agent_id?: string;
  
  // Dates
  created_after?: string;
  created_before?: string;
  updated_after?: string;
}

export interface PropertySortOptions {
  field: 'price' | 'created_at' | 'updated_at' | 'area' | 'bedrooms' | 'views_count' | 'title';
  direction: 'asc' | 'desc';
}

export interface PropertySearchParams {
  query?: string;
  filters?: PropertyFilters;
  sort?: PropertySortOptions;
  page?: number;
  limit?: number;
}

export interface PropertyAnalytics {
  // Overview
  total_properties: number;
  available_properties: number;
  sold_properties: number;
  rented_properties: number;
  
  // Financial
  total_inventory_value: number;
  average_property_price: number;
  total_sales_this_month: number;
  total_rentals_this_month: number;
  commission_earned_this_month: number;
  
  // Performance
  average_days_on_market: number;
  conversion_rate: number;
  most_viewed_properties: Property[];
  top_performing_agents: Array<{
    agent_id: string;
    agent_name: string;
    properties_sold: number;
    total_commission: number;
  }>;
  
  // Market Trends
  price_trends: Array<{
    date: string;
    average_price: number;
    currency: Currency;
  }>;
  
  // Geographic Distribution
  properties_by_city: Array<{
    city: string;
    count: number;
    average_price: number;
  }>;
  
  properties_by_type: Array<{
    type: PropertyType;
    count: number;
    percentage: number;
  }>;
}

export interface CurrencyRates {
  USD_TO_COP: number;
  EUR_TO_COP: number;
  COP_TO_USD: number;
  COP_TO_EUR: number;
  EUR_TO_USD: number;
  USD_TO_EUR: number;
  last_updated: string;
}

// API Response Types
export interface PropertyResponse {
  data: Property[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface PropertyCreateRequest {
  title: string;
  description: string;
  type: PropertyType;
  address: Omit<Address, 'id'>;
  owner_id: string;
  features: PropertyFeatures;
  prices: Omit<Price, 'id'>[];
  images?: Array<{
    url: string;
    alt_text: string;
    is_primary: boolean;
  }>;
  highlighted?: boolean;
  featured?: boolean;
}

export interface PropertyUpdateRequest extends Partial<PropertyCreateRequest> {
  status?: PropertyStatus;
}

// Error Types
export interface PropertyError {
  code: string;
  message: string;
  field?: string;
}

// Utility Types
export type PropertyFormData = Omit<Property, 'id' | 'created_at' | 'updated_at' | 'owner' | 'transactions'> & {
  owner_id: string;
};

export type OwnerFormData = Omit<PropertyOwner, 'id' | 'created_at' | 'updated_at'>;

export type TransactionFormData = Omit<PropertyTransaction, 'id' | 'created_at' | 'updated_at' | 'status_history'>; 