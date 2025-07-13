#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportError

# Configuration
GRAPHQL_URL = os.getenv("GRAPHQL_URL", "http://localhost:8000/graphql")
LOG_DIR = os.getenv("LOG_DIR", "/tmp")
HEARTBEAT_LOG = os.path.join(LOG_DIR, "crm_heartbeat_log.txt")
LOW_STOCK_LOG = os.path.join(LOG_DIR, "low_stock_updates_log.txt")

def create_graphql_client():
    """Create and return a GraphQL client."""
    transport = RequestsHTTPTransport(
        url=GRAPHQL_URL, 
        verify=True, 
        retries=2,
        timeout=30
    )
    return Client(transport=transport, fetch_schema_from_transport=False)

def ensure_log_directory():
    """Ensure the log directory exists."""
    os.makedirs(LOG_DIR, exist_ok=True)

def log_crm_heartbeat():
    """Log CRM heartbeat and perform GraphQL health check."""
    ensure_log_directory()
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"
    
    # Write heartbeat message
    try:
        with open(HEARTBEAT_LOG, "a") as log_file:
            log_file.write(log_message)
    except IOError as e:
        print(f"Error writing to heartbeat log: {e}", file=sys.stderr)
        return False
    
    # GraphQL hello check
    try:
        client = create_graphql_client()
        query = gql("{ hello }")
        result = client.execute(query)
        
        with open(HEARTBEAT_LOG, "a") as log_file:
            hello_response = result.get('hello', 'No response')
            log_file.write(f"{timestamp} GraphQL hello response: {hello_response}\n")
        
        return True
        
    except (TransportError, Exception) as e:
        try:
            with open(HEARTBEAT_LOG, "a") as log_file:
                log_file.write(f"{timestamp} GraphQL hello check failed: {str(e)}\n")
        except IOError:
            print(f"Error writing to log and GraphQL failed: {e}", file=sys.stderr)
        
        return False

def update_low_stock():
    """Update low stock products via GraphQL mutation."""
    ensure_log_directory()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        client = create_graphql_client()
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    updatedProducts
                    message
                }
            }
        """)
        
        result = client.execute(mutation)
        update_result = result.get("updateLowStockProducts", {})
        updated_products = update_result.get("updatedProducts", [])
        message = update_result.get("message", "No message")
        
        with open(LOW_STOCK_LOG, "a") as log_file:
            log_file.write(f"{timestamp} - {message}\n")
            
            if updated_products:
                for product in updated_products:
                    log_file.write(f"{timestamp} - Updated: {product}\n")
            else:
                log_file.write(f"{timestamp} - No products updated\n")
        
        return True
        
    except (TransportError, Exception) as e:
        try:
            with open(LOW_STOCK_LOG, "a") as log_file:
                log_file.write(f"{timestamp} - Low stock update failed: {str(e)}\n")
        except IOError:
            print(f"Error writing to log and update failed: {e}", file=sys.stderr)
        
        return False

def main():
    """Main function to run both operations."""
    print("Starting CRM operations...")
    
    # Run heartbeat
    heartbeat_success = log_crm_heartbeat()
    if heartbeat_success:
        print("✓ Heartbeat logged successfully")
    else:
        print("✗ Heartbeat failed")
    
    # Run low stock update
    stock_success = update_low_stock()
    if stock_success:
        print("✓ Low stock update completed")
    else:
        print("✗ Low stock update failed")
    
    # Exit with appropriate code
    sys.exit(0 if heartbeat_success and stock_success else 1)

if __name__ == "__main__":
    main()