# -*- coding: utf-8 -*-
from django import forms
from .models import SceneRequest


class SceneRequestForm(forms.ModelForm):

    class Meta:
        model = SceneRequest
        fields = ['scene_name']


class SceneFilterForm(forms.Form):

    name = forms.CharField()
    path = forms.CharField()
    row = forms.CharField()
    status = forms.CharField()
    sat = forms.CharField()
    start = forms.DateField()
    end = forms.DateField()
    max_cloud = forms.FloatField()