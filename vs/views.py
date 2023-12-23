import json
import datetime

from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import *
# Create your views here.
def vs(request):
    data = cartDate(request)
    cartItems = data['cartItems']
    products = Product.objects.all()

    context = {'products': products, "cartItems": cartItems}
    return render(request, 'vs/VS.html', context)

def cart(request):
    data = cartDate(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    
    context = {'items':items,'order':order, "cartItems": cartItems}
    return render(request, 'vs/Cart.html', context)

def checkout(request):
    data = cartDate(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items,'order':order, "cartItems": cartItems}
    return render(request, 'vs/Checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('ProductId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,
                                                 complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order,
                                                         product=product )


    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)    

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:

        ShippingAddress.objects.create(
            customer = customer,
            order = order,

            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode']
        )
    return JsonResponse('Payment complete!', safe=False)