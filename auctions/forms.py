from django import forms
from .models import Item, Bid

class ItemForm(forms.ModelForm):
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local'
        })
    )

    class Meta:
        model = Item
        fields = ['title', 'description', 'starting_price', 'end_time', 'image']


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']