from django.views.generic import ListView, DetailView
from taberogumodoki.models import Item, Category, Tag, Reservation
from django.shortcuts import get_object_or_404, render
from taberogumodoki.models.review_models import Review
from django.contrib.auth.mixins import LoginRequiredMixin



class IndexListView(ListView):
    model = Item
    template_name = "pages/index.html"
    queryset = Item.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ←★ 今回追加するのはこれだけ
        context["tags"] = Tag.objects.all()

        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = "pages/item.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = self.object
        context["reviews"] = Review.objects.filter(item=item)

        return context


class CategoryListView(ListView):
    model = Item
    template_name = "pages/list.html"
    paginate_by = 2

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["pk"])
        return Item.objects.filter(is_published=True, category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Category #{self.category.name}"
        return context


class TagListView(ListView):
    model = Item
    template_name = "pages/list.html"
    paginate_by = 2

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs["pk"])
        return Item.objects.filter(is_published=True, tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Tag #{self.tag.name}"
        return context


class SearchView(ListView):
    model = Item
    template_name = "pages/list.html"

    def get_queryset(self):
        qs = Item.objects.filter(is_published=True)

        q = self.request.GET.get("q")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")

        if q:
            qs = qs.filter(name__icontains=q)

        if min_price:
            qs = qs.filter(price__gte=min_price)

        if max_price:
            qs = qs.filter(price__lte=max_price)

        return qs
    
class ReserveListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ログインユーザーの予約を取得
        context['reservations'] = Reservation.objects.filter(user=self.request.user)
        return context

