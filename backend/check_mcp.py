import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('data/webui.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "="*50)

# Check for config table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
if cursor.fetchone():
    print("\nConfig table found. Checking for MCP server configurations...")
    cursor.execute("SELECT data FROM config")
    configs = cursor.fetchall()
    
    if configs:
        print("\nAll configurations:")
        for config_data in configs:
            try:
                data = json.loads(config_data[0]) if config_data[0] else {}
                
                # Check for tool server connections
                if 'TOOL_SERVER_CONNECTIONS' in data or 'tool_server.connections' in data:
                    print("\n" + "="*50)
                    print("\nTOOL_SERVER_CONNECTIONS found:")
                    
                    connections = data.get('TOOL_SERVER_CONNECTIONS') or data.get('tool_server.connections', [])
                    
                    if connections:
                        print(json.dumps(connections, indent=2))
                        
                        # Check for Supabase and Stripe
                        has_supabase = any('supabase' in str(conn).lower() for conn in connections)
                        has_stripe = any('stripe' in str(conn).lower() for conn in connections)
                        
                        print("\n" + "="*50)
                        print("\n📊 MCP SERVER STATUS:")
                        print(f"  Supabase MCP Server: {'✓ FOUND' if has_supabase else '✗ NOT FOUND'}")
                        print(f"  Stripe MCP Server: {'✓ FOUND' if has_stripe else '✗ NOT FOUND'}")
                        
                        # Show details of each server
                        print("\n" + "="*50)
                        print("\n📋 Configured MCP Servers:")
                        for i, conn in enumerate(connections, 1):
                            server_type = conn.get('type', 'unknown')
                            server_name = conn.get('info', {}).get('name', 'Unknown')
                            server_id = conn.get('info', {}).get('id', 'Unknown')
                            print(f"\n  {i}. {server_name}")
                            print(f"     Type: {server_type}")
                            print(f"     ID: {server_id}")
                    else:
                        print("Empty array - No MCP servers configured")
            except Exception as e:
                print(f"Error parsing config: {e}")
    else:
        print("No configurations found in config table")
else:
    print("\nConfig table not found in database")

conn.close()
