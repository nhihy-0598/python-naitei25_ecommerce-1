from core.models import Product
from django import forms
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Product Title"), "class":"form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _("Product Description"), "class":"form-control"}))
    amount = forms.DecimalField(
        required=True,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'placeholder': _("Sale Price"), 
            'class': "form-control",
            'step': '0.01'
        })
    )
    old_price = forms.DecimalField(
        decimal_places=2,
        max_digits=10,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': _("0.00"),
            'class': "form-control",
            'step': '0.01',
            'min': '0'
        })
    )
    type = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Type of product e.g organic cream"), "class":"form-control"}))
    stock_count = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': _("How many are in stock?"), "class":"form-control"}))
    life = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("How long would this product live?"), "class":"form-control"}))
    mfd = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder': _("e.g: 22-11-02"), "class":"form-control"}))
    tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Tags"), "class":"form-control"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}))

    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'amount',
            'old_price',
            'specifications',
            'type',
            'stock_count',
            'life',
            'mfd',
            'tags',
            'digital',
            'category'
        ]

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError(_("Price must be greater than 0"))
        return amount
