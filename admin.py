from django.contrib.gis import admin

from .models import Scene, Image, ScheduledDownload, SceneRequest


class SceneAdmin(admin.OSMGeoAdmin):

    list_display = ['name', 'path', 'row', 'sat', 'cloud_rate', 'date', 'status']
    list_filter = ['path', 'row', 'sat', 'status', 'date']
    search_fields = ['name']


class ImageAdmin(admin.ModelAdmin):

    list_display = ['name', 'type', 'scene']
    list_filter = ['type']
    search_fields = ['name', 'scene__name']


class ScheduledDownloadAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'creation_date', 'last_scene',
        'next_scene_name', 'has_new_scene']
    list_filter = ['path', 'row']


class SceneRequestAdmin(admin.ModelAdmin):

    list_display = ['scene_name', 'user', 'creation_date', 'status']
    list_filter = ['status', 'creation_date']
    search_fields = ['scene_name']


admin.site.register(Scene, SceneAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ScheduledDownload, ScheduledDownloadAdmin)
admin.site.register(SceneRequest, SceneRequestAdmin)