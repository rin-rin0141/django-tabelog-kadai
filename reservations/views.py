from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import ReservationForm
from .models import Reservation, Restaurant
from accounts.models import WebhookEvent
from config import settings
from django.shortcuts import redirect
import stripe
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

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
            reservation.status = 'pending'
            reservation.save()
        
            try:
                checkout_session = stripe.checkout.Session.create(
                    # client_reference_idは、後でWebhookでどのユーザーが支払いをしたのかを識別するために使用する
                    client_reference_id=request.user.id,
                    payment_method_types=["card"],
                    mode="payment",
                    success_url=request.build_absolute_uri("/reservations/reservation_success/"),
                    cancel_url=request.build_absolute_uri("/reservations/reservation_failed/"),
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
                messages.error(request, "決済ページの作成に失敗しました。")
                return redirect("top_display")

        else:
            messages.error(request, "予約の作成に失敗しました。")
            return redirect("top_display")
  
@method_decorator(csrf_exempt, name="dispatch")   
class ReceivingWebhookView(View):

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
            # sessionの中に、stripeに預けたpayment_status,metadataが入っているので、それを取り出す。
            payment_status = session["payment_status"]
            metadata = session["metadata"]
            #reservation_idが無かったらNoneになる
            reservation_id = metadata.get("reservation_id", None)
            #reservation_idをあとで整数として扱う
            try:
                reservation_id = int(reservation_id)
                    
            except (ValueError, TypeError):
                logger.error("予約IDが整数ではありません。")
                return HttpResponse(status=200)

            if payment_status == "paid":
                
                try:
                    reservation = Reservation.objects.get(id=reservation_id)
                    
                    if reservation.status == "pending":
                        reservation.status = "confirmed"
                        reservation.save()
                        WebhookEvent.objects.create(
                            user=reservation.user, event_id=event_id, event_type=event_type
                        )
                        logger.info("支払いが完了しました。")
                        return HttpResponse(status=200)
                    
                    else:
                        logger.warning("予約のステータスがすでに更新されています。")
                        return HttpResponse(status=200)
                    
                except Reservation.DoesNotExist:
                    logger.error("予約が見つかりませんでした。")
                    return HttpResponse(status=200)
            
            else:
                logger.warning("支払いが完了していません。")
                return HttpResponse(status=200)

        else:
            logger.warning("想定外のイベントタイプです。")
            return HttpResponse(status=200)    
        
class ReservationSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "reservation_success.html"   
    
class ReservationFailedView(LoginRequiredMixin, TemplateView):
    template_name = "reservation_failed.html" 
        
        