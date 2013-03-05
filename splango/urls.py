from django.conf.urls import *


urlpatterns = patterns(
    'splango.views',

    url(r'^confirm_human/$', 'confirm_human', name="splango_confirm_human"),

    url(r'^admin/$',
        'experiments_overview',
        name="splango_admin"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/$',
        'experiment_detail',
        name="splango_experiment_detail"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<report_id>\d+)/$',
        'experiment_report',
        name="splango_experiment_report"),
    url(r'^admin/exp/(?P<exp_name>[^/]+)/(?P<variant>[^/]+)/(?P<goal>[^/]+)/$',
        'experiment_log',
        name="splango_experiment_log"),
)
