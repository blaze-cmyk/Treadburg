"""
Direct push to Supabase - Execute migration
"""

import os
from dotenv import load_dotenv

load_dotenv(".env.mcp")

print("=" * 70)
print("  PUSHING TO SUPABASE")
print("=" * 70)

try:
    from supabase import create_client
    
    # Get credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Need service role for DDL
    
    if not url or not key:
        print("❌ Missing Supabase credentials in .env.mcp")
        exit(1)
    
    print(f"\n🔌 Connecting to: {url}")
    supabase = create_client(url, key)
    print("✅ Connected")
    
    # Read migration file
    print("\n📄 Reading migration file...")
    with open("supabase/migrations/002_user_management_system.sql", 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"✅ Loaded {len(sql)} characters")
    
    # Execute SQL
    print("\n🚀 Executing migration...")
    
    # Use PostgREST to execute raw SQL
    try:
        # Split into statements and execute
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"   Found {len(statements)} statements")
        
        success_count = 0
        for i, stmt in enumerate(statements, 1):
            if len(stmt) < 10:  # Skip very short statements
                continue
            
            try:
                # Execute via RPC or direct query
                result = supabase.postgrest.rpc('exec', {'query': stmt}).execute()
                success_count += 1
                if i % 20 == 0:
                    print(f"   Progress: {i}/{len(statements)}")
            except Exception as e:
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'duplicate' in error_msg:
                    print(f"   ⚠️  Statement {i}: Already exists (OK)")
                    success_count += 1
                else:
                    print(f"   ❌ Statement {i}: {str(e)[:80]}")
        
        print(f"\n✅ Executed {success_count} statements successfully")
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        print("\n💡 Trying alternative method...")
        
        # Alternative: Use supabase-py's query method
        try:
            # Execute as single query
            supabase.postgrest.schema('public').rpc('exec', {'sql': sql}).execute()
            print("✅ Migration executed via alternative method")
        except Exception as e2:
            print(f"❌ Alternative method failed: {e2}")
            print("\n⚠️  Please run migration manually in Supabase SQL Editor")
            print("   File: backend/supabase/migrations/002_user_management_system.sql")
            print("   URL: https://app.supabase.com/project/pcxscejarxztezfeucgs/sql")
    
    # Verify tables
    print("\n🔍 Verifying tables...")
    tables = ['users', 'credit_transactions', 'payments', 'subscriptions']
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"   ✅ {table} exists")
        except Exception as e:
            if 'does not exist' in str(e).lower():
                print(f"   ❌ {table} not found")
            else:
                print(f"   ⚠️  {table}: {str(e)[:50]}")
    
    print("\n" + "=" * 70)
    print("  DONE!")
    print("=" * 70)
    
except ImportError:
    print("❌ supabase package not installed")
    print("   Run: pip install supabase")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
