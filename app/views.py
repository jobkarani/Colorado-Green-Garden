import datetime
from math import ceil
from multiprocessing import context
from multiprocessing.dummy import Value
from re import sub
from tokenize import Pointfloat
from django.contrib import messages
from django.db.models import Q
import requests

from .models import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import  HttpResponse, HttpResponseRedirect
from .email import send_welcome_email
from .forms import *
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from decouple import config

from .models import MpesaPayment
from django.views.decorators.csrf import csrf_exempt

import string
import random

from django.conf import settings
from django.core.mail import send_mail

from app import email


# auth
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
        return cart

def about(request):
    products = None
    cart = 0
    cart_items = 0
    cart_count = 0
    if request.user.is_authenticated and request.user.id:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart_count = 0

    ctx={
     'cart':cart,
     'cart_items':cart_items,
     'cart_count':cart_count,
     'products':products
    }
    return render(request, 'about.html',ctx)

def contact(request):
    cart = 0
    products = None
    cart_items = 0
    cart_count = 0
    if request.user.is_authenticated and request.user.id:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart_count = 0

    ctx={
     'cart':cart,
     'cart_items':cart_items,
     'cart_count':cart_count,
     'products':products
    }
    return render (request, 'contact.html',ctx)

def privacypolicy(request ):
    cart = 0
    products = None
    cart_items = 0
    cart_count = 0
    if request.user.is_authenticated and request.user.id:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart_count = 0

    ctx={
     'cart':cart,
     'cart_items':cart_items,
     'cart_count':cart_count,
     'products':products
    }
    return render (request,'privacy-policy.html',ctx)


@login_required(login_url="/accounts/login/")
def create_profile(request):
    current_user = request.user
    title = "Create Profile"
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = current_user
            profile.save()
        return HttpResponseRedirect('/')

    else:
        form = ProfileForm()
    return render(request, 'create_profile.html', {"form": form, "title": title})

@login_required(login_url="/accounts/login/")
def profile(request):
    cart = 0
    current_user = request.user
    profile = Profile.objects.filter(user_id=current_user.id).first()
    print(profile)
    product = Product.objects.filter(id=current_user.id).all()
    if request.user.is_authenticated and request.user.id:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_count = cart_items.count()

    ctx={
        'product':product,
        'products':products,
        'profile':profile,
        'cart':cart,
        'cart_items':cart_items,
        'cart_count':cart_count
    }

    return render(request, "profile.html", ctx)


@login_required(login_url="/accounts/login/")
def update_profile(request,id):
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user = user)
    form = UpdateProfileForm(instance=profile)
    if request.method == "POST":
            form = UpdateProfileForm(request.POST,request.FILES,instance=profile)
            if form.is_valid():

                profile = form.save(commit=False)
                profile.save()
                return redirect('profile')

    ctx = {"form":form}
    return render(request, 'update_prof.html', ctx)

# pages

def index(request, category_slug=None):
    categories = None
    products = None
    cart = 0
    cart_items = 0
    cart_count = 0

    if request.user.is_authenticated and request.user.id:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart_count = 0


    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)[0:8]
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)[0:8]
        product_count = products.count()
    context = {
        'products': products,
        'product_count':product_count,
        'cart':cart,
        'cart_items':cart_items,
        'cart_count':cart_count
    }
    return render(request, 'index.html', context)


def shop(request, category_slug=None,product_slug=None):
    categories = None
    products = None
    cart = 0
    cart_items = 0
    cart_count = 0
    if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart_count = 0

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products': paged_product,
        'product_count':product_count,
        'cart':cart,
        'cart_items':cart_items,
        'cart_count':cart_count
    }
    return render(request, 'shop.html', context)

def product_detail(request, category_slug, product_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product )
        products = Product.objects.all().filter(is_available=True)
        reviews = ReviewRating.objects.all().filter(product_id=single_product)
        review_count = reviews.count()


    except Exception as e:
        raise e

    cart = 0
    cart_items = 0
    cart_count = 0
    if request.user.is_authenticated and request.user.id:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
            cart_count = cart_items.count()
    else:
        cart_count = 0

    context = {
    'single_product': single_product,
    'in_cart':in_cart,
    'products':products,
    'reviews':reviews,
    'review_count':review_count,
    'cart':cart,
    'cart_items':cart_items,
    'cart_count':cart_count
    }
    return render(request, 'product-details.html',context)

@login_required(login_url="/accounts/login/")
def add_cart(request, product_id):
    if request.user.is_authenticated and request.user.id:
        product = Product.objects.get(id = product_id)
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value =request.POST[key]
        try:
            cart = Cart.objects.get(user=request.user,cart_id=_cart_id(request)) #get cart using cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
              user=request.user, cart_id = _cart_id(request)
            )
        cart.save()

    if request.user.is_authenticated and request.user.id:
        is_cart_item_exists = CartItem.objects.filter(user=request.user,product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(user=request.user,product=product, cart=cart)
            ex_var_list = []
            id = []
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
                user=request.user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()


    return redirect('cart')

@login_required(login_url="/accounts/login/")
def remove_cart(request, product_id,cart_item_id):
    if request.user.is_authenticated and request.user.id:
        cart = Cart.objects.get(user=request.user,cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()

            else:
                cart_item.delete()
        except:
            pass
    return redirect('cart')

@login_required(login_url="/accounts/login/")
def remove_cart_item(request, product_id, cart_item_id ):
    cart = Cart.objects.filter(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter( id= cart_item_id)
    cart_item.delete()

    return redirect('cart')

@login_required(login_url="/accounts/login/")
def delete_cart(request):
    if request.user.is_authenticated and request.user.id:
        cart = Cart.objects.get(user=request.user,cart_id=_cart_id(request))
        products = Product.objects.all().filter(is_available=True)
        cart.delete()
    ctx ={
        'products':products,
        'cart':cart,
    }
    return render(request, 'cart.html',ctx)

@login_required(login_url="/accounts/login/")
def cart(request, total=0, quantity=0, cart_items=None):
    if request.user.is_authenticated and request.user.id:
        try:
            sub_total = 0
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            products = Product.objects.all().filter(is_available=True)
                # cart_count = cart_items.count()

            for cart_item in cart_items:
                total += (cart_item.product.new_price * cart_item.quantity)
                quantity += cart_item.quantity
                sub_total = total
        except ObjectDoesNotExist:
            pass #just ignore
    else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            # cart_count = cart_items.count()

    ctx = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'sub_total': sub_total,
        'products':products,
        # 'cart_count':cart_count,
    }
    try:
        grand_total =0
        if request.user.is_authenticated and request.user.id:
            cart = Cart.objects.get(user=request.user,cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(user=request.user,cart=cart,is_active=True)
            products = Product.objects.all().filter(is_available=True)

            for cart_item in cart_items:
                grand_total += (cart_item.product.new_price *cart_item.quantity)


    except ObjectDoesNotExist:
        pass
    cart_count = cart_items.count()
    print(cart_items)
    ctx = {
        'grand_total':grand_total,
        'quantity':quantity,
        'cart_items':cart_items,
        'products':products,
        'cart_count':cart_count,
    }
    return render(request, 'cart.html', ctx)

def search(request):
    products = 0
    product_count = 0
    cart = Cart.objects.get(user=request.user,cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    cart_count = cart_items.count()
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            products= Product.objects.order_by('-name').filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            product_count = products.count()
        elif keyword != keyword :

            return HttpResponse('Ooops no products found with that keyword :(  Try another Keyword :)')

    ctx={
        'products':products,
        'product_count':product_count,
        'cart':cart,
        'cart_items':cart_items,
        'cart_count':cart_count
    }
    return render(request, 'shop.html', ctx)


@login_required(login_url="/accounts/login/")
def checkout(request, total=0, quantity=0, cart_items=None):
    if request.user.is_authenticated and request.user.id:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        products = Product.objects.all().filter(is_available=True)
        cart_count = cart_items.count()
        for cart_item in cart_items:
            total += (cart_item.product.new_price*cart_item.quantity)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_count = cart_items.count()
        for cart_item in cart_items:
            total += (cart_item.product.new_price*cart_item.quantity)

    ctx = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'cart_count':cart_count,
        'products':products,
    }
    return render(request, 'checkout.html',ctx)

@login_required(login_url="/accounts/login/")
def payments(request,total=0, quantity=0, cart_items=None):
    if request.user.is_authenticated and request.user.id:
        prof = Profile.objects.get(user = request.user)
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        products = Product.objects.all().filter(is_available=True)
        cart_count = cart_items.count()
        for cart_item in cart_items:
                total += (cart_item.product.new_price*cart_item.quantity)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_count = cart_items.count()
        for cart_item in cart_items:
            total += (cart_item.product.new_price*cart_item.quantity)

    ctx = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'cart_count':cart_count,
        'products':products,
        "user":prof.user.id
    }
    return render(request, 'payments.html', ctx)

# @login_required(login_url="/accounts/login/")
# def place_order(request,total=0, quantity=0,):
#     current_user = request.user

#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('shop')
#     for cart_item in cart_items:
#         total += (cart_item.product.new_price*cart_item.quantity)
#         quantity += cart_item.quantity
#         total = total

#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             # store all billing info
#             data = Order()
#             data.user = current_user
#             data.first_name = form.cleaned_data['first_name']
#             data.last_name = form.cleaned_data['last_name']
#             data.phone = form.cleaned_data['phone']
#             data.email = form.cleaned_data['email']
#             data.county = form.cleaned_data['county']
#             data.town = form.cleaned_data['town']
#             data.order_note = form.cleaned_data['order_note']
#             data.order_total = total
#             data.ip = request.META.get('REMOTE_ADDR')
#             data.save()

#             # generate order number
#             yr = int(datetime.date.today().strftime('%Y'))
#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))
#             d = datetime.date(yr,mt,dt)
#             current_date = d.strftime("%Y%m%d") #20210305
#             order_number = current_date + str(data.id)
#             data.order_number = order_number
#             data.save()
#             # return redirect('checkout')

#         order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
#         ctx = {
#             'order':order,
#             'cart_items':cart_items,
#             'total':total,
#             'cart':cart,
#         }
#         return render(request, 'confirm.html',ctx)

#     else:
#         return redirect('checkout')


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
    return redirect("/")

@csrf_exempt
@login_required(login_url="/accounts/login/")
def updateOrder(request):
    body=request.body.decode('utf-8')
    jsonBody = json.loads(body)
    user = User.objects.get(username=jsonBody["user"])
    cartItems = CartItem.objects.filter(user = user)
    letters = string.ascii_lowercase
    order = Order(
        user = user, order_id =''.join(random.choice(letters) for i in range(10)),
        paypalId = jsonBody["details"]["id"], status=jsonBody["details"]["status"],
        amount = jsonBody["details"]["purchase_units"][0]["amount"]["value"],
        currency = jsonBody["details"]["purchase_units"][0]["amount"]["currency_code"])
    order.save()
    for cartItem in cartItems:
        product = Product.objects.get(id = cartItem.product.id)
        orderItems = OrderItem(
            user = user, product = product, order = order,
            quantity = cartItem.quantity)
        orderItems.save()
    sendEmails("NEW ORDER", "There is a new order, kindly check admin",
        [settings.EMAIL_HOST_USER])

    sendEmails("ORDER ACCEPTED", "Dear {} We have received your order and we are working diligently to deliver your product!",
        [request.user.email])


def sendEmails(subject, message, recipients):
    email_from = settings.EMAIL_HOST_USER
    send_mail( subject, message, email_from, recipients)


def subscribeToNewsLetter(request):
    if request.method == "GET":
        query = request.GET.get('email')
        if query == '':
            print("Empty query")
        else:
            NewsLetterRecipients(email = query)
    return redirect("/")
