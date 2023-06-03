from django import forms

from .models import Food, Image, GenderOptions


class FoodForm(forms.ModelForm):
    '''
    A ModelForm class for adding a new food item
    '''
    class Meta:
        model = Food
        fields = ['food_name', 'quantity', 'calories', 'fat', 'carbohydrates', 'protein', 'category']

    def __init__(self, *args, **kwargs):
        super(FoodForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class ImageForm(forms.ModelForm):
    '''
    A ModelForm class for adding an image to the food item
    '''
    class Meta:
        model = Image
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = 'form-control'


class EntraineurForm(forms.Form):
    first_name = forms.CharField(label='Nom')
    last_name = forms.CharField(label='Prénom')
    email = forms.EmailField(label='E-main', required=False)
    phone_number = forms.CharField(label='Numéro de téléphone')
    password1 = forms.CharField(label='Mot de passe')
    password2 = forms.CharField(label='Confirmez le mot de passe')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data['password1']
        password2 = cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError({'password2': 'Les deux mots de passe ne correspondent pas'})
        return cleaned_data
    

class EntraineurEditForm(forms.Form):
    first_name = forms.CharField(label='Nom')
    last_name = forms.CharField(label='Prénom')
    email = forms.EmailField(label='E-main', required=False)
    phone_number = forms.CharField(label='Numéro de téléphone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class TriathleteForm(forms.Form):
    first_name = forms.CharField(label='Nom')
    last_name = forms.CharField(label='Prénom')
    # email = forms.EmailField(label='E-main')
    # date_of_birth = forms.DateField(label='Date de naissance')
    # gender = forms.ChoiceField(label='Sexe', choices=GenderOptions.choices)
    # address = forms.CharField(label='Adresse')
    # phone_number = forms.CharField(label='Numéro de téléphone')
    # weight = forms.CharField(label='weight')
    # height = forms.CharField(label='height')
    password1 = forms.CharField(label='Mot de passe')
    password2 = forms.CharField(label='Confirmez le mot de passe')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data['password1']
        password2 = cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError({'password2': 'Les deux mots de passe ne correspondent pas'})
        return cleaned_data
    
class TriathleteEditForm(forms.Form):
    first_name = forms.CharField(label='Nom')
    last_name = forms.CharField(label='Prénom')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
