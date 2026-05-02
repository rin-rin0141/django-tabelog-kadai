from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('title', 'content', 'rating')

    title = forms.CharField(max_length=40, required=True)
    content = forms.CharField(widget=forms.Textarea, required=True)
    rating = forms.IntegerField(max_value=5, min_value=1, required=True)