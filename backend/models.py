from django.db import models

from users.models import CustomUser

CONTACT_CHOICES = (
    ('phone', 'Номер телефона'),
    ('address', 'Адрес'),
)


class Shop(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    filename = models.CharField(max_length=80, verbose_name='Имя файла', null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины',
                                   related_name='categories',
                                   blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    model = models.CharField(max_length=80, verbose_name='Модель')
    category = models.ForeignKey(Category, verbose_name='Категория',
                                 related_name='products',
                                 blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-model',)

    def __str__(self):
        return self.model


class ProductInfo(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    product = models.ForeignKey(Product,
                                verbose_name='Продукт',
                                related_name='product_info',
                                blank=True,
                                on_delete=models.CASCADE)

    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='product_info',
                             blank=True,
                             on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(verbose_name='Количество')

    price = models.PositiveIntegerField(verbose_name='Цена')

    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"


class Parameter(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имен параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE)

    parameter = models.ForeignKey(Parameter, verbose_name='Параметр',
                                  related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)

    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"


class Order(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='Пользователь',
                             related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)

    # ordered_items

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ',
                              related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)

    product = models.ForeignKey(ProductInfo,
                                verbose_name='Продукт',
                                related_name='ordered_items',
                                blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='ordered_items',
                             blank=True,
                             on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order', 'product', 'shop'],
                                    name='unique_order_item'),
        ]


class Contact(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)
    type = models.CharField(verbose_name='Тип контакта',
                            choices=CONTACT_CHOICES,
                            max_length=50)
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.type} : {self.value}'
