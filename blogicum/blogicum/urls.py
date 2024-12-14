from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView
handler403 = 'blog.exceptions.forbidden_access'
handler404 = 'blog.exceptions.page_not_found'
handler500 = 'blog.exceptions.server_error'

urlpatterns = [
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
]
