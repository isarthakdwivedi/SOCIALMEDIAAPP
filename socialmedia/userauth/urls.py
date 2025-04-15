from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from userauth import views

urlpatterns = [
    path('', views.home),
    path('signup/',views.signup, name = 'signup'),
    path('login/',views.login, name ='login' ),
    path('logout/', views.logout_view, name='logout'),
    path('upload', views.upload, name = 'upload'),
    path('like-post/<str:id>', views.likes, name = 'like-post'),
    path('#<str:id>', views.home_posts, name = 'home-posts'),
    path('explore/',views.explore),
    path('profile/<str:id_user>',views.profile),
    path('follow',views.follow,name='follow'),
    path('delete/<str:id>',views.delete,name='delete'),
    path('search_results/',views.search_results,name = 'search_results'),
    path('instagram/', views.instagram_media, name='instagram_media'),
    path('facebook/', views.facebook_feed, name='facebook_feed'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)