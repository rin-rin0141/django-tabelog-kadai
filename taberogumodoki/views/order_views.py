from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from taberogumodoki.models import Order, Item
import json
import stripe
from django.conf import settings
from django.views.generic import ListView, DetailView
from django.contrib import messages


class OrderIndexView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "pages/orders.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "pages/order.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        # json to dict
        context["items"] = json.loads(obj.items)
        context["shipping"] = json.loads(obj.shipping)
        return context


class ReserveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = Item.objects.get(pk=pk)
        return render(request, "pages/reserve.html", {"object": item})


class UnreserveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user,
            is_confirmed=True
        )

        with transaction.atomic():
            # 在庫を戻す
            for elem in json.loads(order.items):
                item = Item.objects.select_for_update().get(pk=elem["pk"])

            # Stripe 返金（あれば）
            if order.stripe_payment_intent_id:
                stripe.Refund.create(
                    payment_intent=order.stripe_payment_intent_id
                )

            # 注文削除
            order.delete()

        messages.success(request, "予約をキャンセルしました")
        return redirect("orders")
