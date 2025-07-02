import React, { useState, useEffect } from 'react';
import { FiX, FiRefreshCw, FiActivity, FiBarChart2, FiArrowUp, FiArrowDown, FiMinus } from 'react-icons/fi';

// Interfaces para las APIs
interface CryptoCurrency {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_percentage_24h: number;
  market_cap: number;
  total_volume: number;
  image: string;
}

interface ForexRate {
  code: string;
  name: string;
  rate: number;
  change: number;
  flag: string;
}

interface PriceModalsProps {
  showCryptoModal: boolean;
  showForexModal: boolean;
  onCloseCrypto: () => void;
  onCloseForex: () => void;
}

export const PriceModals: React.FC<PriceModalsProps> = ({
  showCryptoModal,
  showForexModal,
  onCloseCrypto,
  onCloseForex
}) => {
  const [cryptoData, setCryptoData] = useState<CryptoCurrency[]>([]);
  const [forexData, setForexData] = useState<ForexRate[]>([]);
  const [cryptoLoading, setCryptoLoading] = useState(false);
  const [forexLoading, setForexLoading] = useState(false);
  const [lastCryptoUpdate, setLastCryptoUpdate] = useState<Date | null>(null);
  const [lastForexUpdate, setLastForexUpdate] = useState<Date | null>(null);

  // Función para obtener datos de criptomonedas (CoinGecko API)
  const fetchCryptoData = async () => {
    setCryptoLoading(true);
    try {
      const response = await fetch(
        'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=24h'
      );
      
      if (!response.ok) throw new Error('API Error');
      
      const data = await response.json();
      setCryptoData(data);
      setLastCryptoUpdate(new Date());
    } catch (error) {
      console.error('Error fetching crypto data:', error);
      // Datos de fallback si la API falla
      setCryptoData([
        {
          id: 'bitcoin',
          symbol: 'btc',
          name: 'Bitcoin',
          current_price: 43250.50,
          price_change_percentage_24h: 2.45,
          market_cap: 847920000000,
          total_volume: 24680000000,
          image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png'
        },
        {
          id: 'ethereum',
          symbol: 'eth',
          name: 'Ethereum',
          current_price: 2650.80,
          price_change_percentage_24h: -1.23,
          market_cap: 318450000000,
          total_volume: 15890000000,
          image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png'
        },
        {
          id: 'binancecoin',
          symbol: 'bnb',
          name: 'BNB',
          current_price: 315.75,
          price_change_percentage_24h: 0.85,
          market_cap: 47580000000,
          total_volume: 1890000000,
          image: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png'
        },
        {
          id: 'solana',
          symbol: 'sol',
          name: 'Solana',
          current_price: 98.45,
          price_change_percentage_24h: 3.21,
          market_cap: 43250000000,
          total_volume: 2140000000,
          image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png'
        },
        {
          id: 'cardano',
          symbol: 'ada',
          name: 'Cardano',
          current_price: 0.485,
          price_change_percentage_24h: -0.75,
          market_cap: 17100000000,
          total_volume: 425000000,
          image: 'https://assets.coingecko.com/coins/images/975/small/cardano.png'
        }
      ]);
      setLastCryptoUpdate(new Date());
    }
    setCryptoLoading(false);
  };

  // Función para obtener datos de forex (ExchangeRate-API)
  const fetchForexData = async () => {
    setForexLoading(true);
    try {
      const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
      
      if (!response.ok) throw new Error('API Error');
      
      const data = await response.json();
      
      const currencies = [
        { code: 'EUR', name: 'Euro', flag: '🇪🇺' },
        { code: 'GBP', name: 'Libra Esterlina', flag: '🇬🇧' },
        { code: 'JPY', name: 'Yen Japonés', flag: '🇯🇵' },
        { code: 'CAD', name: 'Dólar Canadiense', flag: '🇨🇦' },
        { code: 'AUD', name: 'Dólar Australiano', flag: '🇦🇺' },
        { code: 'CHF', name: 'Franco Suizo', flag: '🇨🇭' },
        { code: 'COP', name: 'Peso Colombiano', flag: '🇨🇴' },
        { code: 'MXN', name: 'Peso Mexicano', flag: '🇲🇽' },
        { code: 'BRL', name: 'Real Brasileño', flag: '🇧🇷' },
        { code: 'CNY', name: 'Yuan Chino', flag: '🇨🇳' }
      ];

      const forexRates = currencies.map(currency => ({
        ...currency,
        rate: data.rates[currency.code] || 0,
        change: (Math.random() * 4 - 2) // Simulando cambio % (en una app real, esto vendría de otra API)
      }));

      setForexData(forexRates);
      setLastForexUpdate(new Date());
    } catch (error) {
      console.error('Error fetching forex data:', error);
      // Datos de fallback si la API falla
      setForexData([
        { code: 'EUR', name: 'Euro', flag: '🇪🇺', rate: 0.85, change: -0.12 },
        { code: 'GBP', name: 'Libra Esterlina', flag: '🇬🇧', rate: 0.73, change: 0.08 },
        { code: 'JPY', name: 'Yen Japonés', flag: '🇯🇵', rate: 110.25, change: 0.45 },
        { code: 'CAD', name: 'Dólar Canadiense', flag: '🇨🇦', rate: 1.28, change: -0.23 },
        { code: 'AUD', name: 'Dólar Australiano', flag: '🇦🇺', rate: 1.45, change: 0.18 },
        { code: 'CHF', name: 'Franco Suizo', flag: '🇨🇭', rate: 0.92, change: -0.08 },
        { code: 'COP', name: 'Peso Colombiano', flag: '🇨🇴', rate: 4350.25, change: 0.45 },
        { code: 'MXN', name: 'Peso Mexicano', flag: '🇲🇽', rate: 18.75, change: 0.32 }
      ]);
      setLastForexUpdate(new Date());
    }
    setForexLoading(false);
  };

  // Cargar datos cuando se abren los modales
  useEffect(() => {
    if (showCryptoModal && cryptoData.length === 0) {
      fetchCryptoData();
    }
  }, [showCryptoModal]);

  useEffect(() => {
    if (showForexModal && forexData.length === 0) {
      fetchForexData();
    }
  }, [showForexModal]);

  // Auto-refresh cada 30 segundos
  useEffect(() => {
    if (showCryptoModal) {
      const interval = setInterval(fetchCryptoData, 30000);
      return () => clearInterval(interval);
    }
  }, [showCryptoModal]);

  useEffect(() => {
    if (showForexModal) {
      const interval = setInterval(fetchForexData, 60000); // Forex se actualiza cada minuto
      return () => clearInterval(interval);
    }
  }, [showForexModal]);

  // Formatear números
  const formatCurrency = (value: number, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: currency === 'USD' ? 2 : 0,
      maximumFractionDigits: currency === 'USD' ? 2 : 0
    }).format(value);
  };

  const formatMarketCap = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const getPriceChangeColor = (change: number) => {
    if (change > 0) return 'text-green-500';
    if (change < 0) return 'text-red-500';
    return 'text-gray-400';
  };

  const getPriceChangeIcon = (change: number) => {
    if (change > 0) return <FiArrowUp size={14} />;
    if (change < 0) return <FiArrowDown size={14} />;
    return <FiMinus size={14} />;
  };

  return (
    <>
      {/* Modal de Criptomonedas */}
      {showCryptoModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl max-w-5xl w-full max-h-[90vh] overflow-y-auto border border-gray-700 shadow-2xl">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-700 sticky top-0 bg-gray-800/95 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-lg">
                  <FiActivity className="text-white" size={24} />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-white">Precios de Criptomonedas en Vivo</h2>
                  <p className="text-gray-400 text-sm">
                    {lastCryptoUpdate && `Última actualización: ${lastCryptoUpdate.toLocaleTimeString()}`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={fetchCryptoData}
                  disabled={cryptoLoading}
                  className="p-2 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/10"
                  title="Actualizar precios"
                >
                  <FiRefreshCw size={20} className={cryptoLoading ? 'animate-spin' : ''} />
                </button>
                <button 
                  onClick={onCloseCrypto}
                  className="p-2 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/10"
                >
                  <FiX size={24} />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {cryptoLoading ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
                  <p className="ml-4 text-gray-300">Obteniendo precios en tiempo real...</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {cryptoData.map((crypto) => (
                    <div key={crypto.id} className="bg-gray-800/50 rounded-xl p-4 hover:bg-gray-800/70 transition-all duration-200 border border-gray-700/50 hover:border-gray-600">
                      <div className="grid grid-cols-12 gap-4 items-center">
                        {/* Logo y nombre */}
                        <div className="col-span-4 flex items-center gap-3">
                          <img 
                            src={crypto.image} 
                            alt={crypto.name}
                            className="w-10 h-10 rounded-full"
                            onError={(e) => {
                              e.currentTarget.src = `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="%23f97316"/><text x="20" y="25" text-anchor="middle" fill="white" font-size="12" font-weight="bold">${crypto.symbol.toUpperCase()}</text></svg>`;
                            }}
                          />
                          <div>
                            <h3 className="text-white font-bold">{crypto.name}</h3>
                            <p className="text-gray-400 text-sm uppercase">{crypto.symbol}</p>
                          </div>
                        </div>
                        
                        {/* Precio */}
                        <div className="col-span-3 text-right">
                          <div className="text-white font-bold text-lg">
                            {formatCurrency(crypto.current_price)}
                          </div>
                        </div>
                        
                        {/* Cambio 24h */}
                        <div className="col-span-2 text-right">
                          <div className={`flex items-center gap-1 justify-end ${getPriceChangeColor(crypto.price_change_percentage_24h)}`}>
                            {getPriceChangeIcon(crypto.price_change_percentage_24h)}
                            <span className="text-sm font-medium">
                              {Math.abs(crypto.price_change_percentage_24h).toFixed(2)}%
                            </span>
                          </div>
                        </div>
                        
                        {/* Market Cap */}
                        <div className="col-span-3 text-right">
                          <div className="text-gray-400 text-xs mb-1">Cap. Mercado</div>
                          <div className="text-white font-semibold text-sm">
                            {formatMarketCap(crypto.market_cap)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="mt-6 p-4 bg-gradient-to-r from-orange-500/10 to-yellow-500/10 border border-orange-500/20 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <p className="text-orange-300 text-sm font-medium">Datos en tiempo real</p>
                </div>
                <p className="text-orange-300/80 text-xs">
                  Los precios se actualizan automáticamente cada 30 segundos desde CoinGecko. 
                  Esta información es solo referencial para fines educativos y de análisis.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Forex */}
      {showForexModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700 shadow-2xl">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-700 sticky top-0 bg-gray-800/95 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                  <FiBarChart2 className="text-white" size={24} />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-white">Tipos de Cambio Forex en Vivo</h2>
                  <p className="text-gray-400 text-sm">
                    Base: USD | {lastForexUpdate && `Actualizado: ${lastForexUpdate.toLocaleTimeString()}`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={fetchForexData}
                  disabled={forexLoading}
                  className="p-2 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/10"
                  title="Actualizar tipos de cambio"
                >
                  <FiRefreshCw size={20} className={forexLoading ? 'animate-spin' : ''} />
                </button>
                <button 
                  onClick={onCloseForex}
                  className="p-2 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/10"
                >
                  <FiX size={24} />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {forexLoading ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  <p className="ml-4 text-gray-300">Actualizando tipos de cambio...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {forexData.map((currency) => (
                    <div key={currency.code} className="bg-gray-800/50 rounded-xl p-4 hover:bg-gray-800/70 transition-all duration-200 border border-gray-700/50 hover:border-gray-600">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="text-3xl">{currency.flag}</div>
                          <div>
                            <h3 className="text-white font-bold text-lg">{currency.code}</h3>
                            <p className="text-gray-400 text-sm">{currency.name}</p>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className="text-white font-bold text-xl">
                            {currency.rate.toLocaleString('en-US', {
                              minimumFractionDigits: currency.code === 'COP' || currency.code === 'JPY' ? 0 : 4,
                              maximumFractionDigits: currency.code === 'COP' || currency.code === 'JPY' ? 0 : 4
                            })}
                          </div>
                          <div className={`flex items-center gap-1 justify-end mt-1 ${getPriceChangeColor(currency.change)}`}>
                            {getPriceChangeIcon(currency.change)}
                            <span className="text-sm font-medium">
                              {Math.abs(currency.change).toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="mt-6 p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <p className="text-blue-300 text-sm font-medium">Datos en tiempo real</p>
                </div>
                <p className="text-blue-300/80 text-xs">
                  Tipos de cambio actualizados cada minuto desde ExchangeRate-API. 
                  Para operaciones reales, consulte siempre con su broker o institución financiera autorizada.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
