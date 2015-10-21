# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import SceneListView, SceneDetailView, cloud_rate_view, login_view
from .views import logout_view, scene_request_view


urlpatterns = patterns('',
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^$', SceneListView.as_view(), name='index'),
    url(r'^scene/(?P<slug>\w+)/$', SceneDetailView.as_view(), name='scene'),
    url(r'^cloud-rate/$', cloud_rate_view, name='cloud-rate'),
    url(r'^scene-request/$', login_required(scene_request_view,
        login_url='/login/'), name='scene-request')
)
