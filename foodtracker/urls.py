from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('profile/weight', views.weight_log_view, name='weight_log'),
    path('profile/weight/delete/<int:weight_id>', views.weight_log_delete, name='weight_log_delete'),

    path('profile', views.profile, name='profile'),

    path('food/list', views.food_list_view, name='food_list'),
    path('food/add', views.food_add_view, name='food_add'),
    path('food/foodlog', views.food_log_view, name='food_log'),
    path('food/foodlog/delete/<int:food_id>', views.food_log_delete, name='food_log_delete'),
    path('food/<str:food_id>', views.food_details_view, name='food_details'),

    # path('categories', views.categories_view, name='categories_view'),
    # path('categories/<str:category_name>', views.category_details_view, name='category_details_view'),

    path('entraineurs', views.manage_trainers, name='entraineurs'),
    path('entraineurs/add', views.trainers_add_view, name='trainer_add'),
    path('entraineurs/edit/<int:pk>', views.trainers_edit_view, name='trainer_edit'),
    path('entraineurs/delete/<int:pk>', views.trainers_delete_view, name='trainer_delete'),

    path('triathletes', views.manage_athletes, name='triathletes'),
    path('triathletes/profile-setup', views.athelete_profile_setup, name='athlete-profile-setup'),
    path('triathletes/add', views.athlete_add_view, name='athlete_add'),
    path('triathletes/edit/<int:pk>', views.athlete_edit_view, name="athlete_edit"),
    path('triathletes/delete/<int:pk>', views.athlete_delete_view, name="athlete_delete"),

    path('categories', views.manage_categories, name='categories'),
    path('categories/add', views.category_add_view, name='category_add'),
    path('categories/edit/<int:pk>', views.category_edit_view, name='category_edit'),
    path('categories/delete/<int:pk>', views.category_delete_view, name='category_delete'),

    path('aliments', views.manage_aliments, name='aliments'),
    path('aliments/<int:pk>', views.aliment_detail_view, name='aliment_detail'),
    path('aliments/add', views.aliment_add_view, name='aliement_add'),
    path('aliments/edit/<int:pk>', views.aliment_edit_view, name='aliment_edit'),
    path('aliments/delete/<int:pk>', views.aliment_delete_views, name='aliment_delete'),

    path('add-daily-food/<str:section>', views.add_daily_food, name='add_daily_food'),
    path('add-daily-food/<str:section>/<int:aliment_id>/', views.add_daily_food_config, name='add_daily_food_config'),
    path('delete-daily-food/<int:pk>', views.delete_daily_food, name='delete_daily_food'),
]
