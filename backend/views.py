from django.contrib.sites import requests
from django.core.mail import send_mail
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.http import JsonResponse, Http404
import requests
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader

from backend.models import Shop, Category, Product, ProductInfo, ProductParameter, Parameter, Order, OrderItem
from backend.serializers import ProductInfoSerializer, OrderSerializer, OrderItemSerializer
from diplom_new.settings import EMAIL_HOST_USER


class PartnerUpdate(APIView):
    """
    Updates products in shops from json or yaml files
    """

    name = 'partner-update'
    throttle_scope = 'update-shop'
    throttle_classes = (ScopedRateThrottle,)

    def yaml_uploader(self, request, stream):

        data = load_yaml(stream, Loader=Loader)
        shop, created = Shop.objects.get_or_create(name=data['shop'])
        for category in data['categories']:
            try:
                category_object, created = Category.objects.get_or_create(id=category['id'], name=category['name'])
                category_object.shops.add(shop.id)
                category_object.save()

            except IntegrityError:
                continue
        ProductInfo.objects.filter(shop=shop.id).delete()
        for item in data['goods']:
            try:
                product, created = Product.objects.get_or_create(model=item['model'],
                                                                 category=Category.objects.get(id=item['category'])
                                                                 )
            except IntegrityError:
                continue
            product_info = ProductInfo.objects.create(product=product,
                                                      name=item['name'],
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop=shop)
            for name, value in item['parameters'].items():
                parameter_object, created = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info=product_info,
                                                parameter=parameter_object,
                                                value=value)

        return JsonResponse({'Status': True})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        if request.data.get('url'):
            url = request.data.get('url')
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as error:
                return JsonResponse({'Status': False, 'Error': str(error)})
            else:
                stream = requests.get(url).content
                return self.yaml_uploader(stream)

        if request.data.get('filename'):
            file = request.data.get('filename')
            with open(file, 'r', encoding='utf-8') as stream:
                return self.yaml_uploader(request=request, stream=stream)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List or retrieve product
    """
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    List, create, retrieve, update or destroy order
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, ordered_items=[])


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    List, create, retrieve, update or destroy ordered items
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def post(self, request):
        serializer = OrderItemSerializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            serializer.save()
            send_email(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        order = serializer.data['order']
        user = serializer.context['request'].user
        send_email(order=order, user=user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        order = serializer.data['order']
        user = serializer.context['request'].user
        send_email(order=order, user=user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


def send_email(order, user):
    data = (
        'Изменение заказа',
        f'Заказ {order} изменился.',
        EMAIL_HOST_USER,
        [user]
    )
    return send_mail(*data)
