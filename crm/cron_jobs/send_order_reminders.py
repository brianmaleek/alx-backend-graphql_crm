#!/usr/bin/env python3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

# Set up gql client
transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, verify=True, retries=3)
client = Client(transport=transport, fetch_schema_from_transport=False)

# GraphQL query
query = gql("""
    query GetRecentOrders($since: DateTime!) {
      orders(orderDate_Gte: $since) {
        id
        customer {
          email
        }
      }
    }
""")

def main():
    try:
        since_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        result = client.execute(query, variable_values={"since": since_date})
        orders = result.get("orders", [])
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(LOG_FILE, "a") as log_file:
            for order in orders:
                log_line = f"[{timestamp}] Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n"
                log_file.write(log_line)
        
        print("Order reminders processed!")
        
    except Exception as e:
        error_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        error_line = f"[{error_timestamp}] ERROR: {str(e)}\n"
        
        try:
            with open(LOG_FILE, "a") as log_file:
                log_file.write(error_line)
        except IOError:
            pass
        
        print(f"Error processing order reminders: {e}")

if __name__ == "__main__":
    main()