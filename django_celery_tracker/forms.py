from django.forms import ModelForm

from .models import TextForm


class TextFormModelForm(ModelForm):
    class Meta:
        model = TextForm
        fields = ["text"]
