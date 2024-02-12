import uuid

from yookassa import Configuration, Payment

from TestBotShop.settings import env


def create_pay_iokassa(price: int) -> (str, int):
    """
    Create link for pay Юcassa
    :return: link for pay and id order
    """
    Configuration.account_id = env.int('SHOPID')
    Configuration.secret_key = env('SECRET_KEY_IOKASSA')

    name_subscribe = 'Обработка данных'

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f"{price}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{env('REDIRECT_URL')}"
        },
        "capture": True,
        "description": f"{name_subscribe}",
        "receipt": {
            "customer": {
                "email": "ledsfnsdfnn95sdfsdfjn@icloud.com",
            },
            "items": [
                {
                    "description": "Оffданных",
                    "quantity": "1.00",
                    "amount": {
                        "value": price,
                        "currency": "RUB"
                    },
                    "vat_code": "1",
                    "payment_subject": "service",
                },
            ]}}, idempotence_key)

    url = payment.confirmation.confirmation_url

    return url, payment.id