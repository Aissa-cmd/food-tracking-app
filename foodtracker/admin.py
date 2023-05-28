from django.contrib import admin

from .models import (
    User,
    Food,
    FoodCategory,
    FoodLog,
    Image,
    Weight,
    Triathlete,
    Entraineur,
)

admin.site.register(User)
admin.site.register(Triathlete)
admin.site.register(Entraineur)
admin.site.register(Food)
admin.site.register(FoodCategory)
admin.site.register(FoodLog)
admin.site.register(Image)
admin.site.register(Weight)
