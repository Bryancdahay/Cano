from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from .models import Gender, Users
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import IntegrityError


@login_required
def home(request):
    return render(request, "gender/AddGender.html")


def AuthView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            messages.success(request, 'Logged in successfully!')
            return redirect('login')
        else:
            # This is where you print form errors to the console for debugging
            form = UserCreationForm()
            return render(request, "registration/signup.html", {"form": form})
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("login")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {"form": form})

@login_required
def add_gender(request):
    try:
        if request.method == 'POST':
            gender = request.POST.get('gender')

            if not gender:
                messages.error(request, 'Gender field is required.')
                return render(request, 'gender/AddGender.html')  # show error

            Gender.objects.create(gender=gender)
            messages.success(request, 'Gender added successfully!')
            return redirect('/gender/list')
        else:
            return render(request, 'gender/AddGender.html')
    except Exception as e:
        return HttpResponse(f'Error occurred during add gender: {e}')
    

@login_required
def gender_list(request):
    try:
        genders = Gender.objects.all()
        return render(request, 'gender/Genderlist.html', {'genders': genders})
    except Exception as e:
        return HttpResponse(f'Error occurred during loading genders: {e}')


@login_required
def edit_gender(request, genderId):
    try:
        if request.method == 'POST':
            genderobj = Gender.objects.get(pk=genderId)

            gender = request.POST.get('gender')
            genderobj.gender = gender
            genderobj.save()

            messages.success(request, 'Gender updated successfully!')
            data = {
                'gender': genderobj
            }

            return render(request, 'gender/EditGender.html', data)
        else:
            genderobj = Gender.objects.get(pk=genderId) 

            data = {
                'gender': genderobj
            }

        return render(request, 'gender/EditGender.html', data)
    except Exception as e:
        return HttpResponse(f'Error occured during edit gender: {e}')

@login_required
def delete_gender(request, genderId):
    try:
        if request.method == 'POST':
            genderobj = Gender.objects.get(pk=genderId)
            genderobj.delete()

            messages.success(request, 'Gender deleted successfully')
            return redirect('/gender/list')
        else:
            genderobj = Gender.objects.get(pk=genderId)

            data = {
                    'gender': genderobj
                }

            return render(request, 'gender/DeleteGender.html', data)    
    except Exception as e:
        return HttpResponse(f'Error occured during delete gender: {e}')

@login_required
def user_list(request):
    try:
        query = request.GET.get('q', '')
        users = Users.objects.all()

        if query:
            users = users.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query)
            )

        users = users.order_by('user_id')

        paginator = Paginator(users, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'users': page_obj,
            'query': query
        }

        return render(request, 'user/UserList.html', context)
    except Exception as e:
        return HttpResponse(f'Error occurred during user list: {e}')

@login_required
def add_user(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        gender_id = request.POST.get('gender')
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = {}

        # Required field validation
        if not full_name:
            errors['full_name'] = 'Full name is required.'
        if not gender_id:
            errors['gender'] = 'Please select a gender.'
        if not birth_date:
            errors['birth_date'] = 'Birth date is required.'
        if not address:
            errors['address'] = 'Address is required.'
        if not contact_number:
            errors['contact_number'] = 'Contact number is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not username:
            errors['username'] = 'Username is required.'
        if not password:
            errors['password'] = 'Password is required.'
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        # Gender check
        gender_obj = None
        if gender_id:
            try:
                gender_obj = Gender.objects.get(pk=gender_id)
            except Gender.DoesNotExist:
                errors['gender'] = 'Selected gender is invalid.'

        # Duplicate checks
        if email and Users.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists.'
        if username and Users.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'

        # Show form if errors
        if errors:
            return render(request, 'user/AddUser.html', {
                'errors': errors,
                'form_data': request.POST,
                'genders': Gender.objects.all()
            })

        # Try saving user, catch uniqueness error as backup
        try:
            Users.objects.create(
                full_name=full_name,
                gender=gender_obj,
                birth_date=birth_date,
                address=address,
                contact_number=contact_number,
                email=email,
                username=username,
                password=make_password(password)
            )
            messages.success(request, "User added successfully!")
            return redirect('user_list')

        except IntegrityError as e:
            errors['general'] = 'A user with that email or username already exists.'
            return render(request, 'user/AddUser.html', {
                'errors': errors,
                'form_data': request.POST,
                'genders': Gender.objects.all()
            })

    else:
        return render(request, 'user/AddUser.html', {'genders': Gender.objects.all()})
    
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(Users, user_id=user_id)
    genders = Gender.objects.all()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        gender_id = request.POST.get('gender')

        form_data = {
            'full_name': full_name,
            'username': username,
            'birth_date': birth_date,
            'address': address,
            'contact_number': contact_number,
            'email': email,
            'gender': gender_id,
        }
        errors = {}

        if not all([full_name, username, birth_date, address, contact_number, email, gender_id]):
            messages.error(request, "All fields are required.")
            return render(request, 'user/EditUser.html', {'user': user, 'genders': genders, 'form_data': form_data, 'errors': errors})

        # Check for duplicate username
        if Users.objects.exclude(user_id=user_id).filter(username=username).exists():
            errors['username'] = 'This username is already taken.'
        
        if Users.objects.exclude(user_id=user_id).filter(full_name=full_name).exists():
            errors['full_name'] = 'This Full Name is already taken.'

        # Check for duplicate email
        if Users.objects.exclude(user_id=user_id).filter(email=email).exists():
            errors['email'] = 'This email is already taken.'

        if errors:
            return render(request, 'user/EditUser.html', {
                'user': user,
                'genders': genders,
                'form_data': form_data,
                'errors': errors
            })

        gender = get_object_or_404(Gender, gender_id=gender_id)
        user.full_name = full_name
        user.username = username
        user.birth_date = birth_date
        user.address = address
        user.contact_number = contact_number
        user.email = email
        user.gender = gender
        user.save()

        messages.success(request, "User updated successfully.")
        return redirect('user_list')

    return render(request, 'user/EditUser.html', {'user': user, 'genders': genders})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(Users, user_id=user_id)


    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('user_list')

    return render(request, 'user/DeleteUser.html', {'user': user})



