from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, CreateExerciseForm, CreateWorkoutForm
from .models import Workout, Exercise, Customer

def login(request):
    if request.method == "GET":
        form = LoginForm()
        context = { "logForm": form }
        return render(request, "login.html", context)
    else:   
        next = request.POST['next']
        form = LoginForm(request.POST)
        errors = form.errors
        print(errors)
        if not form.is_valid():
            for key, value in errors.items():
                # the message object will be held until the next time a page is rendered
                messages.error(request, value)
            return redirect("/login")
        else: 
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            if next:
                return redirect(next)
            return redirect("/home")

def register(request):
    if request.method == "GET":
        form = RegisterForm()
        context = { "regForm": form }
        return render(request, "register.html", context)
    else: 
        form = UserCreationForm(request.POST) 
        errors = form.errors
        # make this better, refer to add_exercise()
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/register")
        else: 
            new_user = form.save(commit=False)
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            email = request.POST["email"]
            if first_name:
                new_user.first_name = first_name  
            if last_name:
                new_user.last_name = last_name
            if email:
                new_user.email = email
            new_user.save()
            customer = Customer(user=new_user, username=new_user.username)
            customer.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return redirect("/home")

def not_found(request, path):
    return render(request, "404.html")

@login_required
def home(request):
    customer = request.user.customer
    workouts = customer.get_today_workout() 
    context = {'workouts': workouts} 
    return render(request, "home.html", context)

@login_required
def list_exercises(request):
    customer = request.user.customer
    exercises = customer.get_all_exercises()
    context = {'exercises': exercises}
    return render(request, "list_exercises.html", context)

@login_required
def list_workouts(request):
    customer = request.user.customer
    workouts = customer.get_all_workouts()
    context = {'workouts': workouts}
    return render(request, "list_workouts.html", context)


@login_required
def add_exercise(request):
    if request.method == "GET":
        form = CreateExerciseForm()
        context = { "form": form }
        return render(request, "add.html", context)
    else:   
        form = CreateExerciseForm(request.POST)
        new_exercise = form.extract()   
        if not new_exercise:
            errors = form.errors
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/add_exercise") 
        new_exercise.user = request.user
        new_exercise.save()
        return redirect("/list_exercises")

@login_required
def add_workout(request):
    customer = request.user.customer
    if request.method == "GET":
        exercises = customer.get_all_exercises()
        context = {'exercises': exercises}
        return render(request, "add.html", context)
    else:   
        selected_exercises = request.POST.getlist("exercise")
        selected_days = request.POST.getlist("day")
        form = CreateWorkoutForm(request.POST)
        new_workout = form.extract()
        if not new_workout:
            errors = form.errors
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/add_workout")
        new_workout.user = request.user
        # schedule
        new_schedule = new_workout.create_schedule()
        new_schedule.save()
        new_workout.schedule = new_schedule

        for k in selected_days:
            new_workout.set_schedule(k)
        
        new_workout.save()
        for id in selected_exercises:
            exercise = customer.get_exercise(id)
            new_workout.exercises.add(exercise)

        return redirect("/list_workouts")

@login_required
def schedule(request):
    customer = request.user.customer
    workouts = customer.get_today_workout()
    context = {'workouts': workouts }
    return render(request, 'schedule.html', context)

# make sure id is id of one of the user's workouts
@login_required
def completed_workout(request, id):
    customer = request.user.customer
    workout = customer.completed_workout(id)
    return redirect('/home')

@login_required
def view_workout(request, id):
    customer = request.user.customer
    workout = customer.get_workout(id)
    context = {'workout': workout }
    return render(request, 'show.html', context)

@login_required
def view_exercise(request, id):
    customer = request.user.customer
    exercise = customer.get_exercise(id)
    context = {'exercise': exercise }
    return render(request, 'show.html', context)

@login_required
def delete_workout(request, id):
    customer = request.user.customer
    customer.delete_workout(id)
    return redirect('/list_workouts')

@login_required
def delete_exercise(request, id):
    customer = request.user.customer
    customer.delete_exercise(id)
    return redirect('/list_exercises')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('/login')

@login_required
def help(request):
    return render(request, "help.html")

@login_required
def edit_exercise(request, id):
    customer = request.user.customer
    exercise = customer.get_exercise(id)
    
    if request.method == "GET":
        context = {'exercise': exercise }
        return render(request, "edit.html", context)
    else:   
        form = CreateExerciseForm(request.POST)
        new_exercise = form.extract()   
        if not new_exercise:
            errors = form.errors
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/edit_exercise/" + str(exercise.id)) 
        new_exercise.user = request.user
        new_exercise.id = exercise.id
        new_exercise.save()
        return redirect("/view_exercise/"+ str(exercise.id))

@login_required
def edit_workout(request, id):
    customer = request.user.customer
    workout = customer.get_workout(id)

    if request.method == "GET":
        all_exercises = customer.get_all_exercises()
        my_exercises = workout.get_exercises()
        context = {'workout': workout, 'all_exercises': all_exercises, 'my_exercises': my_exercises, 'schedule': workout.schedule}
        return render(request, "edit.html", context)
    else:   
        selected_exercises = request.POST.getlist("exercise")
        selected_days = request.POST.getlist("day")
        form = CreateWorkoutForm(request.POST)
        updated_workout = form.extract()
        if not updated_workout:
            errors = form.errors
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/edit_workout/" + str(workout.id))
        updated_workout.user = request.user
        # update schedule
        updated_schedule = updated_workout.create_schedule()
        updated_schedule.id = workout.schedule.id
        updated_workout.schedule = updated_schedule
        
        for k in selected_days:
            updated_workout.set_schedule(k)
        updated_workout.id = workout.id
        updated_workout.save()
        updated_workout.exercises.clear()
        for id in selected_exercises:
            exercise = customer.get_exercise(id)
            updated_workout.exercises.add(exercise)

        return redirect("/view_workout/" + str(workout.id))
