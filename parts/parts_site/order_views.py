from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.db.models import F
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .constants import *

@login_required
def orders(request):
    return render(request, "orders.html")

@login_required
def orders_filters(request, filter):
    
    orders = Order.objects.all()

    for order in orders:
        items = order.item_set.all()
        total = 0
        for item in items:
            total = total + (item.unit_price * item.quantity)
        order.order_total = total
        order.save()

    match filter:
        case "ready":
            order_list = orders.filter(status__exact = OrderStatus.READY.value)
        case "new":
            order_list = orders.filter(status__exact = OrderStatus.NEW.value)
        case "placed":
            order_list = orders.filter(status__exact = OrderStatus.PLACED.value)
        case "received":
            order_list = orders.filter(status__exact = OrderStatus.RECEIVED.value)

    if order_list:
        order_list = order_list.order_by(F("vendor").desc())

    context = {"order_list": order_list,
               "current_filter": filter,
               }

    return render(request, "orders_filter.html", context)

@login_required
def order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    item_list = order.item_set.all()
    context = {"item_list": item_list,
               "order": order,
               "auto_add": auto_add_available(order.vendor)}
    return render(request, "order.html", context)

@login_required
def editorder(request, order_id):
    context ={}
 
    if request.method == "POST":
        form = OrderFormEdit(request.POST, instance=get_object_or_404(Order, pk=order_id))
        
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()

            return HttpResponseRedirect(reverse("orders"))
            
    else:
        form = OrderFormEdit(instance=get_object_or_404(Order, pk=order_id))
        
    context['form'] = form
    return render(request, "editobject.html", context)

@login_required
def delete(request, order_id = None, item_id = None):
    if item_id:
        item = get_object_or_404(Item, pk=item_id)
        item.delete(keep_parents=True)
        return HttpResponseRedirect(reverse("order",args=(order_id,)))
    elif order_id:
        order = get_object_or_404(Order, pk=order_id)
        order.delete(keep_parents=True)
        return HttpResponseRedirect(reverse("orders"))

@login_required
def newitem(request):
    context ={}
 
    if request.method == "POST":
        form = ItemForm(request.POST)
        
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            item = form.save(commit=False)

            orders = Order.objects.all()
            orders = orders.filter(status__exact = OrderStatus.NEW.value)
            orders = orders.filter(vendor__exact = item.vendor)

            if orders.count() > 0:
                order = orders.last()
            else:
                order = Order()
                order.vendor = item.vendor
                order.status = OrderStatus.NEW
                order.save()

            item.order = order
            item.requested_by = request.user

            item.save()
            form.save_m2m()

            return HttpResponseRedirect(reverse("orders"))
    else:
        form = ItemForm()
        
    context['form']= form
    vendors = Order.objects.filter(status=OrderStatus.NEW).values_list('vendor', flat=True).distinct()
    context['vendors'] = list(vendors)
    return render(request, "newobject.html", context)


@login_required
def edititem(request, order_id, item_id):
    order = get_object_or_404(Order, pk=order_id)
    item = get_object_or_404(Item, pk=item_id)
    
    if order.status != OrderStatus.NEW:
         return HttpResponseRedirect(reverse("order", args=(order_id,)))

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("order", args=(order_id,)))
    else:
        form = ItemForm(instance=item)
    
    context = {'form': form}
    vendors = Order.objects.filter(status=OrderStatus.NEW).values_list('vendor', flat=True).distinct()
    context['vendors'] = list(vendors)
    
    return render(request, "newobject.html", context)


#helper functions
def auto_add_available(vendor: str):
    vendors = ["andymark", "wcp", "mcmaster"]
    for v in vendors:
        if (vendor.lower() in v.lower()) or (v.lower() in vendor.lower()):
            return True
        
    return False