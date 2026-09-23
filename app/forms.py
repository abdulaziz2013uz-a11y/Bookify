from django import forms

from .models import Shifoxona


class ShifoxonaForm(forms.ModelForm):
    class Meta:
        model = Shifoxona
        fields = [
            "nomi",
            "manzili",
            "xona_soni",
            "shifokor_soni",
            "bahosi",
            "kunlik_narxi",
            "ochiqmi",
            "emaili",
            "ochilgan_sana",
        ]
        widgets = {
            "nomi": forms.TextInput(
                attrs={"placeholder": "Masalan: Shifo Medical Center"}
            ),
            "manzili": forms.TextInput(
                attrs={"placeholder": "Masalan: Toshkent shahri, Chilonzor"}
            ),
            "xona_soni": forms.NumberInput(
                attrs={"placeholder": "Xonalar soni", "min": "0"}
            ),
            "shifokor_soni": forms.NumberInput(
                attrs={"placeholder": "Shifokorlar soni", "min": "0"}
            ),
            "bahosi": forms.NumberInput(
                attrs={
                    "placeholder": "Masalan: 4.5",
                    "step": "0.1",
                    "min": "0",
                    "max": "5",
                }
            ),
            "kunlik_narxi": forms.NumberInput(
                attrs={
                    "placeholder": "Masalan: 150.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "emaili": forms.EmailInput(
                attrs={"placeholder": "example@gmail.com"}
            ),
            "ochilgan_sana": forms.DateInput(attrs={"type": "date"}),
            "ochiqmi": forms.CheckboxInput(),
        }