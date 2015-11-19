# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (SceneListView, SceneDetailView, cloud_rate_view, login_view,
    logout_view, request_scene_view, SceneRequestByUserListView,
    NotFoundSceneRequestListView, SceneListDelete)


urlpatterns = patterns('',
    url(r'^imagery/delete/(?P<pk>\d+)/$', login_required(SceneListDelete.as_view(), login_url='/login/'), name='delete_scene'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^$', SceneListView.as_view(), name='index'),
    url(r'^scene/(?P<slug>\w+)/$', SceneDetailView.as_view(), name='scene'),
    url(r'^cloud-rate/$', cloud_rate_view, name='cloud-rate'),
    url(r'^request-scene/$',
        login_required(request_scene_view, login_url='/login/'),
        name='request-scene'),
    url(r'^user-scene-request/$',
        login_required(SceneRequestByUserListView.as_view(), login_url='/login/'),
        name='user-scene-request'),
    url(r'^not-found-scene-request/$',
        NotFoundSceneRequestListView.as_view(),
        name='not-found-scene-request'),
)
