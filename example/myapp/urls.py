from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^sample/$', 'myapp.views.sample',
                           name='myapp_sample'), )
