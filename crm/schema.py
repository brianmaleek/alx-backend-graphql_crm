import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from decimal import Decimal
from graphql import GraphQLError
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from .t
import re

# Define GraphQL types for your models
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

class OrderType(DjangoObjectType):
    total_amount = graphene.Float()  # Custom field to calculate total price
    products = graphene.List(ProductType)  # Custom field to resolve products in the order

    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

    def resolve_products(self, info):
        # Resolve the products field to return a list of products
        return self.products.all()

    def resolve_total_amount(self, info):
        # Resolve the total_amount field to return the total amount of the order
        return self.total_amount

# Input types for mutations
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True, unique=True)
    phone = graphene.String()

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

#  Helper validation function
def is_valid_phone(phone):
    # Check if the phone number is valid (e.g., matches a specific pattern)
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')  # Example pattern for international phone numbers
    return bool(pattern.match(phone))

# Mutations for creating records
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if not input.phone or not is_valid_phone(input.phone):
            raise GraphQLError("Invalid phone number format.")

        # Create a new customer instance
        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        if Customer.objects.filter(email=input.email).exists():
            raise GraphQLError("A customer with this email already exists.")
        if Customer.objects.filter(phone=input.phone).exists():
            raise GraphQLError("A customer with this phone number already exists.")

        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        for item in input:
            try:
                name = item.name
                email = item.email
                phone = item.phone

                if not name or not email:
                    raise GraphQLError("Name and email are required fields.")
                if phone and not is_valid_phone(phone):
                    raise GraphQLError(f"Invalid phone number format. {phone}")
                if Customer.objects.filter(email=email).exists():
                    raise GraphQLError(f"A customer with email {email} already exists.")

                customer = Customer(
                    name=name,
                    email=email,
                    phone=phone
                )

                customer.save()
                created_customers.append(customer)
            except GraphQLError as e:
                errors.append(str(e))
        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(self, info, input):
            name=input.name
            price=Decimal(str(input.price))
            stock=input.stock or 0

            # Validate product fields
            if price <= 0:
                raise GraphQLError("Price must be greater than zero.")
            if stock < 0:
                raise GraphQLError("Stock cannot be negative.")

            product = Product(
                name=name,
                price=price,
                stock=stock
            )

            product.save()
            return CreateProduct(product=product, message="Product created successfully.")

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        customer_id = input.customer_id
        product_ids = input.product_ids
        order_date = input.order_date
        
        if not product_ids:
            raise GraphQLError("At least one product ID must be provided.")
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID.")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise GraphQLError("No products found with the provided IDs.")

        # Ensure that at least one valid product is included in the order
        if len(products) != len(product_ids):
            raise GraphQLError("Some product IDs are invalid or do not exist.")

        total_amount = sum([product.price for product in products])

        order = Order(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date or timezone.now()
        )
        order.save()
        order.product.set(products)  # Set the many-to-many relationship

        return CreateOrder(order=order)

class Query(graphene.ObjectType):
    """
    The root Query class for the GraphQL API, exposing fields to fetch customers, products, and orders.
    Fields:
        - all_customers: List of all customers.
        - all_products: List of all products.
        - all_orders: List of all orders.
    """
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
