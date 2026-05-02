from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ReservationForm
from .models import Reservation, Restaurant
from accounts.models import User
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from config import settings
from django.contrib import messages
from django.shortcuts import render, redirect
import stripe
from django.views.generic import CreateView, TemplateView, View
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.forms import SignupForm, LoginForm
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from config import settings
from accounts.models import WebhookEvent
import stripe, logging
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomReservationView(LoginRequiredMixin, TemplateView):
    template_name = "reservation.html"
    def post(self, request, pk, *args, **kwargs):
        # フォームからデータを取得
        try:
            applicable_restaurant = Restaurant.objects.get(pk=pk)
            
        except Restaurant.DoesNotExist:
            messages.error(request, "レストランが見つかりませんでした。")
            return redirect("top_display")
    
        form = ReservationForm(request.POST)
        
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.restaurant = applicable_restaurant
            number_of_people = form.cleaned_data["number_of_people"]
            reservation.reservation_date = form.cleaned_data["reservation_date"]
            reservation.reservation_time = form.cleaned_data["reservation_time"]
            reservation.save()
        
            try:
                checkout_session = stripe.checkout.Session.create(
                    # client_reference_idは、後でWebhookでどのユーザーが支払いをしたのかを識別するために使用する
                    client_reference_id=request.user.id,
                    payment_method_types=["card"],
                    mode="payment",
                    success_url=request.build_absolute_uri("/accounts/reservation_success/"),
                    cancel_url=request.build_absolute_uri("/accounts/reservation_failed/"),
                    line_items=[
                        {
                            "price_data": {
                                            "currency": "jpy",
                                            "unit_amount": applicable_restaurant.price,
                            "product_data": {
                                                "name": applicable_restaurant.name,
                                                },
                                            },
                            "quantity": number_of_people,
                        }],
                        metadata={
                            "reservation_id": reservation.id,
                            "user_id": request.user.id,
                            "restaurant_id": applicable_restaurant.id,
                            },
                )
                return redirect(checkout_session.url)
            
            except Exception as e:
                print(e)
                messages.error(request, "予約の作成に失敗しました。")
                return redirect("top_display")

        else:
            messages.error(request, "予約の作成に失敗しました。")
            return redirect("top_display")

        
class ReceivingWebhookView(View):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            payload = request.body
            sig_header = request.headers.get("Stripe-Signature")
            webhook_secret = settings.STRIPE_WEBHOOK_SECRET

            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

            event_id = event["id"]

            if WebhookEvent.objects.filter(event_id=event_id).exists():
                logger.warning("同じイベントIDがすでに存在しています。")
                return HttpResponse(status=200)

        # そもそも本文の形がおかしい、読めない場合
        except ValueError as e:
            print(e)
            return HttpResponse(status=400)

        # 読めるけど、署名が正しくない場合
        except stripe.error.SignatureVerificationError as e:
            print(e)
            return HttpResponse(status=400)

        event_type = event["type"]

        if event_type == "checkout.session.completed":
            # sessionに、今回の支払いの情報を入れる。
            session = event["data"]["object"]
            # sessionの中に、stripeに預けたclient_reference_idが入っているので、それを取り出す。
            client_reference_id = session["client_reference_id"]

            # キャンセルの時使うので、customer_idとsubscription_idも取り出しておく
            stripe_customer_id = session["customer"]
            stripe_subscription_id = session["subscription"]

            # そのclient_reference_idは、自前のユーザーidと同じなので、それをもとにユーザーを特定する。
            user = User.objects.get(id=client_reference_id)
            # プランのIDを確認するために、sessionの中のpayment_intentを取り出す
            subscription_id = session["payment_intent"]
            # subscription_idでは、変数のように直接プランのIDを取り出せないので、
            # stripeの機能を使って、subscription_idからsubscription_contentsを取り出す
            variable_subscription_contents = stripe.Subscription.retrieve(
                subscription_id
            )
            # 入れ子構造の中の、今回支払ったプランのIDを取り出す
            items_contents = variable_subscription_contents["items"]
            data_contents = items_contents["data"][0]  # (一つ目のitem)
            price_contents = data_contents["price"]
            plan_id = price_contents["id"]
            user.stripe_customer_id = stripe_customer_id
            user.stripe_subscription_id = stripe_subscription_id

            if plan_id == settings.SUBSCRIPTION_PRICE_ID:
                if not user.is_premium:
                    user.is_premium = True
                    user.premium_term = timezone.now() + timezone.timedelta(days=30)
                    user.save()
                    WebhookEvent.objects.create(
                        user=user, event_id=event_id, event_type=event_type
                    )
                    return HttpResponse(status=200)

                else:
                    logger.warning("すでにプレミアムユーザーです。")
                    WebhookEvent.objects.create(
                        user=user, event_id=event_id, event_type=event_type
                    )
                    return HttpResponse(status=200)

            else:
                logger.error("エラー内容")
                return HttpResponse(status=200)

        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]
            user = User.objects.get(stripe_subscription_id=subscription_id)
            user.is_premium = False
            user.premium_term = None
            user.stripe_subscription_id = None
            user.save()
            WebhookEvent.objects.create(
                user=user, event_id=event_id, event_type=event_type
            )
            return HttpResponse(status=200)

        else:
            logger.warning("想定外のイベントタイプです。")
            return HttpResponse(status=200)        
        
        