#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot CLI
Place market and limit orders on Binance Futures Testnet.
"""

import os
import sys
import argparse
import logging
from getpass import getpass
from dotenv import load_dotenv

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging
from bot.validators import (
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price, ValidationError
)
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

def get_api_credentials():
    """Get API credentials from environment or user input."""
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')
    
    if not api_key:
        api_key = input("Enter your Binance Testnet API Key: ").strip()
    
    if not api_secret:
        api_secret = getpass("Enter your Binance Testnet API Secret: ").strip()
    
    return api_key, api_secret

def interactive_mode():
    """Run in interactive mode with prompts."""
    print("\n" + "="*60)
    print("🤖 BINANCE FUTURES TESTNET TRADING BOT")
    print("="*60)
    
    # Get API credentials
    api_key, api_secret = get_api_credentials()
    
    if not api_key or not api_secret:
        print("❌ API credentials are required")
        return 1
    
    try:
        # Initialize client and order manager
        client = BinanceFuturesClient(api_key, api_secret)
        order_manager = OrderManager(client)
        
        # Get account info to verify connection
        try:
            account = client.get_account_info()
            print(f"\n✅ Connected to Binance Futures Testnet")
            print(f"Account assets: {len(account.get('assets', []))} assets available")
        except Exception as e:
            print(f"\n⚠️  Connected but couldn't fetch account info: {e}")
        
        while True:
            try:
                print("\n" + "-"*40)
                print("ENTER ORDER DETAILS")
                print("-"*40)
                
                # Get order details with validation
                symbol = validate_symbol(input("Symbol (e.g., BTCUSDT): ").strip())
                side = validate_side(input("Side (BUY/SELL): ").strip())
                order_type = validate_order_type(input("Order Type (MARKET/LIMIT): ").strip())
                quantity = validate_quantity(input("Quantity: ").strip())
                
                price = None
                if order_type == 'LIMIT':
                    price_input = input("Price: ").strip()
                    price = validate_price(price_input, order_type)
                
                # Confirm order
                print("\n" + "-"*40)
                print("CONFIRM ORDER")
                print("-"*40)
                print(f"Symbol:     {symbol}")
                print(f"Side:       {side}")
                print(f"Type:       {order_type}")
                print(f"Quantity:   {quantity}")
                if price:
                    print(f"Price:      {price}")
                
                confirm = input("\nPlace order? (yes/no): ").strip().lower()
                
                if confirm in ['yes', 'y']:
                    success, response, error = order_manager.place_order(
                        symbol=symbol,
                        side=side,
                        order_type=order_type,
                        quantity=quantity,
                        price=price
                    )
                    
                    if success:
                        print("\n✅ Order placed successfully!")
                        logger.info(f"Order placed: {response.get('orderId') if response else 'N/A'}")
                    else:
                        print(f"\n❌ Order failed: {error}")
                else:
                    print("\nOrder cancelled")
                
                # Ask if user wants to place another order
                another = input("\nPlace another order? (yes/no): ").strip().lower()
                if another not in ['yes', 'y']:
                    break
                    
            except ValidationError as e:
                print(f"\n❌ Validation Error: {e}")
                logger.warning(f"Validation error: {e}")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Unexpected Error: {e}")
                logger.error(f"Unexpected error: {e}", exc_info=True)
        
        print("\nThank you for using the trading bot!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return 1

def cli_mode(args):
    """Run in command-line mode with argparse."""
    try:
        # Validate inputs
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type) if args.price else None
        
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        
        if not api_key or not api_secret:
            print("❌ API credentials are required")
            return 1
        
        # Initialize and place order
        client = BinanceFuturesClient(api_key, api_secret)
        order_manager = OrderManager(client)
        
        success, response, error = order_manager.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        return 0 if success else 1
        
    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Binance Futures Testnet Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a market buy order
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  
  # Place a limit sell order
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 2000
  
  # Run in interactive mode
  python cli.py --interactive
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode with prompts')
    
    parser.add_argument('--symbol', help='Trading pair symbol (e.g., BTCUSDT)')
    parser.add_argument('--side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('--type', choices=['MARKET', 'LIMIT'], help='Order type')
    parser.add_argument('--quantity', type=float, help='Order quantity')
    parser.add_argument('--price', type=float, help='Price (required for LIMIT orders)')
    
    args = parser.parse_args()
    
    # Check if no arguments provided or interactive mode requested
    if args.interactive or len(sys.argv) == 1:
        return interactive_mode()
    else:
        # Validate required args for CLI mode
        if not all([args.symbol, args.side, args.type, args.quantity]):
            parser.error("--symbol, --side, --type, and --quantity are required in CLI mode")
        
        if args.type == 'LIMIT' and not args.price:
            parser.error("--price is required for LIMIT orders")
        
        return cli_mode(args)

if __name__ == '__main__':
    sys.exit(main())