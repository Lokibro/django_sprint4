from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts, name='category_posts'
    ),

    # Работа с профилем пользователя
    path('profile/<slug:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('edit_profile/', views.ProfileUpdateView.as_view(), name='edit_profile'),
]
