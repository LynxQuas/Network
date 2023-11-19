from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from .models import User, Posts, Follow


def index(request):
    all_posts = Posts.objects.all().order_by("timestamp").reverse()
    p = Paginator(all_posts, 10)
    page = request.GET.get("page", 1)
    get_pages = p.page(page)

    return render(request, "network/index.html", { 
        'get_pages': get_pages
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# Create Post 

def create(request):
    if request.method == "POST":
        post_content = request.POST.get('post_content', "")
        if post_content == "":
           return render(request, "network/create.html", {
               "message": "Error: Please type something."
           })
        created_post = Posts(author=request.user, content=post_content)
        created_post.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/create.html")

def profile(request, user_id):
    user_profile = User.objects.get(pk=user_id)
    try:
        is_followed = user_profile.followers.filter(following=request.user.id).exists()
    except User.DoesNotExist:
        is_followed = False

    return render(request, "network/profile.html", { 
        "user_profile": user_profile,
        "user_posts": user_profile.user_posts.all().order_by('timestamp').reverse(),
        "is_followed": is_followed
    })  

def follow(request, user_id):
    current_user = request.user

    # get the person that user want to follow.
    user_to_follow = User.objects.get(pk=user_id)

    # add the current user to person's following list.
    followed = Follow(user=user_to_follow, following=current_user)
    followed.save()
    return HttpResponseRedirect(reverse('profile', args=(user_id,)))

def unfollow(request, user_id):
    current_user = request.user

    # get the person who user want to unfollow.
    user_to_unfollow = User.objects.get(pk=user_id)

    # get the person's following where user is following and delete.
    unfollowed = Follow.objects.get(user=user_to_unfollow, following=current_user)
    unfollowed.delete()
    return HttpResponseRedirect(reverse('profile', args=(user_id,)))

def following(request):
    # get the current user's following users.
    current_user_following = Follow.objects.filter(following=request.user)
    
    # retrive the current user's following query sets.
    current_user_following_posts = Posts.objects.filter(author__in=current_user_following.values("user"))

    p = Paginator(current_user_following_posts, 10)
    page = request.GET.get("page", 1)
    get_pages = p.page(page)
    
    print("Following's posts:", current_user_following_posts)
    return render(request, "network/following.html", { 
        "current_user_following_posts": get_pages
    })

def update_post_content(current_post, content):
    current_post.content = content
    current_post.save()
    return JsonResponse(current_post.serialize(), safe=False)

def toggle_like(request_data, current_post):
    liked_username = request_data["likes"]   
    liked_user = User.objects.get(username=liked_username)

    if liked_user != current_post.author:
        # Check if the user already likes the post
        if current_post.likes.filter(pk=liked_user.pk).exists():
            # User already likes the post, remove the like
            current_post.likes.remove(liked_user)
            message = "Like removed successfully"
        else:
            # User does not like the post, add the like
            current_post.likes.add(liked_user)
            message = "Like added successfully"
        return JsonResponse({"message": message, "post": current_post.serialize()}, safe=False)
    return JsonResponse({"error": "Cannot like your own post"}, status=400) 

def get_post(request, post_id):
    current_post = Posts.objects.get(pk=post_id)

    if request.method == "POST":
        try:
            request_data = json.loads(request.body)

            if 'content' in request_data:
                return update_post_content(current_post, request_data["content"])
            elif 'likes' in request_data:
                return toggle_like(request_data, current_post)
            else:
                return JsonResponse({"error": "Invalid request data"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse(current_post.serialize(), safe=False)

