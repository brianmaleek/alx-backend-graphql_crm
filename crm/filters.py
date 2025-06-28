import django_filters
from .models import Customer, Product, Order
from django.db.models import Q

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    phone_startswith = django_filters.CharFilter(method='filter_phone_startswith')

    # Filter customers whose phone starts with a specific value or is null
    def filter_phone_startswith(self, queryset, name, value):
        if value:
            return queryset.filter(Q(phone__startswith=value) | Q(phone__isnull=True))
        return queryset

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at__gte', 'created_at__lte', 'phone_startswith']


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    # Filter products with stock less than 10 if low_stock is True
    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = ['name', 'price__gte', 'price__lte', 'stock__gte', 'stock__lte', 'low_stock']

class OrderFilter(django_filters.FilterSet):
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date__gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date__lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    product_id = django_filters.NumberFilter(method='filter_product_id')

    # Filter by product name
    def filter_product_name(self, queryset, name, value):
        if value:
            return queryset.filter(product__name__icontains=value)
        return queryset

    # Filter by product ID
    def filter_product_id(self, queryset, name, value):
        if value:
            return queryset.filter(product__id=value)
        return queryset

    class Meta:
        model = Order
        fields = ['total_amount__gte', 'total_amount__lte', 'order_date__gte', 'order_date__lte']
