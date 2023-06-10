from django import forms
from django.utils import timezone
from django.db.models import Sum
import math
import builtins
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .utils import calculate_age
from .models import (
    User,
    Food,
    FoodCategory,
    FoodLog,
    Image,
    Weight,
    Entraineur,
    Triathlete,
    Aliment,
    AlimentCategory,
    GenderOptions,
    DailyFood,
    DailyFoodDetails,
    DailyExerciseDetails,
)
from .forms import (
    FoodForm,
    ImageForm, 
    EntraineurForm,
    EntraineurEditForm,
    TriathleteForm,
    TriathleteEditForm,
    AlimentForm,
    AlimentEditForm,
    AlimentCategoryForm,
    TriathleteCompleteSetupForm,
)


def index(request):
    '''
    The default route which lists all food items
    '''
    return food_list_view(request)


@login_required
def profile(request):
    pass


@login_required
def dashboard(request):
    if request.user.role == User.UserRoles.TRIATHLETE:
        try:
            daily_food = DailyFood.objects.get(date=timezone.localdate(), athlete_id=request.user.id)
            daily_food_details = DailyFoodDetails.objects.filter(detail_food__id=daily_food.id)
            breakfast = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.BREAKFAST)
            lunch = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.LUNCH)
            dinner = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.DINNER)
            snack = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.SNACK)
            exercises = DailyExerciseDetails.objects.filter(detail_food__id=daily_food.id)
            goal_count = request.user.profile_triathlete.depense_energetique_journaliere
            aliments_count = builtins.sum(builtins.map(lambda x: x.total_energy_value, daily_food_details))
            exercise_count = builtins.sum(builtins.map(lambda x: x.burned_calories, exercises))
            remaining_count = goal_count - aliments_count + exercise_count
            daily_water_goal = daily_food.daily_water_consumption
            water_consumption_count = daily_food.water_consumption_count
        except DailyFood.DoesNotExist:
            daily_food = DailyFood.objects.create(
                athlete=request.user,
                daily_water_consumption=request.user.profile_triathlete.daily_water_consumption,
            )
            breakfast = []
            lunch = []
            dinner = []
            snack = []
            exercises = []
            goal_count = request.user.profile_triathlete.depense_energetique_journaliere
            aliments_count = 0
            exercise_count = 0
            remaining_count = goal_count - aliments_count + exercise_count
            daily_water_goal = request.user.profile_triathlete.daily_water_consumption
            water_consumption_count = 0
        return render(request, 'athelete_dashboard.html', {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'snack': snack,
            'exercises': exercises,
            'goal_count': goal_count,
            'aliments_count': aliments_count,
            'exercise_count': exercise_count,
            'remaining_count': remaining_count,
            'daily_water_goal': daily_water_goal,
            'water_consumption_count': water_consumption_count,
        })
    elif request.user.role == User.UserRoles.ENTRAINEUR:
        triathlete = Triathlete.objects.all()
        return render(request, 'trainer_dashboard.html', {
            'triathlete': triathlete,
        })
    elif request.user.role == User.UserRoles.ADMIN:
        return redirect(reverse('triathletes'))
    return render(request, 'dashboard.html')


def get_daily_food_metadata(daily_food, calories_goal):
    consumed_calories = daily_food.dailyfooddetails.values('detail_food_id').annotate(calories_count=Sum('total_energy_value'))[0]['calories_count']
    exercices_count = daily_food.dailyexercisedetails.values('detail_food_id').annotate(calories_count=Sum('burned_calories'))[0]['calories_count']
    consumed_calories = consumed_calories - exercices_count
    return {
        "daily_food": daily_food,
        "id": daily_food.id,
        "date": daily_food.date,
        "comsumed_calories": consumed_calories,
        "calories_count": consumed_calories,
        "calories_percentage": builtins.round((consumed_calories/calories_goal) * 100, 0),
        "comsumed_water": daily_food.water_consumption_count,
        "water_goal": daily_food.daily_water_consumption,
        "water_percentage": builtins.round((daily_food.water_consumption_count/daily_food.daily_water_consumption)*100, 0),
    }


@login_required
def daily_food_history(request):
    calories_goal = request.user.profile_triathlete.depense_energetique_journaliere
    daily_foods = DailyFood.objects.filter(athlete_id=request.user.id, date__lt=timezone.localdate())
    daily_foods_meta_date = map(lambda x: get_daily_food_metadata(x, calories_goal), daily_foods)
    return render(request, 'daily_food_history.html', {
        'daily_foods_meta_date': daily_foods_meta_date,
        'calories_goal': calories_goal,
    })


@login_required
def athlete_daily_food_history(request, pk):
    athlete = User.objects.get(pk=pk)
    daily_foods = DailyFood.objects.filter(athlete_id=athlete.id, date__lt=timezone.localdate())
    calories_goal = athlete.profile_triathlete.depense_energetique_journaliere
    daily_foods_meta_date = map(lambda x: get_daily_food_metadata(x, calories_goal), daily_foods)
    return render(request, 'athelete_daily_food_history.html', {
        'daily_foods_meta_date': daily_foods_meta_date,
        'calories_goal': calories_goal,
        'athlete': athlete,
    })


@login_required
def athlete_daily_food_today_details(request, pk):
    athlete = User.objects.get(pk=pk)
    try:
        daily_food = DailyFood.objects.get(date=timezone.localdate(), athlete_id=athlete.id)
        daily_food_details = DailyFoodDetails.objects.filter(detail_food__id=daily_food.id)
        breakfast = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.BREAKFAST)
        lunch = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.LUNCH)
        dinner = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.DINNER)
        snack = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.SNACK)
        exercises = DailyExerciseDetails.objects.filter(detail_food__id=daily_food.id)
        goal_count = athlete.profile_triathlete.depense_energetique_journaliere
        aliments_count = builtins.sum(builtins.map(lambda x: x.total_energy_value, daily_food_details))
        exercise_count = builtins.sum(builtins.map(lambda x: x.burned_calories, exercises))
        remaining_count = goal_count - aliments_count + exercise_count
        daily_water_goal = daily_food.daily_water_consumption
        water_consumption_count = daily_food.water_consumption_count
    except DailyFood.DoesNotExist:
        daily_food = DailyFood.objects.create(
            athlete=athlete,
            daily_water_consumption=athlete.profile_triathlete.daily_water_consumption,
        )
        breakfast = []
        lunch = []
        dinner = []
        snack = []
        exercises = []
        goal_count = athlete.profile_triathlete.depense_energetique_journaliere
        aliments_count = 0
        exercise_count = 0
        remaining_count = goal_count - aliments_count + exercise_count
        daily_water_goal = athlete.profile_triathlete.daily_water_consumption
        water_consumption_count = 0
    return render(request, 'athlete_daily_food_history_details.html', {
        'athlete': athlete,
        'daily_food': daily_food,
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'snack': snack,
        'exercises': exercises,
        'goal_count': goal_count,
        'aliments_count': aliments_count,
        'exercise_count': exercise_count,
        'remaining_count': remaining_count,
        'daily_water_goal': daily_water_goal,
        'water_consumption_count': water_consumption_count,
    })


@login_required
def athlete_daily_food_history_details(request, pk, df):
    athlete = User.objects.get(pk=pk)
    daily_food = DailyFood.objects.get(pk=df)
    daily_food_details = DailyFoodDetails.objects.filter(detail_food__id=daily_food.id)
    breakfast = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.BREAKFAST)
    lunch = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.LUNCH)
    dinner = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.DINNER)
    snack = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.SNACK)
    exercises = DailyExerciseDetails.objects.filter(detail_food__id=daily_food.id)
    goal_count = athlete.profile_triathlete.depense_energetique_journaliere
    aliments_count = builtins.sum(builtins.map(lambda x: x.total_energy_value, daily_food_details))
    exercise_count = builtins.sum(builtins.map(lambda x: x.burned_calories, exercises))
    remaining_count = goal_count - aliments_count + exercise_count
    daily_water_goal = daily_food.daily_water_consumption
    water_consumption_count = daily_food.water_consumption_count
    return render(request, 'athlete_daily_food_history_details.html', {
        'athlete': athlete,
        'daily_food': daily_food,
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'snack': snack,
        'exercises': exercises,
        'goal_count': goal_count,
        'aliments_count': aliments_count,
        'exercise_count': exercise_count,
        'remaining_count': remaining_count,
        'daily_water_goal': daily_water_goal,
        'water_consumption_count': water_consumption_count,
    })


@login_required
def daily_food_history_details(request, pk):
    daily_food = DailyFood.objects.get(pk=pk)
    daily_food_details = DailyFoodDetails.objects.filter(detail_food__id=daily_food.id)
    breakfast = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.BREAKFAST)
    lunch = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.LUNCH)
    dinner = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.DINNER)
    snack = daily_food_details.filter(day_section=DailyFoodDetails.DaySection.SNACK)
    exercises = DailyExerciseDetails.objects.filter(detail_food__id=daily_food.id)
    goal_count = request.user.profile_triathlete.depense_energetique_journaliere
    aliments_count = builtins.sum(builtins.map(lambda x: x.total_energy_value, daily_food_details))
    exercise_count = builtins.sum(builtins.map(lambda x: x.burned_calories, exercises))
    remaining_count = goal_count - aliments_count + exercise_count
    daily_water_goal = daily_food.daily_water_consumption
    water_consumption_count = daily_food.water_consumption_count
    return render(request, 'daily_food_history_details.html', {
        'daily_food': daily_food,
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'snack': snack,
        'exercises': exercises,
        'goal_count': goal_count,
        'aliments_count': aliments_count,
        'exercise_count': exercise_count,
        'remaining_count': remaining_count,
        'daily_water_goal': daily_water_goal,
        'water_consumption_count': water_consumption_count,
    })


@login_required
def add_daily_food(request, section):
    aliments = Aliment.objects.all()
    return render(request, 'add_daily_food.html', {
        'aliments': aliments,
        'section': section,
    })


@login_required
def add_daily_food_config(request, section, aliment_id):
    aliment = Aliment.objects.get(pk=aliment_id)
    if request.method == 'POST':
        weight_g = float(request.POST['quantity'])
        total_energy_value = weight_g * float(aliment.energy_value)
        protein = weight_g * (float(aliment.protein) / float(aliment.weight_g))
        carboheidrates = weight_g * (float(aliment.carboheidrates) / float(aliment.weight_g))
        fat = weight_g * (float(aliment.fat) / float(aliment.weight_g))
        daily_food = DailyFood.objects.get(date=timezone.localdate(), athlete_id=request.user.id)
        DailyFoodDetails.objects.create(
            detail_food=daily_food,
            aliment=aliment,
            day_section=section,
            weight_g=weight_g,
            energy_value=aliment.energy_value,
            total_energy_value=total_energy_value,
            protein=protein,
            carboheidrates=carboheidrates, 
            fat=fat, 
        )
        return redirect(reverse('dashboard'))
    return render(request, 'add_daily_food_config.html', {
        'aliment': aliment,
        'day_section': section,
    })


@login_required
def delete_daily_food(request, pk):
    try:
        user = DailyFoodDetails.objects.get(pk=pk)
        if request.method == 'POST':
            deleted, _ = user.delete()
            if deleted:
                messages.success(request, f"L'aliment a été supprimé avec succès")
                return redirect(reverse('dashboard'))
        else:
            return render(request, 'delete_confirmation.html', {
                'title': "Supprimer l'aliment",
                'message': "Êtes-vous sûr de vouloir supprimer cet aliment?",
                'cancell_url': "dashboard"
            })
    except DailyFoodDetails.DoesNotExist:
        messages.error(request, "L'aliment n'existe pas")
        return redirect(reverse('entraineurs'))


@login_required
def delete_daily_exercise(request, pk):
    try:
        user = DailyExerciseDetails.objects.get(pk=pk)
        if request.method == 'POST':
            deleted, _ = user.delete()
            if deleted:
                messages.success(request, f"L'exercise a été supprimé avec succès")
                return redirect(reverse('dashboard'))
        else:
            return render(request, 'delete_confirmation.html', {
                'title': "Supprimer l'exercise",
                'message': "Êtes-vous sûr de vouloir supprimer cet exercise?",
                'cancell_url': "dashboard"
            })
    except DailyExerciseDetails.DoesNotExist:
        messages.error(request, "L'execise n'existe pas")
        return redirect(reverse('entraineurs'))


@login_required
def add_daily_exercise(request):
    return render(request, 'add_daily_exercise.html')


@login_required
def add_daily_exercise_cofig(request, exercise):
    if request.method == 'POST':
        burned_calories = float(request.POST['burned_calories'])
        daily_food = DailyFood.objects.get(date=timezone.localdate(), athlete_id=request.user.id)
        DailyExerciseDetails.objects.create(
            detail_food=daily_food,
            exercise_type=exercise,
            burned_calories=burned_calories,
        )
        return redirect(reverse('dashboard'))
    return render(request, 'add_daily_exercise_config.html', {
        'exercise': exercise,
    })


@login_required
def add_daily_water(request):
    if request.method == 'POST':
        daily_food = DailyFood.objects.get(date=timezone.localdate(), athlete_id=request.user.id)
        daily_food.water_consumption_count = float(daily_food.water_consumption_count) + float(request.POST['water_consumption_count'])
        daily_food.save()
        return redirect(reverse('dashboard'))
    return render(request, 'add_daily_water.html')


@login_required
def profile(request):
    if request.user.role == User.UserRoles.ADMIN:
        return render(request, 'admin_profile.html')
    elif request.user.role == User.UserRoles.TRIATHLETE:
        return render(request, 'athelete_profile.html', {
            "profile": request.user,
            "show_hello": True,
        })
    elif request.user.role == User.UserRoles.ENTRAINEUR:
        return render(request, 'trainer_profile.html', {
            "profile": request.user,
            "show_hello": True,
        })
    else:
        return HttpResponse('profile')


@login_required
def athlete_profile(request, pk):
    athelte = User.objects.get(pk=pk)
    return render(request, 'athelete_profile.html', {
        'profile': athelte,
        "show_hello": False,
    })


@login_required
def trainer_profile(request, pk):
    trainer = User.objects.get(pk=pk)
    return render(request, 'trainer_profile.html', {
        'profile': trainer,
        "show_hello": False,
    })


@login_required
def manage_trainers(request):
    entraineur = Entraineur.objects.all()
    return render(request, 'manage_trainers.html', {'entraineur': entraineur})


@login_required
def trainers_add_view(request):
    if request.method == 'POST':
        trainer_form = EntraineurForm(request.POST)
        if trainer_form.is_valid():
            first_name = trainer_form.cleaned_data['first_name']
            last_name = trainer_form.cleaned_data['last_name']
            username = f"{first_name}.{last_name}"
            email = trainer_form.cleaned_data['email']
            phone = trainer_form.cleaned_data['phone_number']
            passowrd = trainer_form.cleaned_data['password1']
            # create User
            new_user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                role=User.UserRoles.ENTRAINEUR,
            )
            new_user.set_password(passowrd)
            new_user.save()
            # create Entraineur
            Entraineur.objects.create(
                user=new_user,
                phone_number=phone
            )
            messages.success(request, f"L'entraîneur '{first_name} {last_name}' a été créé avec succès")
            return redirect(reverse('entraineurs'))
        else:
            return render(request, 'trainer_add.html', {
                'form': trainer_form,
            })
    return render(request, 'trainer_add.html', {
        'form': EntraineurForm()
    })


@login_required
def trainers_delete_view(request, pk):
    try:
        user = User.objects.get(pk=pk, role=User.UserRoles.ENTRAINEUR)
        if request.method == 'POST':
            deleted, _ = user.delete()
            if deleted:
                messages.success(request, f"L'entraîneur '{user.first_name} {user.last_name}' a été supprimé avec succès")
                return redirect(reverse('entraineurs'))
        else:
            return render(request, 'delete_confirmation.html', {
                'title': "Supprimer l'entraîneur",
                'message': "Êtes-vous sûr de vouloir supprimer cet entraîneur?",
                'cancell_url': "entraineurs"
            })
    except User.DoesNotExist:
        messages.error(request, "L'entraîneur n'existe pas")
        return redirect(reverse('entraineurs'))


@login_required
def trainers_edit_view(request, pk):
    try:
        user = User.objects.get(pk=pk, role=User.UserRoles.ENTRAINEUR)
        if request.method == 'POST':
            form = EntraineurEditForm(request.POST)
            if form.is_valid():
                user.first_name = form.cleaned_data.get('first_name', user.first_name)
                user.last_name = form.cleaned_data.get('last_name', user.last_name)
                user.email = form.cleaned_data.get('email', user.email)
                user.profile_entraineur.phone_number = form.cleaned_data.get('phone_number', user.profile_entraineur.phone_number)
                user.profile_entraineur.save()
                user.save()
                messages.success(request, "Les informations du entraineur ont été mises à jour avec succès")
                return redirect(reverse('entraineurs'))
            else:
                return render(request, 'trainer_edit.html', {
                    'trainer': user,
                    'form': form
                })
        else:
            form = EntraineurEditForm({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone_number': user.profile_entraineur.phone_number,
            })
            return render(request, 'trainer_edit.html', {
                'trainer': user,
                'form': form
            })
    except User.DoesNotExist:
        messages.error(request, "L'entraîneur n'existe pas")
        return redirect(reverse('entraineurs'))    


@login_required
def manage_athletes(request):
    triathlete = Triathlete.objects.all()
    return render(request, 'manage_athletes.html', {'triathlete': triathlete})


@login_required
def athelete_profile_setup(request):
    if request.method == 'POST':
        user = request.user
        form = TriathleteCompleteSetupForm(request.POST)
        if form.is_valid():
            age = calculate_age(form.cleaned_data['date_of_birth'])
            user.email = form.cleaned_data.get('email', None)
            user.profile_triathlete.gender = form.cleaned_data['gender']
            user.profile_triathlete.date_of_birth = form.cleaned_data['date_of_birth']
            user.profile_triathlete.age = age
            user.profile_triathlete.address = form.cleaned_data.get('address', None)
            user.profile_triathlete.phone_number = form.cleaned_data.get('phone_number', None)
            user.profile_triathlete.weight = form.cleaned_data['weight']
            user.profile_triathlete.height = form.cleaned_data['height']
            user.profile_triathlete.complete_profile_setup = True
            height_in_m = builtins.round(float(form.cleaned_data['height']) * math.pow(10, -2), 2)
            # Masse musculaire (%)
            if form.cleaned_data['gender'] == GenderOptions.MALE:
                user.profile_triathlete.masse_masculaire = builtins.round(0.407 * float(form.cleaned_data['weight']) + 0.267 * float(form.cleaned_data['height']) - 19.2, 2)
            else:
                user.profile_triathlete.masse_masculaire = builtins.round(0.252 * float(form.cleaned_data['weight']) + 0.473 * float(form.cleaned_data['height']) - 48.3, 2)
            # IMC (Kg/m^2)
            user.profile_triathlete.imc = builtins.round(float(form.cleaned_data['weight']) / math.pow(height_in_m, height_in_m), 2)
            # Masse Grasse (%)
            if form.cleaned_data['gender'] == GenderOptions.MALE:
                user.profile_triathlete.mass_grasse = builtins.round(1.2 * user.profile_triathlete.imc + 0.23 * age - 10.8 * 1 - 5.4, 2)
            else:
                user.profile_triathlete.mass_grasse = builtins.round(1.2 * user.profile_triathlete.imc + 0.23 * age - 10.8 * 0 - 5.4, 2)
            # Niveau d'ctivité physique
            user.profile_triathlete.niveau_activite = form.cleaned_data['niveau_activite']
            # Métabolisme de base(Kcal)
            if form.cleaned_data['gender'] == GenderOptions.MALE:
                user.profile_triathlete.metabolisme_de_base = builtins.round(13.707 * float(form.cleaned_data['weight']) + 492.3 * height_in_m - 6.673 * age + 77.607, 0)
            else:
                user.profile_triathlete.metabolisme_de_base = builtins.round(9.74 * float(form.cleaned_data['weight']) + 172.9 * height_in_m - 4.737 * age + 667.051, 0)
            # Dépense énergétique journalière(Kcal)
            if form.cleaned_data['niveau_activite'] == Triathlete.PhysicalActivityLevel.TWELVE_15H_WEEK:
                user.profile_triathlete.depense_energetique_journaliere = builtins.round(user.profile_triathlete.metabolisme_de_base * 1.8, 0)
            else:
                user.profile_triathlete.depense_energetique_journaliere = builtins.round(user.profile_triathlete.metabolisme_de_base * 2, 0)
            user.profile_triathlete.daily_water_consumption =  user.profile_triathlete.depense_energetique_journaliere
            user.profile_triathlete.save()
            user.save()
            messages.success(request, "Votre profil a été configuré avec succès")
            return redirect(reverse('dashboard'))
        else:
            return render(request, 'athlete_profile_setup.html', {
                'form': form,
            })
    else:
        return render(request, 'athlete_profile_setup.html', {
            'form': TriathleteCompleteSetupForm(),
        })


@login_required
def athlete_add_view(request):
    if request.method == 'POST':
        trainer_form = TriathleteForm(request.POST)
        if trainer_form.is_valid():
            first_name = trainer_form.cleaned_data['first_name']
            last_name = trainer_form.cleaned_data['last_name']
            username = f"{first_name}.{last_name}"
            passowrd = trainer_form.cleaned_data['password1']
            # create User
            new_user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=User.UserRoles.TRIATHLETE,
            )
            new_user.set_password(passowrd)
            new_user.save()
            # create Triathlete
            Triathlete.objects.create(user=new_user)
            messages.success(request, f"Le triathlete '{first_name} {last_name}' a été créé avec succès")
            return redirect(reverse('triathletes'))
        else:
            return render(request, 'athlete_add.html', {
                'form': trainer_form,
            })
    return render(request, 'athlete_add.html', {
        'form': TriathleteForm()
    })


@login_required
def athlete_edit_view(request, pk):
    try:
        user = User.objects.get(pk=pk, role=User.UserRoles.TRIATHLETE)
        if request.method == 'POST':
            form = TriathleteEditForm(request.POST)
            if form.is_valid():
                user.first_name = form.cleaned_data.get('first_name', user.first_name)
                user.last_name = form.cleaned_data.get('last_name', user.last_name)
                user.save()
                messages.success(request, "Les informations du triathlete ont été mises à jour avec succès")
                return redirect(reverse('triathletes'))
            else:
                return render(request, 'athelete_edit.html', {
                    'athlete': user,
                    'form': form,
                })
        else:
            form = TriathleteEditForm({
                'first_name': user.first_name,
                'last_name': user.last_name,
            })
            return render(request, 'athelete_edit.html', {
                'athlete': user,
                'form': form,
            })
    except User.DoesNotExist:
        messages.error(request, "Le triathlete n'existe pas")
        return redirect(reverse('triathletes'))


@login_required
def athlete_delete_view(request, pk):
    try:
        user = User.objects.get(pk=pk, role=User.UserRoles.TRIATHLETE)
        if request.method == 'POST':
            deleted, _ = user.delete()
            if deleted:
                messages.success(request, f"Le triathlète '{user.first_name} {user.last_name}' a été supprimé avec succès")
                return redirect(reverse('triathletes'))
        else:
            return render(request, 'delete_confirmation.html', {
                'title': "Supprimer Le triathlète",
                'message': "Êtes-vous sûr de vouloir supprimer cet triathlète?",
                'cancell_url': "triathletes"
            })
    except User.DoesNotExist:
        messages.error(request, "Le triathlète n'existe pas")
        return redirect(reverse('triathletes'))


@login_required
def manage_categories(request):
    categories = AlimentCategory.objects.all()
    return render(request, 'manage_categories.html', {
        'categories': categories,
    })


@login_required
def category_add_view(request):
    if request.method == 'POST':
        print('executed')
        category_form = AlimentCategoryForm(request.POST)
        if category_form.is_valid():
            name = category_form.cleaned_data['name']
            # create aliment category
            AlimentCategory.objects.create(name=name)
            messages.success(request, f"La catégorie '{name}' a été créé avec succès")
            return redirect(reverse('categories'))
        else:
            print('data is not valid', category_form.errors)
            return render(request, 'category_add.html', {
                'form': category_form,
            })
    return render(request, 'category_add.html', {
        'form': AlimentCategoryForm(),
    })


@login_required
def category_edit_view(request, pk):
    try:
        category = AlimentCategory.objects.get(pk=pk)
        if request.method == 'POST':
            form = AlimentCategoryForm(request.POST)
            if form.is_valid():
                category.name = form.cleaned_data.get('name', category.name)
                category.save()
                messages.success(request, "Les informations de la catégorie ont été mises à jour avec succès")
                return redirect(reverse('categories'))
            else:
                return render(request, 'category_edit.html', {
                    'category': category,
                    'form': form,
                })
        else:
            form = AlimentCategoryForm({'name': category.name})
            return render(request, 'category_edit.html', {
                'category': category,
                'form': form,
            })
    except AlimentCategory.DoesNotExist:
        messages.error(request, "La catégorie n'existe pas")
        return redirect(reverse('categories'))


@login_required
def category_delete_view(request, pk):
    try:
        category = AlimentCategory.objects.get(pk=pk)
        if request.method == 'POST':
            deleted, _ = category.delete()
            if deleted:
                messages.success(request, f"La catégorie '{category.name}' a été supprimé avec succès")
                return redirect(reverse('categories'))
        else:
            return render(request, 'delete_confirmation.html', {
                'title': "Supprimer La catégorie",
                'message': "Êtes-vous sûr de vouloir supprimer cette catégorie?",
                'cancell_url': "categories"
            })
    except AlimentCategory.DoesNotExist:
        messages.error(request, "La catégorie n'existe pas")
        return redirect(reverse('categories'))


@login_required
def manage_aliments(request):
    aliments = Aliment.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(aliments, 12)
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    return render(request, 'manage_food.html', {
        'aliments': aliments,
        'pages': pages
    })


@login_required
def aliment_detail_view(request, pk):
    try:
        aliment = Aliment.objects.get(pk=pk)
        return render(request, 'aliment_detail.html', {'food': aliment})
    except Aliment.DoesNotExist:
        messages.error(request, "L'aliment n'existe pas")
        return redirect(reverse('aliments'))


@login_required
def aliment_add_view(request):
    if request.method == 'POST':
        aliment_form = AlimentForm(request.POST, request.FILES)
        if aliment_form.is_valid():
            image = aliment_form.cleaned_data['image']
            name = aliment_form.cleaned_data['name']
            category = aliment_form.cleaned_data['category']
            weight_g = aliment_form.cleaned_data['weight_g']
            energy_value = aliment_form.cleaned_data['energy_value']
            protein = aliment_form.cleaned_data['protein']
            carboheidrates = aliment_form.cleaned_data['carboheidrates']
            fat = aliment_form.cleaned_data['fat']
            # create aliment
            new_aliment = Aliment.objects.create(
                image=image,
                name=name,
                category=category,
                weight_g=weight_g,
                energy_value=energy_value,
                protein=protein,
                carboheidrates=carboheidrates,
                fat=fat,
            )
            new_aliment.save()
            messages.success(request, f"L' aliment a été créé avec succès")
            return redirect(reverse('aliments'))
        else:
            return render(request, 'aliment_add.html', {
                'form': aliment_form,
            })
    return render(request, 'aliment_add.html', {
        'form': AlimentForm(),
    })


@login_required
def aliment_edit_view(request, pk):
    try:
        aliment = Aliment.objects.get(pk=pk)
        if request.method == 'POST':
            form = AlimentEditForm(request.POST)
            if form.is_valid():
                aliment.name = form.cleaned_data.get('name', aliment.name)
                aliment.category = form.cleaned_data.get('category', aliment.category)
                aliment.weight_g = form.cleaned_data.get('weight_g', aliment.weight_g)
                aliment.energy_value = form.cleaned_data.get('energy_value', aliment.energy_value)
                aliment.protein = form.cleaned_data.get('protein', aliment.protein)
                aliment.carboheidrates = form.cleaned_data.get('carboheidrates', aliment.carboheidrates)
                aliment.fat = form.cleaned_data.get('fat', aliment.fat)
                aliment.save()
                messages.success(request, "Les informations de l'aliment ont été mises à jour avec succès")
                return redirect(reverse('aliments'))
            else:
                return render(request, 'aliment_edit.html', {
                    'aliment': aliment,
                    'form': form,
                })
        else:
            form = AlimentEditForm({
                'name': aliment.name,
                'category': aliment.category,
                'weight_g': aliment.weight_g,
                'energy_value': aliment.energy_value,
                'total_energy_value': aliment.weight_g * aliment.energy_value,
                'protein': aliment.protein,
                'carboheidrates': aliment.carboheidrates,
                'fat': aliment.fat,
            })
            return render(request, 'aliment_edit.html', {
                'aliment': aliment,
                'form': form,
            })
    except Aliment.DoesNotExist:
        messages.error(request, "L'aliment n'existe pas")
        return redirect(reverse('aliments'))


@login_required
def aliment_edit_image_view(request, pk):
    try:
        aliment = Aliment.objects.get(pk=pk)
        if request.method == 'POST':
            aliment.image = request.FILES['image']
            aliment.save()
            messages.success(request, "L'image de l'aliment ont été mises à jour avec succès")
            return redirect(reverse('aliments'))
        else:
            return render(request, 'aliment_edit_image.html', {
                'aliment': aliment,
            })
    except Aliment.DoesNotExist:
        messages.error(request, "L'aliment n'existe pas")
        return redirect(reverse('aliments'))


@login_required
def aliment_delete_views(request, pk):
    try:
        aliment = Aliment.objects.get(pk=pk)
        if request.method == 'POST':
            deleted, _ = aliment.delete()
            if deleted:
                messages.success(request, f"L'aliment '{aliment.name}' a été supprimé avec succès")
                return redirect(reverse('aliments'))
        else:
            return render(request, 'delete_confirmation.html', {
                'title': "Supprimer L'aliment",
                'message': "Êtes-vous sûr de vouloir supprimer cet aliment?",
                'cancell_url': "aliments"
            })
    except Aliment.DoesNotExist:
        messages.error(request, "L'aliment n'existe pas")
        return redirect(reverse('aliments'))


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'register.html', {
                'message': 'Passwords must match.',
                'categories': FoodCategory.objects.all()
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'register.html', {
                'message': 'Username already taken.',
                'categories': FoodCategory.objects.all()
            })
        login(request, user)
        return redirect(reverse('index'))
    else:
        return render(request, 'register.html', {
            'categories': FoodCategory.objects.all()
        })


def login_view(request):
    if request.method == 'POST':
        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            if user.role == User.UserRoles.ADMIN:
                # user is admin
                return redirect(reverse('dashboard'))
            elif user.role == User.UserRoles.ENTRAINEUR:
                # user is entraineur
                return redirect(reverse('dashboard'))
            else:
                # user is traithlete
                if not user.profile_triathlete.complete_profile_setup:
                    return redirect(reverse('athlete-profile-setup'))
                return redirect(reverse('dashboard'))
        else:
            return render(request, 'login.html', {
                'message': "Nom d'utilisateur et / ou mot de passe incorrect.",
                'categories': FoodCategory.objects.all()
            })
    else:
        return render(request, 'login.html',  {
            'categories': FoodCategory.objects.all()
        })


def logout_view(request):
    logout(request)
    return redirect(reverse('index'))


def food_list_view(request):
    '''
    It renders a page that displays all food items
    Food items are paginated: 4 per page
    '''
    foods = Food.objects.all()

    for food in foods:
        food.image = food.get_images.first()

    # Show 4 food items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(foods, 4)
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    return render(request, 'index.html', {
        'categories': FoodCategory.objects.all(),
        'foods': foods,
        'pages': pages,
        'title': 'Food List'
    })


def food_details_view(request, food_id):
    '''
    It renders a page that displays the details of a selected food item
    '''
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    food = Food.objects.get(id=food_id)

    return render(request, 'food.html', {
        'categories': FoodCategory.objects.all(),
        'food': food,
        'images': food.get_images.all(),
    })


@login_required
def food_add_view(request):
    '''
    It allows the user to add a new food item
    '''
    ImageFormSet = forms.modelformset_factory(Image, form=ImageForm, extra=1)

    if request.method == 'POST':
        food_form = FoodForm(request.POST, request.FILES)
        image_form = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())

        if food_form.is_valid() and image_form.is_valid():
            new_food = food_form.save(commit=False)
            new_food.save()

            for food_form in image_form.cleaned_data:
                if food_form:
                    image = food_form['image']

                    new_image = Image(food=new_food, image=image)
                    new_image.save()

            return render(request, 'food_add.html', {
                'categories': FoodCategory.objects.all(),
                'food_form': FoodForm(),
                'image_form': ImageFormSet(queryset=Image.objects.none()),
                'success': True
            })

        else:
            return render(request, 'food_add.html', {
                'categories': FoodCategory.objects.all(),
                'food_form': FoodForm(),
                'image_form': ImageFormSet(queryset=Image.objects.none()),
            })

    else:
        return render(request, 'food_add.html', {
            'categories': FoodCategory.objects.all(),
            'food_form': FoodForm(),
            'image_form': ImageFormSet(queryset=Image.objects.none()),
        })


@login_required
def food_log_view(request):
    '''
    It allows the user to select food items and
    add them to their food log
    '''
    if request.method == 'POST':
        foods = Food.objects.all()

        # get the food item selected by the user
        food = request.POST['food_consumed']
        food_consumed = Food.objects.get(food_name=food)

        # get the currently logged in user
        user = request.user

        # add selected food to the food log
        food_log = FoodLog(user=user, food_consumed=food_consumed)
        food_log.save()

    else:  # GET method
        foods = Food.objects.all()

    # get the food log of the logged in user
    user_food_log = FoodLog.objects.filter(user=request.user)

    return render(request, 'food_log.html', {
        'categories': FoodCategory.objects.all(),
        'foods': foods,
        'user_food_log': user_food_log
    })


@login_required
def food_log_delete(request, food_id):
    '''
    It allows the user to delete food items from their food log
    '''
    # get the food log of the logged in user
    food_consumed = FoodLog.objects.filter(id=food_id)

    if request.method == 'POST':
        food_consumed.delete()
        return redirect('food_log')

    return render(request, 'food_log_delete.html', {
        'categories': FoodCategory.objects.all()
    })


@login_required
def weight_log_view(request):
    '''
    It allows the user to record their weight
    '''
    if request.method == 'POST':

        # get the values from the form
        weight = request.POST['weight']
        entry_date = request.POST['date']

        # get the currently logged in user
        user = request.user

        # add the data to the weight log
        weight_log = Weight(user=user, weight=weight, entry_date=entry_date)
        weight_log.save()

    # get the weight log of the logged in user
    user_weight_log = Weight.objects.filter(user=request.user)

    return render(request, 'user_profile.html', {
        'categories': FoodCategory.objects.all(),
        'user_weight_log': user_weight_log
    })


@login_required
def weight_log_delete(request, weight_id):
    '''
    It allows the user to delete a weight record from their weight log
    '''
    # get the weight log of the logged in user
    weight_recorded = Weight.objects.filter(id=weight_id)

    if request.method == 'POST':
        weight_recorded.delete()
        return redirect('weight_log')

    return render(request, 'weight_log_delete.html', {
        'categories': FoodCategory.objects.all()
    })


def categories_view(request):
    '''
    It renders a list of all food categories
    '''
    return render(request, 'categories.html', {
        'categories': FoodCategory.objects.all()
    })


def category_details_view(request, category_name):
    '''
    Clicking on the name of any category takes the user to a page that
    displays all of the foods in that category
    Food items are paginated: 4 per page
    '''
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    category = FoodCategory.objects.get(category_name=category_name)
    foods = Food.objects.filter(category=category)

    for food in foods:
        food.image = food.get_images.first()

    # Show 4 food items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(foods, 4)
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    return render(request, 'food_category.html', {
        'categories': FoodCategory.objects.all(),
        'foods': foods,
        'foods_count': foods.count(),
        'pages': pages,
        'title': category.category_name
    })
