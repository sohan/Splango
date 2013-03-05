from django.conf.urls import *


urlpatterns = patterns(
    'splango.views',

    url(r'^confirm_human/$', 'confirm_human', name="splango-confirm-human"),

    url(r'^admin/$',
        'experiments_overview',
        name="splango-admin"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/$',
        'experiment_detail',
        name="splango-experiment-detail"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<report_id>\d+)/$',
        'experiment_report',
        name="splango-experiment-report"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<variant>[^/]+)/(?P<goal>[^/]+)/$',
        'experiment_log',
        name="splango-experiment-log"),
)
