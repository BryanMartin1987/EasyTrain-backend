from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import PersonalaiKeys
from integrations.personalai import Personalai
from Crawlers import wrapper
import environ
env = environ.Env()
environ.Env.read_env()



def register_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            form.save()
            messages.success(request, 'Account created successfully') 
            return redirect('login')
    return render(request, 'register_user.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        authenticated_user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if authenticated_user is not None:
            print("Logged in successfully")
            login(request, authenticated_user)
            messages.success(request, 'Logged in successfully') 
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password') 
            return redirect('login')
        
    return render(request, 'login_user.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login_user', {"message": "You are logged out"})
    else:
        return redirect('login_user', {"message": "You are not logged in"})
            



def home(request):
    if request.user.is_authenticated:
        current_user = request.user

        key_available = PersonalaiKeys.objects.filter(user=current_user.id).exists()

        if request.method == 'POST':
            keyword = request.POST['keyword']
            ai_key = request.POST['key']
            
            if key_available == False:
                if Personalai(key=ai_key).validate_key():
                    ai_key_obj = PersonalaiKeys(key=ai_key, user=current_user.id)
                    ai_key_obj.save()
                    key_available = True
                else:
                    return render(request, 'home.html', {"error_message": "Invalid key"})
            else:
                ai_key = PersonalaiKeys.objects.get(user=current_user.id).key

            response = wrapper.get_urls(keyword)
            per_ai = Personalai(ai_key)
            response = per_ai.upload(response)
               
            return render(request, 'home.html', {"response": response, "key_available": key_available})

        return render(request, 'home.html', {"key_available": key_available})
    else:
        return redirect('login')

