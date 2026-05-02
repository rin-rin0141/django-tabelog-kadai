from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from .models import Restaurant
from .forms import ReviewForm

class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurant/pages/restaurant_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurants = Restaurant.objects.filter(is_published=True)
        
        applicable_reviews = self.object.reviews.all()
        context['results'] = applicable_reviews
        
        context['ADDITIONAL_ITEMS'] = restaurants
        return context
        
    
    
#requestは、ユーザーからのGETやPOSTなどの送信されたデータを含んでいる
def search_result(request):
    max_price = request.GET.get("upper")
    min_price = request.GET.get("lower")
    query = request.GET.get("q")
    results = Restaurant.objects.filter(is_published=True)
    
    if query :
        results = Restaurant.objects.filter(is_published=True, name__icontains=query)
    
        if max_price :
            results = Restaurant.objects.filter(is_published=True, name__icontains=query, price__lte=max_price)
            
            if min_price :
                results = Restaurant.objects.filter(is_published=True, name__icontains=query, price__lte=max_price, price__gte=min_price)
                
        if min_price and not max_price :
            results = Restaurant.objects.filter(is_published=True, name__icontains=query, price__gte=min_price)
                
    elif not query and max_price :
        results = Restaurant.objects.filter(is_published=True, price__lte=max_price)
        
        if min_price :
            results = Restaurant.objects.filter(is_published=True, price__lte=max_price, price__gte=min_price)
            
    elif not query and min_price and not max_price :
        results = Restaurant.objects.filter(is_published=True, price__gte=min_price)
        
    elif not query and not max_price and not min_price :
        results = Restaurant.objects.none()

    #requestの情報を使って、search_result.html にデータを渡してHTMLを作って、それをブラウザに返す
    return render(request, "restaurant/pages/search_result.html", {"q":query, "results":results})

def category_result(request, slug):
    #iexactは完全一致するものを検索するフィルター
    results = Restaurant.objects.filter(is_published=True, category__slug__iexact=slug)
        
    return render(request, "restaurant/pages/search_result.html", {"results": results})

def tag_result(request, slug):
    results = Restaurant.objects.filter(is_published=True, tags__slug__iexact=slug)
        
    return render(request, "restaurant/pages/search_result.html", {"results": results})

def reviewkeep(request, pk):
    if request.method == "POST" :
        applicable_restaurant = get_object_or_404(Restaurant, pk=pk)
        #フォームの受け取り
        form = ReviewForm(request.POST)
        if form.is_valid() :
            review = form.save(commit=False)
            review.restaurant = applicable_restaurant
            review.user = request.user
            review.save()
            return redirect('restaurant:restaurant_detail', pk=applicable_restaurant.pk)
        
        else :
            return redirect('restaurant:restaurant_detail', pk=pk)
        
    else :
        return redirect('restaurant:restaurant_detail', pk=pk)
            
    
    
    

