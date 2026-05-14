from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Bid
from .forms import ItemForm, BidForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone


# =========================
# HTML VIEWS
# =========================

def home(request):
    items = Item.objects.all()

    # 🔥 NEW: SEARCH
    query = request.GET.get('q')
    if query:
        items = items.filter(title__icontains=query)

    # 🔥 NEW: SORT
    sort = request.GET.get('sort')
    if sort == "low":
        items = items.order_by('starting_price')
    elif sort == "high":
        items = items.order_by('-starting_price')

    for item in items:
        item.is_expired = timezone.now() > item.end_time

        # 🔥 EXISTING WINNER LOGIC
        highest_bid = Bid.objects.filter(item=item).order_by('-amount').first()
        item.winner = highest_bid

    return render(request, 'index.html', {'items': items})


def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            return redirect('home')

    else:
        form = ItemForm()

    return render(request, 'add_item.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')


@login_required
def edit_item(request, id):
    item = get_object_or_404(Item, id=id)

    if request.user != item.created_by:
        return redirect('home')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()
            return redirect('item_detail', id=item.id)

    else:
        form = ItemForm(instance=item)

    return render(request, 'edit_item.html', {'form': form, 'item': item})


@login_required
def item_detail(request, id):
    item = get_object_or_404(Item, id=id)
    bids = Bid.objects.filter(item=item).order_by('-amount')
    highest_bid = bids.first()

    success = None

    # ❌ Prevent owner
    if request.user == item.created_by:
        return render(request, 'item_detail.html', {
            'item': item,
            'form': None,
            'highest_bid': highest_bid,
            'error': 'You cannot bid on your own item'
        })

    # ⏳ Auction ended
    if timezone.now() > item.end_time:
        return render(request, 'item_detail.html', {
            'item': item,
            'form': None,
            'highest_bid': highest_bid,
            'error': '⏳ Auction has ended'
        })

    if request.method == 'POST':
        form = BidForm(request.POST)

        if form.is_valid():
            bid = form.save(commit=False)

            # ❌ Lower bid check
            if highest_bid and bid.amount <= highest_bid.amount:
                return render(request, 'item_detail.html', {
                    'item': item,
                    'form': form,
                    'highest_bid': highest_bid,
                    'error': 'Bid must be higher than current highest bid'
                })

            if not highest_bid and bid.amount < item.starting_price:
                return render(request, 'item_detail.html', {
                    'item': item,
                    'form': form,
                    'highest_bid': highest_bid,
                    'error': 'Bid must be higher than starting price'
                })

            bid.user = request.user
            bid.item = item
            bid.save()

            success = "✅ Bid placed successfully!"
            highest_bid = bid
            form = BidForm()

    else:
        form = BidForm()

    return render(request, 'item_detail.html', {
        'item': item,
        'form': form,
        'highest_bid': highest_bid,
        'success': success
    })


# =========================
# 🔥 NEW: DASHBOARD VIEW
# =========================

@login_required


def dashboard(request):
    # All items created by the user
    my_items = Item.objects.filter(created_by=request.user)

    # Active items (not ended)
    active_items = [item for item in my_items if not item.is_ended()]

    # Sold items: ended and had at least one bid
    sold_items = [item for item in my_items if item.is_ended() and item.highest_bid()]

    # Items won by the user (highest bidder)
    won_items = []
    all_ended_items = Item.objects.filter(end_time__lte=timezone.now())
    for item in all_ended_items:
        highest_bid = item.highest_bid()
        if highest_bid and highest_bid.user == request.user:
            won_items.append(item)

    # Total money earned (from items sold by the user)
    total_earned = sum(
        item.highest_bid().amount
        for item in sold_items
        if item.highest_bid()
    )

    context = {
        'active_items': active_items,
        'sold_items': sold_items,
        'won_items': won_items,
        'total_earned': total_earned,
    }

    return render(request, 'dashboard.html', context)

# =========================
# 🔥 OPTIONAL: AJAX BID VIEW (ADVANCED)
# =========================

@login_required
def ajax_bid(request, id):
    item = get_object_or_404(Item, id=id)

    if request.method == "POST":
        amount = request.POST.get('amount')

        bids = Bid.objects.filter(item=item).order_by('-amount')
        highest_bid = bids.first()

        if highest_bid and float(amount) <= highest_bid.amount:
            return JsonResponse({'error': 'Bid too low'})

        if not highest_bid and float(amount) < item.starting_price:
            return JsonResponse({'error': 'Below starting price'})

        Bid.objects.create(
            user=request.user,
            item=item,
            amount=amount
        )

        return JsonResponse({'success': True})
