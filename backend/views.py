from django.contrib.sites import requests
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
import requests
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader

from backend.models import Shop, Category, Product, ProductInfo, ProductParameter, Parameter


class PartnerUpdate(APIView):

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
