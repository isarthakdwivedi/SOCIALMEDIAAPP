import requests
import os
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from .models import LikePost, Profile,Post, Followers
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate , login as django_login
from dotenv import load_dotenv
load_dotenv()

# Create your views here.


from django.contrib import messages


INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")




def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('emailid')
        password = request.POST.get('pwd')
        full_name = request.POST.get('fnm')  # Optional

        print("DEBUG username:", username)
        print("DEBUG email:", email)

        if not username or not email or not password:
            return render(request, 'signup.html', {'invalid': 'All fields are required.'})

        # Check for duplicates
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'invalid': 'Username already taken.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'invalid': 'Email already registered.'})

        try:
            my_user = User.objects.create_user(username=username, email=email, password=password)
            my_user.first_name = full_name
            my_user.save()

            # Profile creation
            Profile.objects.create(user=my_user, id_user=my_user.id)

            # Log the user in after successful signup
            auth_login(request, my_user)

            # Redirect with a success message
            messages.success(request, 'Your account has been created successfully!')
            return redirect('/')

        except IntegrityError:
            return render(request, 'signup.html', {'invalid': 'Something went wrong. Try again.'})

    return render(request, 'signup.html')

def login(request):  
    if request.method == 'POST':
        username = request.POST.get('fnm')  # Assuming 'fnm' is for username
        password = request.POST.get('pwd')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If authentication is successful, log the user in
            django_login(request, user)
            return redirect('/')

        # If authentication fails, show the invalid credentials message
        invalid = "Invalid Credentials"
        return render(request, 'login.html', {'invalid': invalid})

    return render(request, 'login.html')

@login_required(login_url='/login')
def logout_view(request):
    django_logout(request)
    return redirect('/login')


@login_required(login_url = '/login')
def upload(request):
    if request.method == 'POST':
            user = request.user.username
            image = request.FILES.get('image_upload')
            caption = request.POST['caption']
            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()
            return redirect('/')
    else:
        return redirect('/')

@login_required(login_url = '/login')
def home(request):
    following_users = Followers.objects.filter(follower = request.user.username).values_list('user',flat=True)
    post  = Post.objects.filter(Q(user = request.user.username) | Q(user__in=following_users)).order_by('-created_at')
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'id_user': request.user.id})

    context = {
        'post': post,
        'profile' : profile

    }
    return render(request, 'main.html',context)


@login_required(login_url = '/login')
def likes(request,id ):
    if request.method =='GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)
        like_filter = LikePost.objects.filter(post_id=id, username=username).first()

        if like_filter == None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1

        post.save()

        return redirect('/#'+id)    
    

def home_posts(request, id):
    post = Post.objects.get(id = id)
    profile = Profile.objects.get(user = request.user)
    context = {
        'post':post,
        'profile':profile
    }  

    return render(request, 'main.html', context)  


def explore(request):
    post  = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user = request.user)
    context = {
        'post' : post,
        'profile' : profile
        
    }

    return render(request, 'explore.html',context)

def profile(request, id_user):
    # Get user and profile data
    try:
        user_object = User.objects.get(username=id_user)
        user_profile = Profile.objects.get(user=user_object)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

    # Logged-in user's profile
    profile = Profile.objects.get(user=request.user)

    # Get posts by the user
    user_post = Post.objects.filter(user=user_object).order_by('-created_at')
    user_post_length = user_post.count()

    # Follow/Unfollow logic
    follower = request.user.username
    user = id_user
    follow_unfollow = 'Unfollow' if Followers.objects.filter(follower=follower, user=user).exists() else 'Follow'

    # Followers and Following count
    user_followers = Followers.objects.filter(user=user).count()
    user_following = Followers.objects.filter(follower=user).count()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_post': user_post,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following
    }

    # Profile update logic
    if request.method == 'POST':
        image = request.FILES.get('image', user_profile.profileimg)
        bio = request.POST.get('bio', user_profile.bio)
        location = request.POST.get('location', user_profile.location)

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect('/profile/' + id_user)

    return render(request, 'profile.html', context)


@login_required(login_url = '/login')
def follow(request):
    
    if request.method == 'POST':
        follower= request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower = follower, user = user).first():
            delete_follower = Followers.objects.filter(follower = follower, user = user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = Followers.objects.create(follower = follower, user = user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
        
@login_required(login_url = '/login')        
def delete(request,id):
    post = Post.objects.get(id = id)
    post.delete()
    return redirect('/profile/'+request.user.username)


@login_required(login_url = '/login')
def search_results(request):
        query = request.GET.get('q')
        users = User.objects.filter(Q(username__icontains=query))
        posts = Post.objects.filter(caption__icontains=query)
        context = {

            'query' : query,
            'users' : users,
            'posts' : posts
        }
        return render(request,'search_user.html',context)


def instagram_media(request):
    url = f'https://graph.facebook.com/v19.0/{IG_USER_ID}/media'
    params = {
        'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp,permalink',
        'access_token': INSTAGRAM_TOKEN
    }
    response = requests.get(url, params=params)
    media_data = response.json().get('data', [])

    return render(request, 'instagram_feed.html', {'media': media_data})


def facebook_feed(request):
    url = f'https://graph.facebook.com/v19.0/{FB_PAGE_ID}/posts'
    params = {
        'fields': 'message,full_picture,created_time,permalink_url',
        'access_token': INSTAGRAM_TOKEN
    }
    response = requests.get(url, params=params)
    posts = response.json().get('data', [])
    
    return render(request, 'facebook_feed.html', {'posts': posts})
