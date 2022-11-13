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
        fields = ['id', 'name', 'filename']


class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SlugRelatedField(queryset=Product.objects.all(),
                                            many=True,
                                            slug_field='name')

    class Meta:
        model = Category
        fields = ['id', 'products']


class ProductSerializer(serializers.ModelSerializer):
    product_info = 'ProductInfoSerializer(many=True)'

    class Meta:
        model = Product
        fields = ['id', 'model', 'product_info']


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


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    product = serializers.SlugRelatedField(queryset=ProductInfo.objects.all(),
                                           slug_field='name')
    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')
    order = serializers.HyperlinkedRelatedField(queryset=Order.objects.all(),
                                                view_name='order-detail')
    class Meta:
        model = OrderItem
        fields = ['url', 'order', 'product', 'shop', 'quantity']



class OrderItemSerializer1(serializers.HyperlinkedModelSerializer):
    """"serializer for ordered_items field"""
    product = serializers.SlugRelatedField(queryset=ProductInfo.objects.all(),
                                           slug_field='name')
    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')

    class Meta:
        model = OrderItem
        fields = ['url', 'product', 'shop', 'quantity']


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.SlugRelatedField(read_only=True,
                                        slug_field='email')
    ordered_items = OrderItemSerializer1(many=True)

    def create(self, validated_data):
        instance = Order.objects.create(user=validated_data['user'])
        return instance

    class Meta:
        model = Order
        fields = ['url', 'id', 'user', 'ordered_items']
