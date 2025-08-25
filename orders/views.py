from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from .models import Category, MenuItem, Order, OrderItem, Profile
from .forms import RegisterForm, ProfileForm, CheckoutForm

def _get_cart(session):
    return session.setdefault('cart', {})

def _cart_items(cart):
    ids = [int(k) for k in cart.keys()]
    items_map = {m.id: m for m in MenuItem.objects.filter(id__in=ids)}
    result = []
    total = 0
    for sid, qty in cart.items():
        mid = int(sid)
        item = items_map.get(mid)
        if not item: 
            continue
        line_total = item.price * qty
        total += line_total
        result.append({'item': item, 'qty': qty, 'line_total': line_total})
    return result, total

def home(request):
    categories = Category.objects.all().order_by('name')
    category_slug = request.GET.get('category')
    if category_slug:
        items = MenuItem.objects.filter(category__slug=category_slug, is_available=True).order_by('name')
    else:
        items = MenuItem.objects.filter(is_available=True).order_by('name')
    return render(request, 'home.html', {'categories': categories, 'items': items, 'active_category': category_slug})

def item_detail(request, slug):
    item = get_object_or_404(MenuItem, slug=slug, is_available=True)
    if request.method == 'POST':
        qty = max(1, int(request.POST.get('qty', '1')))
        cart = _get_cart(request.session)
        cart[str(item.id)] = cart.get(str(item.id), 0) + qty
        request.session.modified = True
        messages.success(request, f"Added {qty} × {item.name} to cart.")
        return redirect('cart')
    return render(request, 'item_detail.html', {'item': item})

def cart_view(request):
    cart = _get_cart(request.session)
    items, total = _cart_items(cart)
    if request.method == 'POST':
        if 'update' in request.POST:
            for key, val in request.POST.items():
                if key.startswith('qty_'):
                    mid = key.split('_',1)[1]
                    try:
                        q = int(val)
                    except ValueError:
                        q = 1
                    if q <= 0:
                        cart.pop(mid, None)
                    else:
                        cart[mid] = q
            request.session.modified = True
            messages.success(request, "Cart updated.")
            return redirect('cart')
        elif 'clear' in request.POST:
            request.session['cart'] = {}
            messages.info(request, "Cart cleared.")
            return redirect('cart')
    return render(request, 'cart.html', {'items': items, 'total': total})

@login_required
@transaction.atomic
def checkout(request):
    cart = _get_cart(request.session)
    items, total = _cart_items(cart)
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect('home')
    profile, _ = Profile.objects.get_or_create(user=request.user)
    initial = {'phone': profile.phone, 'address': profile.address}
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                status=Order.Status.PENDING,
                total_price=total,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
            )
            for row in items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=row['item'],
                    quantity=row['qty'],
                    price=row['item'].price
                )
            # Clear cart
            request.session['cart'] = {}
            # Send confirmation email
            try:
                send_mail(
                    subject=f"Order #{order.id} Confirmation",
                    message=f"Thank you for your order! Your order id is {order.id}. Status: {order.status}.",
                    from_email=None,
                    recipient_list=[request.user.email or 'test@example.com'],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, f"Order placed successfully! Your order id is {order.id}.")
            return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)
    return render(request, 'checkout.html', {'form': form, 'items': items, 'total': total})

@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            Profile.objects.create(user=user)
            messages.success(request, "Account created. Please log in.")
            return redirect('login_view')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form})