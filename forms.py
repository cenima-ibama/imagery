# -*- coding: utf-8 -*-
from django import forms
from .models import PastSceneDownload

class SchedulingForm (forms.ModelForm):

    class Meta:
        model = PastSceneDownload
        fields = ['scene']
