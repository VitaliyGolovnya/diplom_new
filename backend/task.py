import dramatiq
from django.core.mail import send_mail

from diplom_new.settings import EMAIL_HOST_USER


@dramatiq.actor
def send_email(order, user):
    data = (
        'Изменение заказа',
        f'Заказ {order} изменился.',
        EMAIL_HOST_USER,
        [user]
    )
    return send_mail(*data)
