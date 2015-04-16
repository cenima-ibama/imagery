from django.contrib import admin

from .models import Scene, Image

admin.site.register(Scene, admin.ModelAdmin)
admin.site.register(Image, admin.ModelAdmin)