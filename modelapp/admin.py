from django.contrib import admin
from .models import Model

class ModelAdmin(admin.ModelAdmin):
    list_display = ['question']

class ModelAdminAnswer(admin.ModelAdmin):
    list_display = ['question', 'answer']

admin.site.register(Model, ModelAdmin)
admin.site.register(Model, ModelAdminAnswer)