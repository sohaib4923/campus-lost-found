from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import Item, ClaimRequest


def home(request):
    items = Item.objects.all().order_by("-created_at")

    search = request.GET.get("search", "").strip()
    report_type = request.GET.get("type", "")

    if search:
        items = items.filter(
            Q(item_name__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search) |
            Q(category__icontains=search)
        )

    if report_type in ["LOST", "FOUND"]:
        items = items.filter(report_type=report_type)

    return render(
        request,
        "items/home.html",
        {
            "items": items,
            "search": search,
            "report_type": report_type,
        }
    )


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("home")

    return render(request, "items/register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "items/login.html")


def user_logout(request):
    logout(request)
    return redirect("home")


def add_item(request):
    if not request.user.is_authenticated:
        return redirect("login")

    report_type = request.GET.get("type", "LOST")

    if request.method == "POST":
        Item.objects.create(
            user=request.user,
            report_type=request.POST.get("report_type"),
            item_name=request.POST.get("item_name"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            location=request.POST.get("location"),
            item_date=request.POST.get("item_date"),
            image=request.FILES.get("image"),
        )

        return redirect("home")

    return render(
        request,
        "items/add_item.html",
        {"report_type": report_type}
    )

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    return render(
        request,
        "items/item_detail.html",
        {"item": item}
    )


def claim_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect("login")

    item = get_object_or_404(Item, id=item_id)

    # Apna item claim nahi kar sakte
    if item.user == request.user:
        messages.error(
            request,
            "You cannot claim your own reported item."
        )
        return redirect("item_detail", item_id=item.id)

    # Item already claimed/closed hai
    if item.status != "OPEN":
        messages.error(
            request,
            "This item is no longer available for claiming."
        )
        return redirect("item_detail", item_id=item.id)

    # Check duplicate claim
    existing_claim = ClaimRequest.objects.filter(
        item=item,
        claimant=request.user
    ).first()

    if existing_claim:
        messages.error(
            request,
            f"You have already claimed this item. "
            f"Current status: {existing_claim.get_status_display()}."
        )
        return redirect("item_detail", item_id=item.id)

    if request.method == "POST":
        message = request.POST.get("message", "").strip()

        if not message:
            messages.error(request, "Please enter a message.")
            return redirect("claim_item", item_id=item.id)

        ClaimRequest.objects.create(
            item=item,
            claimant=request.user,
            message=message
        )

        messages.success(
            request,
            "Claim request submitted successfully."
        )

        return redirect("dashboard")

    return render(
        request,
        "items/claim_item.html",
        {"item": item}
    )
    
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    my_items = Item.objects.filter(user=request.user).order_by("-created_at")
    my_claims = ClaimRequest.objects.filter(
        claimant=request.user
    ).select_related("item").order_by("-created_at")

    return render(
        request,
        "items/dashboard.html",
        {
            "my_items": my_items,
            "my_claims": my_claims,
        }
    )