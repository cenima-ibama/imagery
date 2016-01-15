# -*- coding: utf-8 -*-
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Scene


class SceneSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Scene
        id_field = False
        geo_field = 'geom'
        fields = ['name', 'status', 'date']
