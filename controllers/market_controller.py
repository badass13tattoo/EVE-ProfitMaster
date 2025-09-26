"""
Market Controller
Handles market data operations and price calculations
"""

from flask import request, jsonify
from typing import Dict, List
from services.market_data_service import MarketDataService


class MarketController:
    """Controller for market operations"""
    
    def __init__(self, market_service: MarketDataService):
        self.market_service = market_service
    
    def get_type_prices(self, type_id: int, region_id: int = 10000002) -> Dict:
        """Get prices for a specific type"""
        try:
            prices = self.market_service.get_type_prices(type_id, region_id)
            return prices
        except Exception as e:
            print(f"Error getting type prices: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_market_orders(self, region_id: int, type_id: int = None) -> List[Dict]:
        """Get market orders for a region"""
        try:
            orders = self.market_service.get_market_orders(region_id, type_id)
            return orders
        except Exception as e:
            print(f"Error getting market orders: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_market_prices(self, region_id: int) -> List[Dict]:
        """Get market prices for a region"""
        try:
            prices = self.market_service.get_market_prices(region_id)
            return prices
        except Exception as e:
            print(f"Error getting market prices: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def calculate_market_value(self, type_id: int, quantity: int, region_id: int = 10000002) -> Dict:
        """Calculate market value for a quantity of items"""
        try:
            value = self.market_service.calculate_market_value(type_id, quantity, region_id)
            return value
        except Exception as e:
            print(f"Error calculating market value: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_region_info(self, region_id: int) -> Dict:
        """Get region information"""
        try:
            region_info = self.market_service.get_region_info(region_id)
            return region_info
        except Exception as e:
            print(f"Error getting region info: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_market_groups(self) -> List[Dict]:
        """Get market groups"""
        try:
            groups = self.market_service.get_market_groups()
            return groups
        except Exception as e:
            print(f"Error getting market groups: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
    
    def get_market_group_info(self, group_id: int) -> Dict:
        """Get market group information"""
        try:
            group_info = self.market_service.get_market_group_info(group_id)
            return group_info
        except Exception as e:
            print(f"Error getting market group info: {e}")
            return {'error': f'Internal server error: {str(e)}'}, 500
