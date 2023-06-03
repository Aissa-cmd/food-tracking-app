from typing import Iterable, Optional
from django.contrib.auth.models import AbstractUser
from django.db import models


class GenderOptions(models.TextChoices):
    MALE = ('MALE', 'Male')
    FEMALE = ('FEMALE', 'Female')


class User(AbstractUser):
    class UserRoles(models.TextChoices):
        ADMIN = ('ADMIN', 'Admin')
        ENTRAINEUR = ('ENTRAINEUR', 'Entraineur')
        TRIATHLETE = ('TRIATHLETE', 'Triathlete')

    email = models.EmailField('email address', null=True)
    role = models.CharField(max_length=15, choices=UserRoles.choices)

    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.username}'
    
    class Meta:
        db_table = 'users'


class Triathlete(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_triathlete')
    gender = models.CharField(max_length=10, choices=GenderOptions.choices, null=True)
    date_of_birth = models.DateField(null=True)
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    daily_calories = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    complete_profile_setup = models.BooleanField(default=False)

    class Meta:
        db_table = 'triathletes'


class Entraineur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_entraineur')
    phone_number = models.CharField(max_length=20)

    class Meta:
        db_table = 'entraineurs'


class Aliment(models.Model):
    image = models.ImageField(upload_to='images/')
    name = models.CharField(max_length=255)
    # le poids en gramme
    weight_g = models.DecimalField(max_digits=8, decimal_places=2)
    # Valeur  énergétique (kcal/g)
    energy_value = models.DecimalField(max_digits=8, decimal_places=2)
    # Valeur énergétique totale (kcal)
    total_energy_value = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def save(self, *args, **kwargs):
        self.total_energy_value = self.weight_g * self.energy_value
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'aliments'


class FoodCategory(models.Model):
    category_name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'

    def __str__(self):
        return f'{self.category_name}'

    @property
    def count_food_by_category(self):
        return Food.objects.filter(category=self).count()


class Food(models.Model):
    food_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=7, decimal_places=2, default=100.00)
    calories = models.IntegerField(default=0)
    fat = models.DecimalField(max_digits=7, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=7, decimal_places=2)
    protein = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='food_category')

    def __str__(self):
        return f'{self.food_name} - category: {self.category}'


class Image(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='get_images')
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f'{self.image}'


class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_consumed = models.ForeignKey(Food, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Food Log'
        verbose_name_plural = 'Food Log'

    def __str__(self):
        return f'{self.user.username} - {self.food_consumed.food_name}'


class Weight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=7, decimal_places=2)
    entry_date = models.DateField()

    class Meta:
        verbose_name = 'Weight'
        verbose_name_plural = 'Weight'

    def __str__(self):
        return f'{self.user.username} - {self.weight} kg on {self.entry_date}'
