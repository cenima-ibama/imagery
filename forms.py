# -*- coding: utf-8 -*-
from django import forms
from .models import SceneRequest


class SceneRequestForm (forms.ModelForm):

    class Meta:
        model = SceneRequest
        fields = ['scene_name']
