from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

# Remover CSRF só do admin
admin.site.csrf_exempt = True
# Register your models here.
