from django.conf.urls import url
from . import views
from frontend import auth, users, controllers, sensors, automation

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auth/login$', auth.loginAction, name='auth_login'),
    url(r'^auth/logout$', auth.logoutAction, name='auth_logout'),
    url(r'^auth/subscribe$', auth.subscribeAction, name='auth_subscribe'),
    url(r'^users/edit$', users.editAction, name='user_edit'),
    url(r'^controllers/?$', controllers.indexAction, name='controllers_index'),
    url(r'^controllers/add', controllers.addAction, name='controller_add'),
    url(r'^controllers/setdescr/(?P<key>[^/]+)', controllers.setDescriptionAction, name='controller_setdescr'),
    url(r'^controllers/viewlogs/(?P<key>[^/]+)', controllers.viewLogs, name='view_logs'),
    url(r'^controllers/deletelogs/(?P<key>[^/]+)', controllers.clearLogs, name='clear_logs'),
    url(r'^controllers/delete/(?P<key>[^/]+)', controllers.deleteAction, name='controller_delete'),
    url(r'^sensors/command/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)/(?P<instid>[^/]+)/(?P<sid>[^/]+)/(?P<cmd>.+)', sensors.commandAction, name='sensor_cmd'),
    url(r'^sensors/setdescr/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)/(?P<instid>[^/]+)/(?P<sid>[^/]+)', sensors.setdescrAction, name='sensor_setdescr'),
    url(r'^sensors/hideDevice/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)', sensors.hideDeviceAction, name='device_hide'),
    url(r'^sensors/unhideDevice/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)', sensors.unhideDeviceAction, name='device_unhide'),
    url(r'^sensors/hideSensor/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)/(?P<instid>[^/]+)/(?P<sid>[^/]+)', sensors.hideSensorAction, name='sensor_hide'),
    url(r'^sensors/unhideSensor/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)/(?P<instid>[^/]+)/(?P<sid>[^/]+)', sensors.unhideSensorAction, name='sensor_unhide'),
    url(r'^sensors/unhideSensor/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)', sensors.unhideAllSensorAction, name='sensor_all_unhide'),
    url(r'^sensors/graph/(?P<key>[^/]+)/(?P<zid>[^/]+)/(?P<devid>[^/]+)/(?P<instid>[^/]+)/(?P<sid>[^/]+)', sensors.showGraphAction, name='sensor_graph'),
    url(r'^sensors/(?P<key>[^/]+)', sensors.indexAction, name='sensors_list'),
    url(r'^automation/add/(?P<key>[^/]+)', automation.addAction, name='rule_add'),
    url(r'^automation/delete/(?P<key>[^/]+)/(?P<rid>.+)', automation.deleteAction, name='rule_delete'),
    url(r'^automation/edit/(?P<key>[^/]+)/(?P<rid>.+)', automation.editAction, name='rule_edit'),
    url(r'^automation/setdescr/(?P<key>[^/]+)/(?P<rid>.+)', automation.setDescrAction, name='rule_setdescr'),
    url(r'^automation/enable/(?P<key>[^/]+)/(?P<rid>.+)', automation.enableAction, name='rule_enable'),
    url(r'^automation/disable/(?P<key>[^/]+)/(?P<rid>.+)', automation.disableAction, name='rule_disable'),
    url(r'^automation/(?P<key>[^/]+)', automation.indexAction, name='automation'),
]

