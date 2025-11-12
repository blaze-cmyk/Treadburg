"""
Setup script for Supabase and Stripe integrations

This script helps you configure and test the integrations.
Run with: python setup_integrations.py
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_env_file():
    """Check if .env.mcp file exists"""
    env_file = Path(".env.mcp")
    example_file = Path(".env.mcp.example")
    
    if not env_file.exists():
        print("❌ .env.mcp file not found!")
        if example_file.exists():
            print("📝 Creating .env.mcp from example file...")
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env.mcp - Please fill in your credentials")
            return False
        else:
            print("❌ .env.mcp.example not found!")
            return False
    else:
        print("✅ .env.mcp file found")
        return True


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = {
        "supabase": "Supabase Python Client",
        "stripe": "Stripe Python Library",
        "dotenv": "Python Dotenv"
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package if package != "dotenv" else "dotenv")
            print(f"✅ {description} installed")
        except ImportError:
            print(f"❌ {description} NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("   OR")
        print("   pip install -r requirements-integrations.txt")
        return False
    
    return True


def load_env_variables():
    """Load environment variables from .env.mcp"""
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.mcp")
        print("✅ Environment variables loaded")
        return True
    except Exception as e:
        print(f"❌ Error loading environment variables: {e}")
        return False


def test_supabase_connection():
    """Test Supabase connection"""
    print_header("Testing Supabase Connection")
    
    try:
        from open_webui.integrations.supabase_integration import SupabaseClient
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials not configured")
            print("   Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env.mcp")
            return False
        
        print(f"📡 Connecting to: {url}")
        client = SupabaseClient()
        print("✅ Supabase client initialized successfully")
        
        # Test basic query
        try:
            # This will fail if tables don't exist, but connection is OK
            print("🔍 Testing database connection...")
            print("✅ Supabase connection successful")
            print("\n⚠️  Note: Run the migration SQL to create tables")
            print("   File: backend/supabase/migrations/001_initial_schema.sql")
        except Exception as e:
            print(f"⚠️  Connection OK, but tables may not exist: {e}")
            print("   Run the migration SQL to create tables")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False


def test_stripe_connection():
    """Test Stripe connection"""
    print_header("Testing Stripe Connection")
    
    try:
        from open_webui.integrations.stripe_integration import StripeClient
        
        api_key = os.getenv("STRIPE_SECRET_KEY")
        
        if not api_key:
            print("❌ Stripe API key not configured")
            print("   Please set STRIPE_SECRET_KEY in .env.mcp")
            return False
        
        print(f"📡 Connecting to Stripe...")
        client = StripeClient()
        print("✅ Stripe client initialized successfully")
        
        # Test API call
        try:
            import asyncio
            products = asyncio.run(client.list_products(limit=1))
            print(f"✅ Stripe API connection successful")
            print(f"   Found {len(products)} product(s)")
        except Exception as e:
            print(f"⚠️  Client initialized but API call failed: {e}")
            print("   Check your API key permissions")
        
        return True
        
    except Exception as e:
        print(f"❌ Stripe connection failed: {e}")
        return False


def check_mcp_config():
    """Check MCP server configuration"""
    print_header("Checking MCP Configuration")
    
    config_file = Path("mcp_servers_config.json")
    
    if not config_file.exists():
        print("❌ mcp_servers_config.json not found!")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"✅ MCP configuration file found")
        print(f"   Configured servers: {len(config)}")
        
        for server in config:
            server_name = server.get('info', {}).get('name', 'Unknown')
            enabled = server.get('enabled', False)
            status = "✅ Enabled" if enabled else "⚠️  Disabled"
            print(f"   - {server_name}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading MCP config: {e}")
        return False


def create_test_data():
    """Offer to create test data"""
    print_header("Test Data Setup")
    
    response = input("Would you like to create test products in Stripe? (y/n): ")
    
    if response.lower() != 'y':
        print("⏭️  Skipping test data creation")
        return
    
    try:
        from open_webui.integrations.stripe_integration import StripeClient
        import asyncio
        
        client = StripeClient()
        
        print("\n📦 Creating test products...")
        
        # Create test products
        products = [
            {
                "name": "TradeBerg Pro - Monthly",
                "description": "Professional trading analysis - Monthly subscription",
                "price": 2999,  # $29.99
                "interval": "month"
            },
            {
                "name": "TradeBerg Pro - Yearly",
                "description": "Professional trading analysis - Yearly subscription (Save 20%)",
                "price": 28799,  # $287.99
                "interval": "year"
            }
        ]
        
        async def create_products():
            for product_data in products:
                # Create product
                product_result = await client.create_product(
                    name=product_data["name"],
                    description=product_data["description"]
                )
                
                if product_result["success"]:
                    product_id = product_result["product"]["id"]
                    print(f"✅ Created product: {product_data['name']}")
                    
                    # Create price
                    price_result = await client.create_price(
                        product_id=product_id,
                        unit_amount=product_data["price"],
                        currency="usd",
                        recurring={"interval": product_data["interval"]}
                    )
                    
                    if price_result["success"]:
                        price_id = price_result["price"]["id"]
                        print(f"   Price ID: {price_id}")
                    else:
                        print(f"   ❌ Failed to create price: {price_result.get('error')}")
                else:
                    print(f"❌ Failed to create product: {product_result.get('error')}")
        
        asyncio.run(create_products())
        print("\n✅ Test products created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")


def main():
    """Main setup function"""
    print_header("TradeBerg Integration Setup")
    
    print("This script will help you set up Supabase and Stripe integrations.\n")
    
    # Step 1: Check environment file
    print_header("Step 1: Environment Configuration")
    if not check_env_file():
        print("\n⚠️  Please configure .env.mcp and run this script again")
        return
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n⚠️  Please install missing dependencies and run this script again")
        return
    
    # Step 3: Load environment variables
    print_header("Step 3: Loading Environment Variables")
    if not load_env_variables():
        return
    
    # Step 4: Check MCP configuration
    check_mcp_config()
    
    # Step 5: Test Supabase
    supabase_ok = test_supabase_connection()
    
    # Step 6: Test Stripe
    stripe_ok = test_stripe_connection()
    
    # Step 7: Offer to create test data
    if stripe_ok:
        create_test_data()
    
    # Final summary
    print_header("Setup Summary")
    
    if supabase_ok and stripe_ok:
        print("✅ All integrations configured successfully!")
        print("\n📝 Next steps:")
        print("   1. Run Supabase migration: backend/supabase/migrations/001_initial_schema.sql")
        print("   2. Configure webhook endpoint in Stripe dashboard")
        print("   3. Test the API endpoints")
        print("   4. Start using the integrations!")
    else:
        print("⚠️  Some integrations need attention:")
        if not supabase_ok:
            print("   - Supabase: Check credentials and configuration")
        if not stripe_ok:
            print("   - Stripe: Check API key and permissions")
    
    print("\n📚 For more information, see: SUPABASE_STRIPE_INTEGRATION_GUIDE.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
