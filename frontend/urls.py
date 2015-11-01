from django.conf.urls import url
from . import views
from frontend import auth, controllers, sensors

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auth/login$', auth.loginAction, name='auth_login'),
    url(r'^auth/logout$', auth.logoutAction, name='auth_logout'),
    url(r'^controllers/?$', controllers.indexAction, name='controllers_index'),
    url(r'^controllers/add', controllers.addAction, name='controller_add'),
    url(r'^controllers/setdescr/(?P<key>[^/]+)', controllers.setDescriptionAction, name='controller_setdescr'),
    url(r'^controllers/delete/(?P<key>[^/]+)', controllers.deleteAction, name='controller_delete'),
    url(r'^sensors/command/(?P<key>[^/]+)/(?P<sid>[^/]+)/(?P<cmd>.+)', sensors.commandAction, name='sensor_cmd'),
    url(r'^sensors/(?P<key>[^/]+)', sensors.indexAction, name='sensors_list'),
]
