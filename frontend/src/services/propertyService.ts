import { 
  Property, 
  PropertyFilters, 
  PropertySearchParams, 
  PropertyResponse, 
  PropertyCreateRequest, 
  PropertyUpdateRequest,
  PropertyError,
  PropertyAnalytics,
  PropertySortOptions,
  PropertyType,
  PropertyStatus,
  Currency
} from '../types/property';
import { currencyService } from './currencyService';

// Configuración del API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_ENDPOINTS = {
  properties: '/api/v1/properties',
  analytics: '/api/v1/properties/analytics',
  owners: '/api/v1/property-owners',
  transactions: '/api/v1/property-transactions',
};

class PropertyService {
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutos

  constructor() {
    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    // Asegurar que el servicio de divisas esté inicializado
    await currencyService.updateRates();
  }

  /**
   * Maneja las solicitudes HTTP al backend
   */
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        // Aquí agregaríamos headers de autenticación cuando esté disponible
        // 'Authorization': `Bearer ${token}`,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          message: `HTTP ${response.status}: ${response.statusText}` 
        }));
        
        throw new PropertyError({
          code: `HTTP_${response.status}`,
          message: errorData.message || `Error ${response.status}`,
          field: errorData.field,
        });
      }

      return await response.json();
    } catch (error) {
      if (error instanceof PropertyError) {
        throw error;
      }
      
      // Error de red o parsing
      throw new PropertyError({
        code: 'NETWORK_ERROR',
        message: error instanceof Error ? error.message : 'Error de conexión',
      });
    }
  }

  /**
   * Genera una clave de cache basada en parámetros
   */
  private getCacheKey(endpoint: string, params?: any): string {
    if (!params) return endpoint;
    return `${endpoint}_${JSON.stringify(params)}`;
  }

  /**
   * Obtiene datos del cache si están disponibles y son recientes
   */
  private getCachedData<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    const isExpired = Date.now() - cached.timestamp > this.CACHE_DURATION;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data as T;
  }

  /**
   * Guarda datos en el cache
   */
  private setCachedData<T>(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Limpia el cache (útil después de crear/actualizar/eliminar)
   */
  private clearCache(): void {
    this.cache.clear();
  }

  /**
   * Construye query string para filtros
   */
  private buildQueryString(params: PropertySearchParams): string {
    const queryParams = new URLSearchParams();
    
    if (params.query) {
      queryParams.append('q', params.query);
    }
    
    if (params.page) {
      queryParams.append('page', params.page.toString());
    }
    
    if (params.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    
    if (params.sort) {
      queryParams.append('sort_by', params.sort.field);
      queryParams.append('sort_order', params.sort.direction);
    }
    
    // Filtros
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach(v => queryParams.append(`${key}[]`, v.toString()));
          } else {
            queryParams.append(key, value.toString());
          }
        }
      });
    }
    
    return queryParams.toString();
  }

  /**
   * Obtiene todas las propiedades con filtros y paginación
   */
  public async getProperties(params: PropertySearchParams = {}): Promise<PropertyResponse> {
    const queryString = this.buildQueryString(params);
    const endpoint = `${API_ENDPOINTS.properties}?${queryString}`;
    const cacheKey = this.getCacheKey('properties', params);
    
    // Intentar obtener del cache primero
    const cached = this.getCachedData<PropertyResponse>(cacheKey);
    if (cached) {
      console.log('📦 Usando propiedades desde cache');
      return cached;
    }
    
    try {
      const response = await this.makeRequest<PropertyResponse>(endpoint);
      
      // Aplicar conversión de divisas si es necesario
      if (response.data) {
        response.data = response.data.map(property => this.enhancePropertyWithCurrency(property));
      }
      
      this.setCachedData(cacheKey, response);
      return response;
    } catch (error) {
      console.error('Error obteniendo propiedades:', error);
      
      // Fallback: retornar datos mock en caso de error
      return this.getMockProperties(params);
    }
  }

  /**
   * Obtiene una propiedad específica por ID
   */
  public async getProperty(id: string): Promise<Property> {
    const endpoint = `${API_ENDPOINTS.properties}/${id}`;
    const cacheKey = this.getCacheKey('property', { id });
    
    const cached = this.getCachedData<Property>(cacheKey);
    if (cached) {
      return cached;
    }
    
    try {
      const property = await this.makeRequest<Property>(endpoint);
      const enhancedProperty = this.enhancePropertyWithCurrency(property);
      
      this.setCachedData(cacheKey, enhancedProperty);
      return enhancedProperty;
    } catch (error) {
      console.error('Error obteniendo propiedad:', error);
      throw error;
    }
  }

  /**
   * Crea una nueva propiedad
   */
  public async createProperty(propertyData: PropertyCreateRequest): Promise<Property> {
    try {
      const property = await this.makeRequest<Property>(API_ENDPOINTS.properties, {
        method: 'POST',
        body: JSON.stringify(propertyData),
      });
      
      // Limpiar cache después de crear
      this.clearCache();
      
      return this.enhancePropertyWithCurrency(property);
    } catch (error) {
      console.error('Error creando propiedad:', error);
      throw error;
    }
  }

  /**
   * Actualiza una propiedad existente
   */
  public async updateProperty(id: string, updates: PropertyUpdateRequest): Promise<Property> {
    try {
      const property = await this.makeRequest<Property>(`${API_ENDPOINTS.properties}/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(updates),
      });
      
      // Limpiar cache después de actualizar
      this.clearCache();
      
      return this.enhancePropertyWithCurrency(property);
    } catch (error) {
      console.error('Error actualizando propiedad:', error);
      throw error;
    }
  }

  /**
   * Elimina una propiedad
   */
  public async deleteProperty(id: string): Promise<void> {
    try {
      await this.makeRequest(`${API_ENDPOINTS.properties}/${id}`, {
        method: 'DELETE',
      });
      
      // Limpiar cache después de eliminar
      this.clearCache();
    } catch (error) {
      console.error('Error eliminando propiedad:', error);
      throw error;
    }
  }

  /**
   * Obtiene analytics de propiedades
   */
  public async getAnalytics(): Promise<PropertyAnalytics> {
    const cacheKey = this.getCacheKey('analytics');
    
    const cached = this.getCachedData<PropertyAnalytics>(cacheKey);
    if (cached) {
      return cached;
    }
    
    try {
      const analytics = await this.makeRequest<PropertyAnalytics>(API_ENDPOINTS.analytics);
      this.setCachedData(cacheKey, analytics);
      return analytics;
    } catch (error) {
      console.error('Error obteniendo analytics:', error);
      
      // Fallback: retornar analytics mock
      return this.getMockAnalytics();
    }
  }

  /**
   * Búsqueda avanzada de propiedades
   */
  public async searchProperties(
    query: string, 
    filters?: PropertyFilters,
    sort?: PropertySortOptions
  ): Promise<PropertyResponse> {
    const params: PropertySearchParams = {
      query,
      filters,
      sort,
      page: 1,
      limit: 20,
    };
    
    return this.getProperties(params);
  }

  /**
   * Obtiene propiedades por tipo
   */
  public async getPropertiesByType(type: PropertyType): Promise<Property[]> {
    const response = await this.getProperties({
      filters: { type: [type] },
      limit: 100,
    });
    
    return response.data;
  }

  /**
   * Obtiene propiedades por estado
   */
  public async getPropertiesByStatus(status: PropertyStatus): Promise<Property[]> {
    const response = await this.getProperties({
      filters: { status: [status] },
      limit: 100,
    });
    
    return response.data;
  }

  /**
   * Obtiene propiedades en un rango de precios
   */
  public async getPropertiesByPriceRange(
    minPrice: number, 
    maxPrice: number, 
    currency: Currency = 'COP'
  ): Promise<Property[]> {
    const response = await this.getProperties({
      filters: { 
        price_min: minPrice, 
        price_max: maxPrice,
        currency 
      },
      limit: 100,
    });
    
    return response.data;
  }

  /**
   * Mejora una propiedad con información de divisas
   */
  private enhancePropertyWithCurrency(property: Property): Property {
    // Agregar conversiones de precios en tiempo real
    if (property.current_price) {
      const conversions = currencyService.convertToAll(
        property.current_price.amount,
        property.current_price.currency
      );
      
      (property as any).price_conversions = conversions;
    }
    
    return property;
  }

  /**
   * Datos mock para fallback
   */
  private getMockProperties(params: PropertySearchParams): PropertyResponse {
    // Implementación de datos mock básicos
    const mockProperties: Property[] = [
      {
        id: 'mock-1',
        title: 'Apartamento Moderno en El Poblado',
        description: 'Hermoso apartamento con vista panorámica',
        type: 'apartment',
        status: 'available',
        address: {
          id: 'addr-1',
          street: 'Carrera 43A',
          number: '15-30',
          neighborhood: 'El Poblado',
          city: 'Medellín',
          state: 'Antioquia',
          country: 'Colombia',
        },
        owner: {
          id: 'owner-1',
          type: 'own',
          name: 'Genius Industries',
          email: 'propiedades@geniusindustries.org',
          phone: '+57 300 123 4567',
          document_type: 'NIT',
          document_number: '123456789-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          active: true,
        },
        features: {
          area_total: 120,
          area_built: 110,
          bedrooms: 3,
          bathrooms: 2,
          parking_spaces: 1,
          storage_rooms: 1,
          balconies: 1,
          terraces: 0,
          stratum: 5,
          construction_year: 2020,
          furnished: true,
          pet_friendly: false,
          has_elevator: true,
          has_pool: true,
          has_gym: true,
          has_garden: false,
          has_bbq_area: true,
          has_playground: false,
          has_security: true,
          has_concierge: true,
        },
        prices: [],
        current_price: {
          id: 'price-1',
          amount: 850000000,
          currency: 'COP',
          type: 'sale',
          negotiable: true,
          last_updated: new Date().toISOString(),
        },
        images: [],
        property_tax_annual: 3500000,
        highlighted: true,
        featured: true,
        published: true,
        views_count: 245,
        favorites_count: 18,
        assigned_agent_id: 'agent-1',
        listing_agent_id: 'agent-1',
        created_by: 'system',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_modified_by: 'system',
        transactions: [],
        visits_scheduled: 3,
        inquiries_count: 12,
      }
    ];

    return {
      data: mockProperties,
      total: mockProperties.length,
      page: params.page || 1,
      limit: params.limit || 10,
      total_pages: 1,
    };
  }

  /**
   * Analytics mock para fallback
   */
  private getMockAnalytics(): PropertyAnalytics {
    return {
      total_properties: 1247,
      available_properties: 856,
      sold_properties: 234,
      rented_properties: 157,
      total_inventory_value: 45678900000,
      average_property_price: 680000000,
      total_sales_this_month: 12,
      total_rentals_this_month: 28,
      commission_earned_this_month: 125000000,
      average_days_on_market: 45,
      conversion_rate: 0.18,
      most_viewed_properties: [],
      top_performing_agents: [],
      price_trends: [],
      properties_by_city: [
        { city: 'Medellín', count: 523, average_price: 650000000 },
        { city: 'Bogotá', count: 412, average_price: 780000000 },
        { city: 'Cali', count: 312, average_price: 520000000 },
      ],
      properties_by_type: [
        { type: 'apartment', count: 624, percentage: 50.04 },
        { type: 'house', count: 398, percentage: 31.91 },
        { type: 'commercial', count: 225, percentage: 18.05 },
      ],
    };
  }

  /**
   * Utilidades para filtros avanzados
   */
  public getFilterOptions(): {
    types: { value: PropertyType; label: string }[];
    statuses: { value: PropertyStatus; label: string }[];
    currencies: { value: Currency; label: string }[];
    cities: string[];
    stratum: number[];
  } {
    return {
      types: [
        { value: 'apartment', label: 'Apartamento' },
        { value: 'house', label: 'Casa' },
        { value: 'commercial', label: 'Comercial' },
        { value: 'land', label: 'Lote' },
        { value: 'office', label: 'Oficina' },
        { value: 'warehouse', label: 'Bodega' },
        { value: 'local', label: 'Local' },
        { value: 'penthouse', label: 'Penthouse' },
        { value: 'studio', label: 'Estudio' },
      ],
      statuses: [
        { value: 'available', label: 'Disponible' },
        { value: 'reserved', label: 'Reservado' },
        { value: 'sold', label: 'Vendido' },
        { value: 'rented', label: 'Arrendado' },
        { value: 'under_construction', label: 'En Construcción' },
        { value: 'maintenance', label: 'En Mantenimiento' },
        { value: 'off_market', label: 'Fuera del Mercado' },
      ],
      currencies: [
        { value: 'COP', label: 'Peso Colombiano (COP)' },
        { value: 'USD', label: 'Dólar Americano (USD)' },
        { value: 'EUR', label: 'Euro (EUR)' },
      ],
      cities: [
        'Medellín', 'Bogotá', 'Cali', 'Barranquilla', 'Cartagena',
        'Santa Marta', 'Bucaramanga', 'Pereira', 'Manizales', 'Armenia'
      ],
      stratum: [1, 2, 3, 4, 5, 6],
    };
  }
}

// Extender la clase Error para errores específicos de propiedades
class PropertyError extends Error {
  public code: string;
  public field?: string;

  constructor(error: { code: string; message: string; field?: string }) {
    super(error.message);
    this.name = 'PropertyError';
    this.code = error.code;
    this.field = error.field;
  }
}

// Instancia singleton del servicio
export const propertyService = new PropertyService();

// Hook para usar el servicio en componentes React
export const useProperties = () => {
  return {
    getProperties: propertyService.getProperties.bind(propertyService),
    getProperty: propertyService.getProperty.bind(propertyService),
    createProperty: propertyService.createProperty.bind(propertyService),
    updateProperty: propertyService.updateProperty.bind(propertyService),
    deleteProperty: propertyService.deleteProperty.bind(propertyService),
    getAnalytics: propertyService.getAnalytics.bind(propertyService),
    searchProperties: propertyService.searchProperties.bind(propertyService),
    getPropertiesByType: propertyService.getPropertiesByType.bind(propertyService),
    getPropertiesByStatus: propertyService.getPropertiesByStatus.bind(propertyService),
    getPropertiesByPriceRange: propertyService.getPropertiesByPriceRange.bind(propertyService),
    getFilterOptions: propertyService.getFilterOptions.bind(propertyService),
  };
};

export { PropertyError };
export default propertyService; 