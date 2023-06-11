from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class GenderOptions(models.TextChoices):
    MALE = ('MALE', 'Male')
    FEMALE = ('FEMALE', 'Female')


class AlimentCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'alimentcategories'


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
    class PhysicalActivityLevel(models.TextChoices):
        # LESS_1H_WEEK  = ('LESS_1H_WEEK', "<1h d'exercice par semaine")
        # ONEH_3H_WEEK  = ('ONEH_3H_WEEK', "1h à 3h d'exercise par semaine")
        # FOURH_6H_WEEK = ('FOURH_6H_WEEK', "4h à 6h d'exercise par semaine")
        # GREAT_6H_WEEK = ('GREAT_6H_WEEK', ">6h d'exercice par semaine")
        TWELVE_15H_WEEK = ('TWELVE_15H_WEEK', "12h à 15h d'exercice par semaine")
        MORE_20H_WEEK = ('MORE_20H_WEEK', ">20h d'exercice par semaine")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_triathlete')
    image = models.ImageField(upload_to='profile-images/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GenderOptions.choices, null=True)
    date_of_birth = models.DateField(null=True)
    age = models.IntegerField(null=True)
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    complete_profile_setup = models.BooleanField(default=False)
    masse_masculaire = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    imc = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    mass_grasse = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    niveau_activite = models.CharField(max_length=15, choices=PhysicalActivityLevel.choices)
    metabolisme_de_base = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    depense_energetique_journaliere = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # daily_water_consumption in ml
    daily_water_consumption = models.DecimalField(max_digits=8, decimal_places=2, null=True)

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
    category = models.ForeignKey(AlimentCategory, null=True, on_delete=models.SET_NULL, related_name='aliments')
    # le poids en gramme
    weight_g = models.DecimalField(max_digits=8, decimal_places=2)
    # Valeur  énergétique (kcal/g)
    energy_value = models.DecimalField(max_digits=8, decimal_places=2)
    # Valeur énergétique totale (kcal)
    total_energy_value = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    protein =  models.DecimalField(max_digits=7, decimal_places=2)
    carboheidrates = models.DecimalField(max_digits=7, decimal_places=2)
    fat = models.DecimalField(max_digits=7, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_energy_value = self.weight_g * self.energy_value
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'aliments'


class DailyFood(models.Model):
    date = models.DateField(default=timezone.now)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dailyfoods')
    # daily_water_consumption in ml
    daily_water_consumption = models.DecimalField(max_digits=8, decimal_places=2)
    # water_goal in ml
    water_consumption_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = 'dailyfoods'


class DailyFoodDetails(models.Model):
    class DaySection(models.TextChoices):
        BREAKFAST = ('BREAKFAST', 'Breakfast')
        LUNCH = ('LUNCH', 'Lunch')
        DINNER = ('DINNER', 'Dinner')
        SNACK = ('SNACK', 'Snack')

    detail_food = models.ForeignKey(DailyFood, on_delete=models.CASCADE, related_name='dailyfooddetails')
    aliment = models.ForeignKey(Aliment, null=True, on_delete=models.CASCADE)
    day_section = models.CharField(max_length=15, choices=DaySection.choices)
    weight_g = models.DecimalField(max_digits=8, decimal_places=2)
    # Valeur  énergétique (kcal/g)
    energy_value = models.DecimalField(max_digits=8, decimal_places=2)
    # Valeur énergétique totale (kcal)
    total_energy_value = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    protein =  models.DecimalField(max_digits=7, decimal_places=2)
    carboheidrates = models.DecimalField(max_digits=7, decimal_places=2)
    fat = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        db_table = 'dailyfooddetails'


class DailyExerciseDetails(models.Model):
    class ExerciseType(models.TextChoices):
        SEMI_SPRINT_XS = ('SEMI_SPRINT_XS', 'Semi-Sprint (XS)')
        SPRINT_S = ('SPRINT_S', 'Sprint (S)')
        OLYMPIQUE_M = ('OLYMPIQUE_M', 'Olympique (M)')
        TRIATHLON_L = ('TRIATHLON_L', 'Triathlon (L)')
        TRIATHLON_XL = ('TRIATHLON_XL', 'Triathlon (XL)')

    detail_food = models.ForeignKey(DailyFood, on_delete=models.CASCADE, related_name='dailyexercisedetails')
    exercise_type = models.CharField(max_length=255, choices=ExerciseType.choices)
    burned_calories = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    class Meta:
        db_table = 'dailyexercisedetails'

# =========================================================================

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
