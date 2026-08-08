from django.urls import path
from .import views



urlpatterns = [


    #employee path
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),



    #admin path
    path("admin_dash/", views.admin_dash, name="admin_dash"),
    path("adminlogout/", views.adminlogout, name="adminlogout"),
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    # path('employees/', views.employee_list, name='employee_list'),




]
  