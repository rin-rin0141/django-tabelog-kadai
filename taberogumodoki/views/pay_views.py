from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.conf import settings
from taberogumodoki.models import Item, Order
import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
import json
from django.contrib import messages

stripe.api_key = settings.STRIPE_API_SECRET_KEY


def create_line_item(unit_amount, name, quantity):
    return {
        "price_data": {
            "currency": "jpy",
            "unit_amount": unit_amount,
            "product_data": {
                "name": name,
            },
        },
        "quantity": quantity,
        "tax_rates": [settings.STRIPE_TAX_RATE_ID],  # ← ここ重要
    }


def check_profile_filled(profile):
    if not profile.name:
        return False
    if not profile.zipcode:
        return False
    if not profile.prefecture:
        return False
    if not profile.city:
        return False
    if not profile.address1:
        return False
    return True


class PaySuccessView(LoginRequiredMixin, TemplateView):
    template_name = "pages/success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")

        order = Order.objects.filter(
            user=request.user,
            is_confirmed=False,
            stripe_session_id=session_id,
        ).first()

        if not order:
            messages.error(request, "注文が見つかりませんでした。もう一度お試しください。")
            return redirect("/cart/")

        # ✅ payment_intent_id を保存（返金に使える）
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            order.stripe_payment_intent_id = session.payment_intent
            order.save()
        except Exception:
            pass

        with transaction.atomic():
            for elem in json.loads(order.items):
                item = Item.objects.select_for_update().get(pk=elem["pk"])
                item.stock = F("stock") - elem["quantity"]
                item.sold_count = F("sold_count") + elem["quantity"]
                item.save()

            order.is_confirmed = True
            order.save()

        del request.session["cart"]
        return super().get(request, *args, **kwargs)


from django.db import transaction
from django.db.models import F


class PayWithStripe(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        # プロフィールチェック
        if not check_profile_filled(request.user.profile):
            messages.error(request, "プロフィールを埋めないと予約できません。")
            return redirect("/profile/")

        cart = request.session.get("cart")
        if not cart or not cart.get("items"):
            messages.error(request, "カートが空です。")
            return redirect("/")

        items = []
        line_items = []

        with transaction.atomic():

            for item_pk, quantity in cart["items"].items():
                item = Item.objects.select_for_update().get(pk=item_pk)

                # ✅ 在庫チェック
                if item.stock < quantity:
                    messages.error(request, f"{item.name} の在庫が足りません")
                    return redirect("/")

                line_items.append(create_line_item(item.price, item.name, quantity))

                items.append(
                    {
                        "pk": item.pk,
                        "name": item.name,
                        "image": str(item.image),
                        "price": item.price,
                        "quantity": quantity,
                    }
                )

        # 仮注文作成（← order 変数に入れる）


        order = Order.objects.create(
            user=request.user,
            uid=request.user.pk,
            items=json.dumps(items),
            shipping=serializers.serialize("json", [request.user.profile]),
            amount=cart["total"],
            tax_included=cart["tax_included_total"],
            reserve_date=cart["reserve_date"],
            reserve_time=cart["reserve_time"],
        )

        # Stripe セッション（DB確定後）
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            # ✅ session_id を success に付ける（超重要）
            success_url=f"{settings.MY_URL}/pay/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.MY_URL}/pay/cancel/",
        )

        # ✅ Order と Stripe を紐づけ保存
        order.stripe_session_id = checkout_session.id
        order.save()

        return redirect(checkout_session.url)


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request):
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.STRIPE_PRICE_ID,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=settings.MY_URL + "/subscribe/success/",
            cancel_url=settings.MY_URL + "/subscribe/cancel/",
        )
        return redirect(checkout_session.url)


class SubscribeSuccessView(TemplateView):
    template_name = "pages/subscribe_success.html"

    def get(self, request, *args, **kwargs):
        request.user.is_paid = True
        request.user.save()
        return super().get(request, *args, **kwargs)


class SubscribeCancelView(LoginRequiredMixin, View):
    def post(self, request):
        request.user.is_paid = False
        request.user.save()
        messages.success(request, "プレミアム会員を退会しました。")
        return redirect("/")
