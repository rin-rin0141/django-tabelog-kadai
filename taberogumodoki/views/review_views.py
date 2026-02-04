from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from taberogumodoki.forms import ReviewForm
from django.shortcuts import render, redirect
from taberogumodoki.models.review_models import Review



@login_required
def create_review(request, item_id):
    if not request.user.is_paid:
        return HttpResponseForbidden("プレミアム会員のみレビューできます")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.item_id = item_id
            review.save()
            return redirect("item_detail", pk=item_id)
    else:
        form = ReviewForm()

    return render(request, "pages/review_form.html", {"form": form, "item_id": item_id,})
