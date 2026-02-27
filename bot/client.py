import requests
import time
import hashlib
import hmac
import urllib.parse
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """Client for Binance Futures Testnet API."""
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Binance Futures client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        logger.info("Binance Futures client initialized for testnet")
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature for request."""
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method: str, endpoint: str, signed: bool = False, 
                      params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            signed: Whether request requires signature
            params: Request parameters
            
        Returns:
            API response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        logger.debug(f"Making {method} request to {endpoint} with params: {params}")
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            logger.debug(f"Response status: {response.status_code}")
            
            result = response.json()
            logger.debug(f"Response data: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    logger.error(f"API error: {error_data}")
                    raise Exception(f"API error: {error_data.get('msg', 'Unknown error')}")
                except:
                    pass
            raise Exception(f"Request failed: {str(e)}")
    
    def get_server_time(self) -> int:
        """Get server time."""
        response = self._make_request('GET', '/fapi/v1/time')
        return response.get('serverTime', 0)
    
    def get_exchange_info(self) -> Dict:
        """Get exchange information."""
        return self._make_request('GET', '/fapi/v1/exchangeInfo')
    
    def get_account_info(self) -> Dict:
        """Get account information."""
        return self._make_request('GET', '/fapi/v2/account', signed=True)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                   price: Optional[float] = None, **kwargs) -> Dict:
        """
        Place an order on Binance Futures.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Price for LIMIT orders
            **kwargs: Additional order parameters
            
        Returns:
            Order response from API
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            **kwargs
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = kwargs.get('timeInForce', 'GTC')
        
        logger.info(f"Placing {side} {order_type} order for {quantity} {symbol}")
        logger.debug(f"Order params: {params}")
        
        try:
            response = self._make_request('POST', '/fapi/v1/order', signed=True, params=params)
            logger.info(f"Order placed successfully: {response.get('orderId')}")
            return response
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get order status."""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('GET', '/fapi/v1/order', signed=True, params=params)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order."""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/fapi/v1/order', signed=True, params=params)