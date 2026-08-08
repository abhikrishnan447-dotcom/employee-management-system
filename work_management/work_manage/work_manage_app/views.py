from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from . import models
from .models import Register



# Home Page
def index(request):
    return render(request, "index.html")


# Register emp
def register(request):

    if request.method == "POST":

        name = request.POST.get("name")
        photo = request.FILES.get("photo")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        age = request.POST.get("age")

        if models.Register.objects.filter(email=email).exists():
            return HttpResponse("<script>alert('Email already exists');window.location.href='{% url 'register' %}'</script>")
        else:
            user = models.Register.objects.create(name=name,email=email,phone=phone,password=password,photo=photo)
            user.save()
            return HttpResponse("<script>alert('Registration successfully please login');window.location.href='{% url 'login' %}'</script>")
        
    else:
        return render(request, 'register.html')

# Login emp
def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user=models.Register.objects.get(email=email)
            if user.password == password:
                request.session['email'] =email
                return redirect ('home')
            else:
                 return HttpResponse("<script>alert('Invalid password & Email....!!');window.location.href='/login/'</script>")
        except models.Register.DoesNotExist:
            return HttpResponse("<script>alert('Invalid user....!!');window.location.href='/login/'</script>")
        


    return render(request,'login.html')

# home
def home(request):

    if "user_id" not in request.session:
        return redirect("login")

    user = models.Register.objects.get(id=request.session["user_id"])

    return render(request, "home.html", {"user": user})



# Logout emp
def logout(request):
    request.session.flush()
    return HttpResponse("<script>alert('Logout Successfully....!!');window.location.href='/index/';</script>")

# dashboard
def dashboard(request):

    if "user_id" not in request.session:
        return redirect("login")

    user = models.Register.objects.get(id=request.session["user_id"])

    return render(request, "dashboard.html", {"user": user})



#admin credentials
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"


#admin login
def adminlogin(request):

    if request.method=="POST":

        email=request.POST.get("email")
        password=request.POST.get("password")

        if email==ADMIN_EMAIL and password==ADMIN_PASSWORD:

            request.session["admin"]=email

            return redirect("admin_dash")

        else:

            messages.error(request,"Invalid Admin Login")

    return render(request,"adminlogin.html")




def admin_dash(request):

    total_employees = Register.objects.count()

    context = {
        'total_employees': total_employees
    }

    return render(request, 'admin_dash.html', context)


def adminlogout(request):

    if "admin" in request.session:

        del request.session["admin"]

    return redirect("adminlogin")



