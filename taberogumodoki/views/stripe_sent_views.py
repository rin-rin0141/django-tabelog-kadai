import json
import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model
from taberogumodoki.models import Subscription

User = get_user_model()

stripe.api_key = settings.STRIPE_API_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event['type']
    data = event['data']['object']

    # ✅ 初回サブスク作成（決済成功）
    if event_type == 'checkout.session.completed':
        user = User.objects.get(email=data['customer_email'])

        Subscription.objects.update_or_create(
            user=user,
            defaults={
                'stripe_customer_id': data['customer'],
                'stripe_subscription_id': data['subscription'],
                'status': 'active',
            }
        )

    # ❌ 支払い失敗
    elif event_type == 'invoice.payment_failed':
        sub = Subscription.objects.filter(
            stripe_subscription_id=data['subscription']
        ).first()

        if sub:
            sub.status = 'past_due'
            sub.save()

    # 🔄 支払い復活
    elif event_type == 'invoice.payment_succeeded':
        sub = Subscription.objects.filter(
            stripe_subscription_id=data['subscription']
        ).first()

        if sub:
            sub.status = 'active'
            sub.save()

    # 🛑 解約
    elif event_type == 'customer.subscription.deleted':
        sub = Subscription.objects.filter(
            stripe_subscription_id=data['id']
        ).first()

        if sub:
            sub.status = 'canceled'
            sub.save()

    return HttpResponse(status=200)
