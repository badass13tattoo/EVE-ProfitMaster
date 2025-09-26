"""
Market Data Service
Handles market data collection and price calculations
"""

import requests
from typing import Dict, List, Optional
from .cache_service import CacheService


class MarketDataService:
    """Service for market data collection and price calculations"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.esi_base_url = "https://esi.evetech.net/latest"
    
    def get_market_orders(self, region_id: int, type_id: int = None) -> List[Dict]:
        """Get market orders for a region"""
        cache_key = f"market_orders_{region_id}_{type_id or 'all'}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.esi_base_url}/markets/{region_id}/orders/"
            params = {}
            if type_id:
                params['type_id'] = type_id
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 300)  # Cache for 5 minutes
            return data
        except Exception as e:
            print(f"Error getting market orders: {e}")
            return []
    
    def get_market_prices(self, region_id: int) -> List[Dict]:
        """Get market prices for a region"""
        cache_key = f"market_prices_{region_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.esi_base_url}/markets/{region_id}/prices/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 3600)  # Cache for 1 hour
            return data
        except Exception as e:
            print(f"Error getting market prices: {e}")
            return []
    
    def get_type_prices(self, type_id: int, region_id: int = 10000002) -> Dict:
        """Get prices for a specific type in a region"""
        cache_key = f"type_prices_{type_id}_{region_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get market orders for the type
            orders = self.get_market_orders(region_id, type_id)
            
            # Calculate buy and sell prices
            buy_orders = [order for order in orders if order.get('is_buy_order', False)]
            sell_orders = [order for order in orders if not order.get('is_buy_order', False)]
            
            # Sort by price
            buy_orders.sort(key=lambda x: x.get('price', 0), reverse=True)
            sell_orders.sort(key=lambda x: x.get('price', 0))
            
            # Get best prices
            best_buy_price = buy_orders[0].get('price', 0) if buy_orders else 0
            best_sell_price = sell_orders[0].get('price', 0) if sell_orders else 0
            
            # Calculate volume
            total_buy_volume = sum(order.get('volume_remain', 0) for order in buy_orders)
            total_sell_volume = sum(order.get('volume_remain', 0) for order in sell_orders)
            
            prices = {
                'type_id': type_id,
                'region_id': region_id,
                'buy_price': best_buy_price,
                'sell_price': best_sell_price,
                'buy_volume': total_buy_volume,
                'sell_volume': total_sell_volume,
                'spread': best_sell_price - best_buy_price if best_buy_price and best_sell_price else 0
            }
            
            self.cache_service.set(cache_key, prices, 300)  # Cache for 5 minutes
            return prices
        except Exception as e:
            print(f"Error getting type prices: {e}")
            return {
                'type_id': type_id,
                'region_id': region_id,
                'buy_price': 0,
                'sell_price': 0,
                'buy_volume': 0,
                'sell_volume': 0,
                'spread': 0
            }
    
    def get_historical_prices(self, type_id: int, region_id: int = 10000002) -> List[Dict]:
        """Get historical prices for a type (if available)"""
        cache_key = f"historical_prices_{type_id}_{region_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # This would typically use a third-party service like Fuzzworks
            # For now, we'll return empty data
            historical_data = []
            self.cache_service.set(cache_key, historical_data, 3600)  # Cache for 1 hour
            return historical_data
        except Exception as e:
            print(f"Error getting historical prices: {e}")
            return []
    
    def calculate_market_value(self, type_id: int, quantity: int, region_id: int = 10000002) -> Dict:
        """Calculate market value for a quantity of items"""
        prices = self.get_type_prices(type_id, region_id)
        
        return {
            'type_id': type_id,
            'quantity': quantity,
            'region_id': region_id,
            'buy_value': prices['buy_price'] * quantity,
            'sell_value': prices['sell_price'] * quantity,
            'average_value': ((prices['buy_price'] + prices['sell_price']) / 2) * quantity if prices['buy_price'] and prices['sell_price'] else 0
        }
    
    def get_region_info(self, region_id: int) -> Dict:
        """Get region information"""
        cache_key = f"region_{region_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.esi_base_url}/universe/regions/{region_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting region info: {e}")
            return {'region_id': region_id, 'name': f'Region {region_id}'}
    
    def get_market_groups(self) -> List[Dict]:
        """Get market groups"""
        cache_key = "market_groups"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.esi_base_url}/markets/groups/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting market groups: {e}")
            return []
    
    def get_market_group_info(self, group_id: int) -> Dict:
        """Get market group information"""
        cache_key = f"market_group_{group_id}"
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.esi_base_url}/markets/groups/{group_id}/"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.cache_service.set(cache_key, data, 86400)  # Cache for 24 hours
            return data
        except Exception as e:
            print(f"Error getting market group info: {e}")
            return {'group_id': group_id, 'name': f'Group {group_id}'}
