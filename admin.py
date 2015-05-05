from django.contrib import admin

from .models import Scene, Image, ScheduledDownload

admin.site.register(Scene, admin.ModelAdmin)
admin.site.register(Image, admin.ModelAdmin)
admin.site.register(ScheduledDownload, admin.ModelAdmin)