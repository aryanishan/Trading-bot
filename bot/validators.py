import re
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_symbol(symbol):
    """Validate trading symbol format."""
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string")
    
    # Basic symbol validation (e.g., BTCUSDT, ETHUSDT)
    pattern = r'^[A-Z]{2,10}USDT$'
    if not re.match(pattern, symbol):
        raise ValidationError(f"Invalid symbol format: {symbol}. Should be like BTCUSDT, ETHUSDT")
    
    return symbol.upper()

def validate_side(side):
    """Validate order side."""
    side = side.upper()
    if side not in ['BUY', 'SELL']:
        raise ValidationError(f"Invalid side: {side}. Must be BUY or SELL")
    return side

def validate_order_type(order_type):
    """Validate order type."""
    order_type = order_type.upper()
    if order_type not in ['MARKET', 'LIMIT']:
        raise ValidationError(f"Invalid order type: {order_type}. Must be MARKET or LIMIT")
    return order_type

def validate_quantity(quantity):
    """Validate order quantity."""
    try:
        qty = Decimal(str(quantity))
        if qty <= 0:
            raise ValidationError("Quantity must be positive")
        if qty > 1000:  # Reasonable max for testnet
            logger.warning(f"Large quantity detected: {qty}")
        return float(qty)
    except (InvalidOperation, TypeError):
        raise ValidationError(f"Invalid quantity: {quantity}. Must be a number")

def validate_price(price, order_type):
    """Validate price (required for LIMIT orders)."""
    if order_type.upper() == 'MARKET':
        return None
    
    try:
        price_val = Decimal(str(price))
        if price_val <= 0:
            raise ValidationError("Price must be positive")
        return float(price_val)
    except (InvalidOperation, TypeError):
        raise ValidationError(f"Invalid price: {price}. Must be a number for LIMIT orders")