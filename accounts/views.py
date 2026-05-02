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
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SignUpView(CreateView):
    form_class = SignupForm
    success_url = "/accounts/login/"
    template_name = "signup.html"

    def form_valid(self, form):
        messages.success(
            self.request, "新規登録が完了しました。続けてログインしてください。"
        )
        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "signup.html"
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, "ログインが完了しました。")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = "/"


class MypageView(LoginRequiredMixin, TemplateView):
    template_name = "mypage.html"


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "password_change.html"


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = "password_change_done.html"


class CustomSubscribeView(LoginRequiredMixin, TemplateView):

    def post(self, request, *args, **kwargs):
        success_url = request.build_absolute_uri("/accounts/subscribe_success/")
        cancel_url = request.build_absolute_uri("/accounts/subscribe_failed/")

        try:
            checkout_session = stripe.checkout.Session.create(
                # client_reference_idは、後でWebhookでどのユーザーが支払いをしたのかを識別するために使用する
                client_reference_id=request.user.id,
                payment_method_types=["card"],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                line_items=[
                    {
                        "price": settings.SUBSCRIPTION_PRICE_ID,
                        "quantity": 1,
                    }
                ],
            )
            return redirect(checkout_session.url)

        except Exception as e:
            print(e)
            return redirect("subscribe_failed")


class CancelSubscribeView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.stripe_subscription_id:
            try:
                stripe.Subscription.modify(
                    user.stripe_subscription_id, cancel_at_period_end=True
                )
                messages.success(request, "プレミアム会員の解約予約が完了しました。" + "\n" + "現在のプレミアム会員の期限までは、引き続きプレミアム会員の特典を利用できます。")
                return redirect("mypage")

            except Exception as e:
                print(e)
                messages.error(request, "プレミアム会員の解約に失敗しました。")
                return redirect("mypage")

        else:
            messages.error(request, "プレミアム会員ではありません。")
            return redirect("mypage")


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

            # プレ垢解約の時使うので、customer_idとsubscription_idも取り出しておく
            stripe_customer_id = session["customer"]
            stripe_subscription_id = session["subscription"]

            # そのclient_reference_idは、自前のユーザーidと同じなので、それをもとにユーザーを特定する。
            user = User.objects.get(id=client_reference_id)
            # プランのIDを確認するために、sessionの中のsubscription_idを取り出す
            subscription_id = session["subscription"]
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


class SuccessSubscribeView(LoginRequiredMixin, TemplateView):
    template_name = "subscribe_success.html"


class FailedSubscribeView(LoginRequiredMixin, TemplateView):
    template_name = "subscribe_failed.html"
