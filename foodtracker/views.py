from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

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
)
from .forms import (
    FoodForm,
    ImageForm, 
    EntraineurForm,
    EntraineurEditForm,
    TriathleteForm,
    TriathleteEditForm,
    AlimentForm,
    AlimentCategoryForm,
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
    return render(request, 'dashboard.html')


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
                    'user': user,
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
                'user': user,
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
                    'user': user,
                    'form': form,
                })
        else:
            form = TriathleteEditForm({
                'first_name': user.first_name,
                'last_name': user.last_name,
            })
            return render(request, 'athelete_edit.html', {
                'user': user,
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
    return render(request, 'manage_food.html', {
        'aliments': aliments,
    })


@login_required
def aliment_add_view(request):
    if request.method == 'POST':
        aliment_form = AlimentForm(request.POST, request.FILES)
        if aliment_form.is_valid():
            image = aliment_form.cleaned_data['image']
            category = aliment_form.cleaned_data['category']
            name = aliment_form.cleaned_data['name']
            weight_g = aliment_form.cleaned_data['weight_g']
            energy_value = aliment_form.cleaned_data['energy_value']
            # total_energy_value = aliment_form.cleaned_data['total_energy_value']
            # create aliment
            new_aliment = Aliment.objects.create(
                image=image,
                name=name,
                category=category,
                weight_g=weight_g,
                energy_value=energy_value,
                # total_energy_value=total_energy_value,
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
        return HttpResponseRedirect(reverse('index'))
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
                return HttpResponseRedirect(reverse('dashboard'))
            elif user.role == User.UserRoles.ENTRAINEUR:
                # user is entraineur
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                # user is traithlete
                return HttpResponseRedirect(reverse('dashboard'))
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
    return HttpResponseRedirect(reverse('index'))


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
        return HttpResponseRedirect(reverse('login'))

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
        return HttpResponseRedirect(reverse('login'))

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
