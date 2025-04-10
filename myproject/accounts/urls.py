from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
        next_page='/'  # <-- redirect after login to the main page
    ), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout')
]
