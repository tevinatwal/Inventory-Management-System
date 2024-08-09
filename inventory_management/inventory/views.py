from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, InventoryItemForm
from .models import InventoryItem, Category
from inventory_management.settings import LOW_QUANTITY
from django.contrib import messages
from django.db.models import Q, Sum, F
from decimal import Decimal
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string


class Index(TemplateView):
    template_name = 'inventory/index.html'

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.all().order_by('id')
        low_inventory_ids = InventoryItem.objects.filter(quantity__lte=LOW_QUANTITY).values_list('id', flat=True)
        categories = Category.objects.all()

        low_inventory = InventoryItem.objects.filter(quantity__lte=LOW_QUANTITY)
        if low_inventory.count() > 0:
            if low_inventory.count() > 1:
                messages.error(request, f'{low_inventory.count()} items have low inventory')
            else:
                messages.error(request, f'{low_inventory.count()} item has low inventory')

        total_cost = InventoryItem.objects.aggregate(total_cost=Sum(F('quantity') * F('unit_cost')))['total_cost']
        total_cost = round(total_cost or Decimal(0), 2)

        return render(request, 'inventory/dashboard.html', {
            'items': items, 
            'low_inventory_ids': low_inventory_ids,
            'categories': categories,
            'total_cost': total_cost or 0
        })
    
class GeneratePdf(View):
    def get(self, request):
        items = InventoryItem.objects.all().order_by('id')
        total_cost = InventoryItem.objects.aggregate(total_cost=Sum(F('quantity') * F('unit_cost')))['total_cost']
        total_cost = round(total_cost or Decimal(0), 2)

        html_string = render_to_string('inventory/pdf_template.html', {'items': items, 'total_cost': total_cost})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attatchment; filename="inventory.pdf"'
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
        return response

class LowItemsView(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.filter(quantity__lte=LOW_QUANTITY).order_by('id')
        low_inventory_ids = InventoryItem.objects.filter(quantity__lte=LOW_QUANTITY).values_list('id', flat=True)
        categories = Category.objects.all()

        return render(request, 'inventory/dashboard.html', {
            'items': items,
            'low_inventory_ids': low_inventory_ids,
            'categories': categories
        })
    
class SearchItemsView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('query', '')
        items = InventoryItem.objects.filter(name__icontains=query).order_by('id')
        low_inventory_ids = InventoryItem.objects.filter(quantity__lte=LOW_QUANTITY).values_list('id', flat=True)
        categories = Category.objects.all()

        return render(request, 'inventory/dashboard.html', {
            'items': items,
            'low_inventory_ids': low_inventory_ids,
            'categories': categories
        })
    
class FilterCategoryView(LoginRequiredMixin, View):
    def get(self, request):
        category_id = request.GET.get('category')
        items = InventoryItem.objects.filter(category_id=category_id).order_by('id')
        low_inventory_ids = InventoryItem.objects.filter(quantity__lte=LOW_QUANTITY).values_list('id', flat=True)
        categories = Category.objects.all()

        return render(request, 'inventory/dashboard.html',{
            'items': items,
            'low_inventory_ids': low_inventory_ids,
            'categories': categories
        })

class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )

            login(request, user)
            return redirect('index')
        
        return render(request, 'inventory/signup.html', {'form': form})
    
class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'
