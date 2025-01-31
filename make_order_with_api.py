import json
import time
from datetime import datetime, timedelta
import requests


def create_and_pay_order(ENV: str, num_orders: int, delivery_type: str, request_source: str, delivery_day: str = ""):
    start_time = time.time()

    # Если delivery_day не передан, используем завтрашнюю дату
    if not delivery_day:
        now = datetime.now()
        delivery_date = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    else:
        # Если передан конкретный день, конвертируем его в нужный формат
        try:
            delivery_date = datetime.strptime(delivery_day, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except ValueError:
            print("Ошибка: неверный формат даты. Используйте формат 'YYYY-MM-DD'.")
            return
    for order_num in range(num_orders):
        phone_number = "+7 (999) 999 77 65"  # телефон тестового аккаунта
        code_test_account = 7981



        # =================================================
        # send sms
        url = f"https://api2.{ENV}.azalia-now.ru/v1/api/auth/send-code"
        payload = json.dumps({
            "phone": phone_number
        })
        headers = {
            'accept': 'application/json',
            'request-source': request_source,
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        customer_id = response.json()['data']['customerId']
        # print("Customer ID:", customer_id)

        # =================================================
        # auth with sms code
        url = f"https://api2.{ENV}.azalia-now.ru/v1/api/auth/login"
        payload = json.dumps({
            "customerId": customer_id,
            "code": code_test_account
        })
        headers = {
            'request-source': request_source,
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        access_token = response.json()['data']['accessToken']
        refresh_token = response.json()['data']['refreshToken']
        # print("Access Token:", access_token)
        # print("Refresh Token:", refresh_token)

        # =================================================
        # make delivery
        if delivery_type != 'self':
            url = f"https://api2.{ENV}.azalia-now.ru/v2/api/deliveries"

            payload = json.dumps({
                "latitude": "55.7558",
                "longitude": "37.6173",
                "city": "Москва",
                "delivery_date": delivery_date
            })
            headers = {
                'Authorization': access_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Cookie': f'accessToken={access_token}; refreshToken={refresh_token}'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
            delivery_id = response.json()['data']['id']
            print("Delivery_id:", delivery_id)
        else:
            delivery_id = None
        # =====================================================
        # check data customer
        url = f"https://api2.{ENV}.azalia-now.ru/v1/api/customers/{customer_id}"

        payload = {}
        headers = {
            'accept': 'application/json',
            'Authorization': access_token,
            'Cookie': f'accessToken={access_token}; refreshToken={refresh_token}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        # print(response.text)
        customer_name = response.json()['data']['name']
        customer_phone = response.json()['data']['phone']
        # print(customer_name)
        # print(customer_phone)

        # =============================================
        # create order
        url = f"https://api2.{ENV}.azalia-now.ru/v1/api/orders/create"
        payload = {
            "items": [
                {
                    "id": "419",
                    "amount": 1,
                    "name": "Огромный шикарный букет из 151 розовой розы",
                    "image": "https://azalianow.ru/images/19_1_buket_cvetov_azalianow_8557e94bc9.webp",
                    "quantity": 1,
                    "product_id": "419",
                    "price_per_one": 33620,
                    "promocode_available": False,
                    "is_payable_service": False
                },
                {
                    "id": "11169",
                    "amount": 1,
                    "name": "101 белая кустовая пионовидная роза, Голландия",
                    "image": "https://azalianow.ru/images/azalianow_moskva_buket_101_belaya_pionovidnaya_kustovaya_roza_neveste_kupit_zakaz_dostavka_01_ca0ae1b733.webp",
                    "quantity": 1,
                    "product_id": "11169",
                    "price_per_one": 52520,
                    "promocode_available": True,
                    "is_payable_service": False
                }
            ],
            "location": {
                "address": 'г. Москва, 2-й Хорошевский проезд, д. 7, стр. 17',
                "flat": "САМОВЫВОЗ",
                "dueDate": delivery_date,
                "dueTime": "10:00 - 13:00" if delivery_type == 'self' else "21:00 - 00:00",
                "latitude": "55.772755" if delivery_type == 'self' else "55.809904",
                "longitude": "37.533149" if delivery_type == 'self' else "37.703749",
                "city": "Москва",
                "organizationName": "AzaliaNow" if delivery_type == 'self' else ""
            },
            "recipient": {
                "name": "Клим",
                "phone": "+7 (999) 123 45 67"
            },
            "customer": {
                "name": customer_name,
                "phone": customer_phone,
                "email": ""
            },
            "paymentMethod": {
                "system": "tinkoff",
                "type": "default_tinkoff_bank"
            },
            "comment": "",
            "deliveryId": 0 if delivery_type == 'self' else delivery_id,
            "deliveryType": delivery_type,
            "deliveryTariff": "self" if delivery_type == 'self' else "default",
            "deductPoints": 0,
            "postcard": "",
            "isSelfDelivery": True if delivery_type == 'self' else False,
            "isAnonymousDelivery": False,
            "promocode": "",
            "isSurprise": False
        }

        headers = {
            'Cookie': f'accessToken={access_token}; refreshToken={refresh_token}',
            'Accept': "application/json",
            'Content-Type': "application/json",
            'Authorization': access_token,
            'request-source': request_source
        }

        response = requests.post(url, headers=headers, json=payload)

        # print(response.status_code)
        # print(response.json())
        uid = response.json()['data']['UID']

        # print("UID:", uid)

        # make payment
        url = f"https://api2.{ENV}.azalia-now.ru/v1/api/payment/status"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        data = {
            "uid": uid,
            "status": "payment_success",
            "paymentProvider": "tinkoff",
            "paymentSystemStatus": "CONFIRMED"
        }

        response = requests.post(url, headers=headers, json=data)


        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'Время создания и оплаты заказов в количестве: {num_orders} составляет: {execution_time:.4f} секунд')


create_and_pay_order(ENV='preprod',  # preprod, staging, test1
                     num_orders=300,  # количество заказов
                     delivery_type="self",  # internal, external, self  тип доставки
                     request_source="web",  # web, mobile
                     delivery_day="2025-02-01")  # год месяц день доставки


