from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     min_length=8
                                     )
    password2 = serializers.CharField()
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                   )

    class Meta:
        model = CustomUser
        fields = ['email',
                  'password',
                  'password2',
                  'company',
                  'position',
                  'type',
                  'name',
                  'surname',
                  'middle_name',
                  ]

    def save(self, *args, **kwargs):
        user = CustomUser(email=self.validated_data['email'],
                          company=self.validated_data['company'],
                          position=self.validated_data['position'],
                          type=self.validated_data['type'],
                          name=self.validated_data['name'],
                          surname=self.validated_data['surname'],
                          middle_name=self.validated_data['middle_name']
                          )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError[{password: 'Пароль не совпадает'}]
        user.set_password(password)
        user.save()
        return user


class ShopSeriazlier(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                              many=True,
                                              slug_field='name')

    class Meta:
        model = Shop
        fields = ['id', 'url', 'name', 'filename']


class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SlugRelatedField(queryset=Product.objects.all(),
                                            many=True,
                                            slug_field='name')

    class Meta:
        model = Category
        fields = ['id', 'url', 'products']


class ProductSerializer(serializers.ModelSerializer):
    product_info = 'ProductInfoSerializer(many=True)'

    class Meta:
        model = Product
        fields = ['id', 'url', 'model', 'product_info']


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.SlugRelatedField(queryset=Parameter.objects.all(),
                                             slug_field='name')

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(queryset=Product.objects.all(),
                                           slug_field='model')
    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')
    product_parameters = ProductParameterSerializer(many=True)

    class Meta:
        model = ProductInfo
        fields = ['shop', 'product', 'name', 'product_parameters', 'quantity', 'price', 'price_rrc']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(),
                                        many=True,
                                        slug_field='email')
    ordered_items = 'OrderItemSerializer(many=True)'

    class Meta:
        model = Order
        fields = ['url', 'user', 'ordered_items']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(queryset=ProductInfo.objects.all(),
                                           slug_field='name')
    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')

    class Meta:
        model = OrderItem
        fields = ['product', 'shop', 'quantity']
