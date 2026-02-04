import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

stripe.api_key = settings.STRIPE_API_SECRET_KEY


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request):
        checkout_session = stripe.checkout.Session.create(
            mode='subscription',
            payment_method_types=['card'],
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,  # ← StripeのPrice ID
                    'quantity': 1,
                }
            ],
            customer_email=request.user.email,
            success_url=f'{settings.MY_URL}/subscribe/success/',
            cancel_url=f'{settings.MY_URL}/subscribe/cancel/',
        )

        return redirect(checkout_session.url)
    

