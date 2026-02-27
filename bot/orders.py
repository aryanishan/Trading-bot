import logging
from typing import Dict, Optional, Tuple
from .client import BinanceFuturesClient

logger = logging.getLogger(__name__)

class OrderManager:
    """Manage order placement and tracking."""
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize OrderManager.
        
        Args:
            client: BinanceFuturesClient instance
        """
        self.client = client
        logger.info("OrderManager initialized")
    
    def format_order_summary(self, order_params: Dict) -> str:
        """Format order parameters for display."""
        lines = [
            "\n" + "="*50,
            "ORDER REQUEST SUMMARY",
            "="*50,
            f"Symbol:     {order_params.get('symbol')}",
            f"Side:       {order_params.get('side')}",
            f"Type:       {order_params.get('type')}",
            f"Quantity:   {order_params.get('quantity')}"
        ]
        
        if order_params.get('price'):
            lines.append(f"Price:      {order_params.get('price')}")
        
        if order_params.get('stopPrice'):
            lines.append(f"Stop Price: {order_params.get('stopPrice')}")
        
        lines.append("="*50)
        return "\n".join(lines)
    
    def format_order_response(self, response: Dict) -> str:
        """Format order response for display."""
        lines = [
            "\n" + "="*50,
            "ORDER RESPONSE DETAILS",
            "="*50,
            f"Order ID:     {response.get('orderId')}",
            f"Client ID:    {response.get('clientOrderId')}",
            f"Status:       {response.get('status')}",
            f"Symbol:       {response.get('symbol')}",
            f"Side:         {response.get('side')}",
            f"Type:         {response.get('type')}",
            f"Quantity:     {response.get('origQty')}",
            f"Executed Qty: {response.get('executedQty')}"
        ]
        
        if response.get('avgPrice'):
            lines.append(f"Avg Price:    {response.get('avgPrice')}")
        
        if response.get('price') and float(response.get('price')) > 0:
            lines.append(f"Limit Price:  {response.get('price')}")
        
        if response.get('stopPrice') and float(response.get('stopPrice')) > 0:
            lines.append(f"Stop Price:   {response.get('stopPrice')}")
        
        lines.append("="*50)
        return "\n".join(lines)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                   price: Optional[float] = None, **kwargs) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Place an order with comprehensive error handling.
        
        Returns:
            Tuple of (success, response, error_message)
        """
        try:
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                **kwargs
            }
            
            if price:
                order_params['price'] = price
            
            # Log and display order summary
            logger.info(f"Preparing to place order: {order_params}")
            print(self.format_order_summary(order_params))
            
            # Place the order
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                **kwargs
            )
            
            # Display response
            print(self.format_order_response(response))
            
            # Check order status
            if response.get('status') in ['NEW', 'PARTIALLY_FILLED', 'FILLED']:
                logger.info(f"Order placed successfully. Status: {response.get('status')}")
                return True, response, None
            else:
                logger.warning(f"Order placed but status is {response.get('status')}")
                return True, response, f"Order status: {response.get('status')}"
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to place order: {error_msg}")
            print(f"\n❌ ERROR: {error_msg}")
            return False, None, error_msg