from django.contrib import admin
from django.urls import path
from .views import Index, SignUpView, Dashboard, AddItem, EditItem, DeleteItem, LowItemsView, SearchItemsView, FilterCategoryView, GeneratePdf
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('add-item/', AddItem.as_view(), name='add-item'),
    path('edit-item/<int:pk>', EditItem.as_view(), name='edit-item'),
    path('delete-item/<int:pk>', DeleteItem.as_view(), name='delete-item'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='inventory/logout.html'), name='logout'), 
    path('low-items/', LowItemsView.as_view(), name='low-items'),
    path('search-items/', SearchItemsView.as_view(), name='search-items'),
    path('filter-category/', FilterCategoryView.as_view(), name='filter-category'),
    path('generate-pdf/', GeneratePdf.as_view(), name='generate-pdf'),
]