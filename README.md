# Understanding GraphQL

## Overview

GraphQL is a powerful query language and runtime for APIs, developed by Facebook, that allows clients to request exactly the data they need — nothing more, nothing less. Unlike REST APIs, which return fixed data structures, GraphQL gives clients the flexibility to shape the response format.

We will explore the foundations of GraphQL, understand its advantages over REST, and learn how to implement GraphQL in Django using libraries like `graphene-django`.

## Learning **Objective**s

By the end of this module, we will be able to:

- Explain what GraphQL is and how it differs from REST.
- Describe the key components of a GraphQL schema (types, queries, mutations).
- Set up and configure GraphQL in a Django project using `graphene-django`.
- Build GraphQL queries and mutations to fetch and manipulate data.
- Use tools like `GraphiQL` or Insomnia to interact with GraphQL endpoints.
- Follow best practices to design scalable and secure GraphQL APIs.

## Learning Outcomes

After completing this lesson, we should be able to:

- Implement GraphQL APIs in Django applications.
- Write custom queries and mutations using `graphene`.
- Integrate Django models into GraphQL schemas.
- Optimize performance and security in GraphQL endpoints.
- Explain when to use GraphQL instead of REST in real-world projects.

## Key Concepts

- **GraphQL vs REST**: Unlike REST which has multiple endpoints, GraphQL uses a single endpoint for all operations.
- **Schema**: Defines how clients can access the data. Includes Types, Queries, and Mutations.
- **Resolvers**: Functions that fetch data for a particular query or mutation.
- **Graphene-Django**: A Python library that integrates GraphQL into Django seamlessly.

## Best Practices for Using GraphQL with Django

| Area |  Best Practice |
|:----------------|:--------------------------------------------------|
| **Schema Design** | Keep schema clean and modular. Define reusable types and use clear naming.  |
| **Security** | Implement authentication and authorization in resolvers. Avoid exposing all data.  |
| **Error Handling** | Use custom error messages and handle exceptions gracefully in resolvers. |
| **Pagination** | Implement pagination on large query sets to improve performance. |
| **N+1 Problem** | Use tools like `DjangoSelectRelatedField` or `graphene-django-optimizer`  |
| **Testing** | Write unit tests for your queries and mutations to ensure correctness.  |
| **Documentation** | Use GraphiQL for automatic schema documentation and make it available to clients.|

## Tools & Libraries

- `graphene-django`: Main library to integrate GraphQL in Django
- `GraphiQL`: Browser-based UI for testing GraphQL APIs
- `Django ORM`: Connect your models directly to GraphQL types
- `Insomnia/Postman`: Useful for testing APIs including GraphQL

## Real-World Use Cases

- Airbnb-style applications with flexible data querying
- Dashboards that need precise, real-time data
- Mobile apps with limited bandwidth and specific data needs

## Tasks

### 0. Set Up GraphQL Endpoint

**mandatory**

**Objective**

Set up a GraphQL endpoint and define your first schema and query.

**Instructions**

#### Create Project and App

- Set up a new Django project called `alx-backend-graphql_crm`.
- Create an app named `crm` as the main app.

#### Install Required Libraries

- Install `graphene-django` and `django-filters` using pip:

```bash
pip install graphene-django django-filter
```

### Define GraphQL Schema

- In `alx-backend-graphql/schema.py`, define a `Query` class that inherits from `graphene.ObjectType`.
- Inside it, declare a single field:
  - Name: `hello`
  - Type: `String`
  - It should return a default value of `"Hello, GraphQL!"` when queried.

#### Connect the GraphQL Endpoint

- In `urls.py`, connect the GraphQL endpoint using:

```python
 from django.urls import path
 from graphene_django.views import GraphQLView
 from django.views.decorators.csrf import csrf_exempt

 urlpatterns = [
     path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
 ]
```

### Checkpoint

Visit: [http://localhost:8000/graphql](http://localhost:8000/graphql) to access the GraphiQL interface.
Run the following query:

```json
{
  hello
}
```

**Repo:**

- **GitHub repository**: **alx-backend-graphql_crm**
- **File**: [settings.py](./settings.py), [crm](./crm), [schema.py](./schema.py)

### 1. Task 1: Build and Seed a CRM Database with GraphQL Integration

**mandatory**

**Objective**

Enhance the CRM system by adding GraphQL mutations to create `Customer`, `Product`, and `Order` instances. This includes:

- Bulk customer creation
- Nested order creation with product associations
- Robust validation and error handling

#### Instructions

##### 1. Define the Mutations

In `crm/schema.py`, create the following mutation classes:

#### CreateCustomer

- **Inputs**:
  - name (required, string)
  - email (required, unique email)
  - phone (optional, string)

- **Validations**:
  - Ensure email is unique.
  - Validate phone format (e.g., +1234567890 or 123-456-7890).

- **Behavior**:
  - Saves the customer to the database.
  - Returns the created customer object and a success message.
  - Think: How will you handle validation errors (e.g., duplicate email)?

#### BulkCreateCustomers

- **Inputs**:
  - A list of customers, each with name, email, and optional phone.

- **Behavior**:
  - Validates each customer’s data.
  - Creates customers in a single transaction.
    - Returns:
      - List of successfully created customers.
      - List of errors for failed records.
  - Challenge: Support partial success — create valid entries even if some fail.

#### CreateProduct

- **Inputs**:
  - name (required, string)
  - price (required, positive decimal)
  - stock (optional, non-negative integer, default: 0)

- **Validations**:
Ensure price is positive and stock is not negative.

- **Behavior**:
  - Saves the product to the database.
  - Returns the created product object.

#### CreateOrder

- **Inputs**:
  - customer_id (required, existing customer ID)
  - product_ids (required, list of existing product IDs)
  - order_date (optional, defaults to now)

- **Validations**:
  - Ensure customer and product IDs are valid.
  - Ensure at least one product is selected.

- **Behavior**:
  - Creates an order.
  - Associates specified products.
  - Calculates total_amount as the sum of product prices.
  - Returns the created order object with nested customer and product data.

- **Think**: How will you ensure the total_amount is accurate?
- **Challenge**: Implement custom error handling with user-friendly messages (e.g., “Email already exists”, “Invalid product ID”).

#### 2. Add Mutations to the Schema

In `crm/schema.py`:

  - Define a Mutation class.
  - Add mutation fields:

```python
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
```

- **Hint**: Use Graphene’s `Field` and `List` types appropriately.

#### 3. Integrate Into Main Schema

In `graphql_crm/schema.py`:

- Import `Query` and `Mutation` from `crm.schema`.
- Combine them:

```python
import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

- **Think**: Ensure support for nested objects and graceful error handling.

#### Checkpoint: Test Mutations at /`graphql`

```graphql
# Create a single customer

mutation {
  createCustomer(input: {
    name: "Alice",
    email: "<alice@example.com>",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}

# Bulk create customers

mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
  }
}

# Create a product

mutation {
  createProduct(input: {
    name: "Laptop",
    price: 999.99,
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
  }
}

# Create an order with products

mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
  }
}
```

**Repo:**

- **GitHub repository**: **alx-backend-graphql_crm**
- **File**: [models.py](./models.py),[schema.py](./schema.py), [graphql_crm/schema.py](./graphql_crm/schema.py), [seed_db.py](./seed_db.py)

## 2. Task 2: Implement Complex GraphQL Mutations for CRM

**mandatory**

**Objective**:

Enhance the CRM system by adding GraphQL mutations to create `Customer`, `Product`, and `Order` instances, including bulk customer creation and nested order creation with product associations, with robust validation and error handling.

#### Instructions

##### 1. Define the Mutations

- In `crm/schema.py`, create the following mutation classes:
  - **CreateCustomer**
    - Takes `name` (required, string), `email` (required, unique email), and `phone` (optional, string) as inputs.
    - Validates that the email is unique and the phone number (if provided) matches a valid format (e.g., `+1234567890` or `123-456-7890`).
    - Saves the new customer to the database.
    - Returns the created customer object and a success message.
    - Think: How will you handle validation errors (e.g., duplicate email)?
  - **BulkCreateCustomers**
    - Takes a list of customer inputs, each containing `name`, `email`, and optional `phone`.
    - Validates each customer’s data and creates them in a single transaction.
    - Returns a list of created customers and any errors for failed creations.
    - Challenge: Ensure partial success (valid customers are created even if some fail).
  - **CreateProduct**
    - Takes `name` (required, string), `price` (required, positive decimal), and `stock` (optional, positive integer, default 0).
      - Validates that the price is positive and the `stock` is non-negative.
      - Saves the new product to the database.
      - Returns the created product object.
  - **CreateOrder**
    - Takes `customer_id` (required, ID of an existing customer), `product_ids` (required, list of product IDs), and optional `order_date` (defaults to now).
    - Validates that the customer and products exist and that at least one product is provided.
    - Creates an order, associates the specified products, and calculates `total_amount` as the sum of product prices.
  - Returns the created order object, including nested customer and product details.
  - Think: How will you ensure the `total_amount` is accurate and consistent?
  - Challenge: Implement custom error handling for all mutations, returning user-friendly error messages (e.g., “Email already exists” or “Invalid product ID”).

##### 2. Add Mutations to the Schema

- In `crm/schema.py`, define a `Mutation` class.
- Add fields for each mutation:
  - `create_customer`: Calls CreateCustomer.
  - `bulk_create_customer`s: Calls BulkCreateCustomers.
  - `create_product`: Calls CreateProduct.
  - `create_order`: Calls CreateOrder.

**Hint**: Use Graphene’s Field and List types appropriately for input and output.

##### 3. Integrate Into Main Schema

- In graphql_crm/schema.py:
  - Import `Query` and `Mutation` from `crm.schema`.
  - Combine them into the project’s main schema to support both queries and mutations.
- Think: How will you ensure the schema handles nested objects and errors gracefully?

##### 4. Checkpoint

- Run the following GraphQL mutations at /graphql to verify your setup:

```graphql
# Create a single customer

   mutation {
     createCustomer(input: { name: "Alice", email: "<alice@example.com>", phone: "+1234567890" }) {
       customer {
         id
         name
         email
         phone
       }
       message
     }
   }

# Bulk create customers

   mutation {
     bulkCreateCustomers(input: [
       { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
       { name: "Carol", email: "carol@example.com" }
     ]) {
       customers {
         id
         name
         email
       }
       errors
     }
   }

# Create a product

   mutation {
     createProduct(input: { name: "Laptop", price: 999.99, stock: 10 }) {
       product {
         id
         name
         price
         stock
       }
     }
   }

# Create an order with products

   mutation {
     createOrder(input: { customerId: "1", productIds: ["1", "2"] }) {
       order {
         id
         customer {
           name
         }
         products {
           name
           price
         }
         totalAmount
         orderDate
       }
     }
   }
```

**Repo:**

- **GitHub repository**: **alx-backend-graphql_crm**
- **File**: [schema.py](./schema.py)

### 3. Task 3: Add Filtering

**mandatory**

**Objective**:

Allow users to search for customers using filters such as emails or names

#### Instructions

##### 1. Ensure django-filter is Installed

- Confirm that `django-filter` is installed (previously done with `pip install django-filter`).
- Add '`django_filters`' to `INSTALLED_APPS` in your Django settings if not already present.

##### 2. Create Custom Filter Classes

- In a new file `crm/filters.py`, define the following filter classes using `django-filter`:

**CustomerFilter**: - `name`: Case-insensitive partial match (using `icontains`). - `email`: Case-insensitive partial match (using `icontains`). - `created_at`: Date range filter (e.g., `created_at__gte` and `created_at__lte`). - Challenge: Add a custom filter to match customers with a specific phone number pattern (e.g., starts with `+1`).

**ProductFilter**: - `name`: Case-insensitive partial match. - `price`: Range filter (e.g., `price__gte`, `price__lte`). - `stock`: Exact match or range filter (e.g., `stock__gte`, `stock__lte`). - Think: How can you filter products with low stock (e.g., `stock < 10`)?

**OrderFilter**: - `total_amount`: Range filter (e.g., `total_amount__gte`, `total_amount__lte`). - `order_date`: Date range filter. - `customer_name`: Filter orders by customer’s name (case-insensitive partial match, using related field lookup). - `product_name`: Filter orders by product’s name (case-insensitive partial match, using related field lookup). - Challenge: Allow filtering orders that include a specific product ID.

- **Hint**: Use `django-filter’s` `FilterSet` class and define `Meta` classes to specify the model and fields.

##### 1. Integrate Filters with GraphQL

- In `crm/schema.py`, update the GraphQL `Query` class to support filtered queries:
  - all_customers: Accepts filter arguments for `name`, `email`, `created_at__gte`, `created_at__lte`, and `phone_pattern`.
  - `all_products`: Accepts filter arguments for `name`, `price__gte`, `price__lte`, s`tock__gte`, and `stock__lte`.
  - `all_orders`: Accepts filter arguments for `total_amount__gte`, `total_amount__lte`, `order_date__gte`, `order_date__lte`, `customer_name`, and `product_name`.
  - Challenge: Add an `order_by` argument to sort results (e.g., by `name`, `price`, or `order_date` in ascending/descending order).
- Use Graphene-Django’s `DjangoFilterConnectionField` to integrate the filter classes with GraphQL.
- Define custom input types (e.g., using `graphene.InputObjectType`) for complex filters like date ranges or related field lookups.
- **Think**: How will you handle nested filters for related models (e.g., filtering orders by customer name)?

##### 2. Update the Schema

- Ensure the `Query` class in `crm/schema.py` is updated to include the filtered fields.
- In `graphql_crm/schema.py`, verify that the main schema includes the updated `Query` class from `crm.schema`.
- **Hint**: Test the schema to ensure filters and sorting work correctly.

##### 3. Checkpoint

- Run the following GraphQL queries at `/graphql` to verify your filtering setup:

```graphql
# Filter customers by name and creation date

   query {
     allCustomers(filter: { nameIcontains: "Ali", createdAtGte: "2025-01-01" }) {
       edges {
         node {
           id
           name
           email
           createdAt
         }
       }
     }
   }

# Filter products by price range and sort by stock

   query {
     allProducts(filter: { priceGte: 100, priceLte: 1000 }, orderBy: "-stock") {
       edges {
         node {
           id
           name
           price
           stock
         }
       }
     }
   }

# Filter orders by customer name, product name, and total amount

   query {
     allOrders(filter: { customerName: "Alice", productName: "Laptop", totalAmountGte: 500 }) {
       edges {
         node {
           id
           customer {
             name
           }
           product {
             name
           }
           totalAmount
           orderDate
         }
       }
     }
   }
```

**Repo:**

- **GitHub repository**: **alx-backend-graphql_crm**
- **File**: [crm/schema.py](./crm/schema.py), [alx-backend-graphql_crm/settings.py](./alx-backend-graphql_crm/settings.py), [crm/filters.py](./crm/filters.py)
