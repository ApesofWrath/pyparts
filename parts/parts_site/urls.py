from django.urls import path, include

from . import views, mfg_views, order_views, debug_views

urlpatterns = [
    path("", views.index, name="index"),
    path('accounts/', include('allauth.urls')),

    path("projects/", views.projects, name="projects"),
    path("newproject/", views.newproject, name="newproject"),

    path("projects/<int:project_id>/", views.project, name="project"),
    path("projects/<int:project_id>/newassembly/", views.newassembly, name="newassembly"),
    path("projects/<int:project_id>/delete/", views.delete, name="deleteproject"),
    path("projects/<int:project_id>/edit/", views.edit, name="editproject"),

    path("projects/<int:project_id>/assembly/<int:assembly_id>/", views.assembly_view, name="assembly"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/delete/", views.delete, name="deleteassembly"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/edit/", views.edit, name="editassembly"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/newsubassembly/", views.newassembly, name="newsubassembly"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/newpart/", views.newpart, name="newpart"),

    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/", views.part, name="part"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/revision/<int:revision_id>/", views.part, name="part_revision"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/delete/", views.delete, name="deletepart"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/edit/", views.edit, name="editpart"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/newrevision/", views.newrevision, name="newrevision"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/revision/<int:revision_id>/edit/", views.editrevision, name="editrevision"),
    path("projects/<int:project_id>/assembly/<int:assembly_id>/part/<int:part_id>/revision/<int:revision_id>/delete/", views.deleterevision, name="deleterevision"),

    path("mfg/", mfg_views.mfg, name="mfgsummary"),
    path("mfg/projects/<int:project_id>/", mfg_views.mfg_project, name="mfgproject"),
    path("mfg/projects/<int:project_id>/<filter>", mfg_views.mfg_filters, name="mfgfilters"),

    path("orders/", order_views.orders, name="orders"),
    path("orders/filters/<filter>", order_views.orders_filters, name="ordersfilters"),
    path("orders/<int:order_id>/", order_views.order, name="order"),
    path("orders/<int:order_id>/edit/", order_views.editorder, name="editorder"),
    path("orders/<int:order_id>/item/<int:item_id>/delete", order_views.delete, name="deleteitem"),
    path("orders/newitem/", order_views.newitem, name="newitem"),
    
    # Debug endpoints
    path("debug/upload/", debug_views.debug_upload_page, name="debug_upload"),
    path("debug/media/", debug_views.debug_media_page, name="debug_media"),
    path("debug/test-upload/", debug_views.test_file_upload, name="test_upload"),
    path("debug/media-access/", debug_views.test_media_access, name="test_media_access"),
    path("debug/media-file/<path:file_path>", debug_views.test_media_file, name="test_media_file"),
]