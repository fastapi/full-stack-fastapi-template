import { Currency, CurrencyRates } from '../types/property';

// Configuración de APIs de divisas
const EXCHANGE_API_KEYS = {
  // Usar APIs gratuitas como backup
  fixer: process.env.REACT_APP_FIXER_API_KEY,
  exchangerate: process.env.REACT_APP_EXCHANGERATE_API_KEY,
};

// Tasas de cambio por defecto (backup offline)
const DEFAULT_RATES: CurrencyRates = {
  USD_TO_COP: 4150.00,
  EUR_TO_COP: 4580.00,
  COP_TO_USD: 0.000241,
  COP_TO_EUR: 0.000218,
  EUR_TO_USD: 1.10,
  USD_TO_EUR: 0.91,
  last_updated: new Date().toISOString(),
};

class CurrencyService {
  private rates: CurrencyRates = DEFAULT_RATES;
  private lastFetch: Date | null = null;
  private readonly CACHE_DURATION = 30 * 60 * 1000; // 30 minutos

  constructor() {
    this.loadCachedRates();
    this.updateRates();
  }

  /**
   * Carga las tasas desde localStorage si están disponibles
   */
  private loadCachedRates(): void {
    try {
      const cached = localStorage.getItem('currency_rates');
      if (cached) {
        const data = JSON.parse(cached);
        if (data.rates && data.timestamp) {
          const age = Date.now() - new Date(data.timestamp).getTime();
          if (age < this.CACHE_DURATION) {
            this.rates = data.rates;
            this.lastFetch = new Date(data.timestamp);
            console.log('📊 Usando tasas de cambio desde cache');
            return;
          }
        }
      }
    } catch (error) {
      console.warn('Error cargando cache de divisas:', error);
    }
  }

  /**
   * Guarda las tasas en localStorage
   */
  private saveCachedRates(): void {
    try {
      const cacheData = {
        rates: this.rates,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem('currency_rates', JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Error guardando cache de divisas:', error);
    }
  }

  /**
   * Actualiza las tasas de cambio desde APIs externas
   */
  public async updateRates(): Promise<void> {
    // Si ya tenemos datos recientes, no actualizar
    if (this.lastFetch && Date.now() - this.lastFetch.getTime() < this.CACHE_DURATION) {
      return;
    }

    try {
      console.log('🔄 Actualizando tasas de cambio...');
      
      // Intentar primero con ExchangeRate-API (gratuita)
      const exchangeRateSuccess = await this.fetchFromExchangeRateAPI();
      if (exchangeRateSuccess) {
        this.lastFetch = new Date();
        this.saveCachedRates();
        console.log('✅ Tasas actualizadas desde ExchangeRate-API');
        return;
      }

      // Backup: usar Fixer.io si está disponible
      if (EXCHANGE_API_KEYS.fixer) {
        const fixerSuccess = await this.fetchFromFixerAPI();
        if (fixerSuccess) {
          this.lastFetch = new Date();
          this.saveCachedRates();
          console.log('✅ Tasas actualizadas desde Fixer.io');
          return;
        }
      }

      // Si no se pueden obtener tasas actualizadas, usar las por defecto
      console.log('⚠️ Usando tasas de cambio por defecto');
      this.rates.last_updated = new Date().toISOString();
      
    } catch (error) {
      console.error('Error actualizando tasas de cambio:', error);
      // Continuar con las tasas por defecto
    }
  }

  /**
   * Obtiene tasas desde ExchangeRate-API (gratuita)
   */
  private async fetchFromExchangeRateAPI(): Promise<boolean> {
    try {
      // USD como base
      const usdResponse = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
      const usdData = await usdResponse.json();
      
      if (usdData.rates) {
        const copFromUsd = usdData.rates.COP || DEFAULT_RATES.USD_TO_COP;
        const eurFromUsd = usdData.rates.EUR || (1 / DEFAULT_RATES.USD_TO_EUR);
        
        this.rates = {
          USD_TO_COP: copFromUsd,
          EUR_TO_COP: copFromUsd / eurFromUsd,
          COP_TO_USD: 1 / copFromUsd,
          COP_TO_EUR: eurFromUsd / copFromUsd,
          EUR_TO_USD: eurFromUsd,
          USD_TO_EUR: 1 / eurFromUsd,
          last_updated: new Date().toISOString(),
        };
        
        return true;
      }
    } catch (error) {
      console.warn('Error con ExchangeRate-API:', error);
    }
    
    return false;
  }

  /**
   * Obtiene tasas desde Fixer.io (requiere API key)
   */
  private async fetchFromFixerAPI(): Promise<boolean> {
    if (!EXCHANGE_API_KEYS.fixer) return false;
    
    try {
      const response = await fetch(
        `https://api.fixer.io/latest?access_key=${EXCHANGE_API_KEYS.fixer}&symbols=USD,COP,EUR`
      );
      const data = await response.json();
      
      if (data.success && data.rates) {
        // Fixer usa EUR como base
        const usdRate = data.rates.USD;
        const copRate = data.rates.COP;
        
        this.rates = {
          USD_TO_COP: copRate / usdRate,
          EUR_TO_COP: copRate,
          COP_TO_USD: usdRate / copRate,
          COP_TO_EUR: 1 / copRate,
          EUR_TO_USD: usdRate,
          USD_TO_EUR: 1 / usdRate,
          last_updated: new Date().toISOString(),
        };
        
        return true;
      }
    } catch (error) {
      console.warn('Error con Fixer.io:', error);
    }
    
    return false;
  }

  /**
   * Convierte una cantidad de una moneda a otra
   */
  public convert(amount: number, fromCurrency: Currency, toCurrency: Currency): number {
    if (fromCurrency === toCurrency) return amount;
    
    const conversionKey = `${fromCurrency}_TO_${toCurrency}` as keyof CurrencyRates;
    const rate = this.rates[conversionKey];
    
    if (typeof rate === 'number') {
      return Number((amount * rate).toFixed(2));
    }
    
    // Fallback: conversión a través de USD
    if (fromCurrency === 'COP' && toCurrency === 'USD') {
      return Number((amount * this.rates.COP_TO_USD).toFixed(2));
    }
    if (fromCurrency === 'USD' && toCurrency === 'COP') {
      return Number((amount * this.rates.USD_TO_COP).toFixed(2));
    }
    if (fromCurrency === 'COP' && toCurrency === 'EUR') {
      return Number((amount * this.rates.COP_TO_EUR).toFixed(2));
    }
    if (fromCurrency === 'EUR' && toCurrency === 'COP') {
      return Number((amount * this.rates.EUR_TO_COP).toFixed(2));
    }
    if (fromCurrency === 'USD' && toCurrency === 'EUR') {
      return Number((amount * this.rates.USD_TO_EUR).toFixed(2));
    }
    if (fromCurrency === 'EUR' && toCurrency === 'USD') {
      return Number((amount * this.rates.EUR_TO_USD).toFixed(2));
    }
    
    return amount; // Si no se puede convertir, retornar el valor original
  }

  /**
   * Obtiene la tasa de cambio actual entre dos monedas
   */
  public getRate(fromCurrency: Currency, toCurrency: Currency): number {
    if (fromCurrency === toCurrency) return 1;
    
    const conversionKey = `${fromCurrency}_TO_${toCurrency}` as keyof CurrencyRates;
    const rate = this.rates[conversionKey];
    
    return typeof rate === 'number' ? rate : 1;
  }

  /**
   * Formatea una cantidad con el símbolo de la moneda
   */
  public formatCurrency(amount: number, currency: Currency): string {
    const symbols = {
      COP: '$',
      USD: 'US$',
      EUR: '€'
    };
    
    const formatter = new Intl.NumberFormat('es-CO', {
      style: 'decimal',
      minimumFractionDigits: currency === 'COP' ? 0 : 2,
      maximumFractionDigits: currency === 'COP' ? 0 : 2,
    });
    
    const symbol = symbols[currency];
    const formattedAmount = formatter.format(amount);
    
    return currency === 'EUR' 
      ? `${formattedAmount}${symbol}`
      : `${symbol}${formattedAmount}`;
  }

  /**
   * Obtiene todas las tasas actuales
   */
  public getCurrentRates(): CurrencyRates {
    return { ...this.rates };
  }

  /**
   * Obtiene el estado de las tasas (cuándo fueron actualizadas por última vez)
   */
  public getRatesStatus(): {
    lastUpdated: string;
    isRecent: boolean;
    minutesAgo: number;
  } {
    const lastUpdated = new Date(this.rates.last_updated);
    const now = new Date();
    const minutesAgo = Math.floor((now.getTime() - lastUpdated.getTime()) / (1000 * 60));
    const isRecent = minutesAgo < 30;
    
    return {
      lastUpdated: this.rates.last_updated,
      isRecent,
      minutesAgo,
    };
  }

  /**
   * Convierte un precio a múltiples monedas
   */
  public convertToAll(amount: number, fromCurrency: Currency): {
    COP: number;
    USD: number;
    EUR: number;
    formatted: {
      COP: string;
      USD: string;
      EUR: string;
    };
  } {
    const currencies: Currency[] = ['COP', 'USD', 'EUR'];
    const result = {
      COP: 0,
      USD: 0,
      EUR: 0,
      formatted: {
        COP: '',
        USD: '',
        EUR: '',
      },
    };
    
    currencies.forEach(currency => {
      const convertedAmount = this.convert(amount, fromCurrency, currency);
      result[currency] = convertedAmount;
      result.formatted[currency] = this.formatCurrency(convertedAmount, currency);
    });
    
    return result;
  }

  /**
   * Fuerza la actualización de las tasas
   */
  public async forceUpdate(): Promise<void> {
    this.lastFetch = null;
    await this.updateRates();
  }
}

// Instancia singleton del servicio
export const currencyService = new CurrencyService();

// Hook para usar el servicio en componentes React
export const useCurrency = () => {
  return {
    convert: currencyService.convert.bind(currencyService),
    formatCurrency: currencyService.formatCurrency.bind(currencyService),
    getCurrentRates: currencyService.getCurrentRates.bind(currencyService),
    getRatesStatus: currencyService.getRatesStatus.bind(currencyService),
    convertToAll: currencyService.convertToAll.bind(currencyService),
    updateRates: currencyService.updateRates.bind(currencyService),
    forceUpdate: currencyService.forceUpdate.bind(currencyService),
    getRate: currencyService.getRate.bind(currencyService),
  };
};

export default currencyService; 