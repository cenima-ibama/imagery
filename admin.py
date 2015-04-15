from django.contrib import admin

from .models import Scene, File

admin.site.register(Scene, admin.ModelAdmin)
admin.site.register(File, admin.ModelAdmin)