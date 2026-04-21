import requests, json
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def create_checkout(user, plan='pro', success_url='', cancel_url=''):
    payload = {
        'vendor_id': settings.PADDLE_VENDOR_ID,
        'vendor_auth_code': settings.PADDLE_API_KEY,
        'product_id': settings.PADDLE_PRODUCT_ID,
        'customer_email': user.email,
        'passthrough': json.dumps({'user_id': user.id, 'plan': plan}),
        'return_url': success_url,
    }
    r = requests.post('https://vendors.paddle.com/api/2.0/product/generate_pay_link', data=payload)
    data = r.json()
    if data.get('success'):
        return data['response']['url']
    raise Exception(f"Paddle error: {data}")

def activate_plan(user, plan='pro'):
    profile = user.profile
    profile.plan = plan
    profile.pro_since = timezone.now()
    profile.pro_expires = timezone.now() + timedelta(days=30)
    profile.save()
