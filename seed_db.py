import os
import django
import random
from decimal import Decimal
from datetime import datetime
from faker import Faker

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

# Initialize Faker
faker = Faker()

# clear existing data
def clear_data():
    """Clear existing data from the database."""
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()


# Function to create a customer
def create_customer():
    """Create a new customer."""
    customer = Customer.objects.create(
        name=faker.name(),
        email=faker.email(),
        phone=faker.phone_number()
    )
    print(f"Created customer: {customer.name} with email: {customer.email}")

# Function to create random customers
def create_random_customers(n=10):
    """Create a specified number of random customers."""
    customers = []
    for _ in range(n):
        customers.append(Customer(
            name=faker.name(),
            email=faker.email(),
            phone=faker.phone_number()
        ))
    Customer.objects.bulk_create(customers)
    print(f"Created {Customer.objects.count()} customers.")

# Function to create random products
def create_random_products(n=20):
    """Create a specified number of random products."""
    products = []
    for _ in range(n):
        products.append(Product(
            name=faker.word().capitalize(),
            price=round(Decimal(random.uniform(10.0, 1000.0)), 2),
            stock=random.randint(0, 100)
        ))
    Product.objects.bulk_create(products)
    print(f"Created {Product.objects.count()} products.")

# Function to create random orders
def create_random_orders(n=5):
    """Create a specified number of random orders."""
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())
    
    if not customers or not products:
        print("No customers or products available to create orders.")
        return

    for _ in range(n):
        customer = random.choice(customers)
        order_products = random.sample(products, k=random.randint(1, min(5, len(products))))
        total_amount = sum(product.price for product in order_products)

        order = Order.objects.create(
            customer=customer,
            total_amount=round(Decimal(total_amount), 2),
            order_date=faker.date_time_this_year()
        )
        order.product.set(order_products)
        print(f"Created order {order.id} for customer {customer.name} with total amount {order.total_amount}.")