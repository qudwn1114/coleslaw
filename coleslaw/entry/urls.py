from django.urls import path, include

from django.views.generic import TemplateView


app_name='entry'
urlpatterns = [
    path('test',  TemplateView.as_view(template_name="test.html")),
]