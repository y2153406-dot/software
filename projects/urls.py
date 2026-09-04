from django.urls import path

from . import views


urlpatterns = [

    # PROJECT LIST

    path(
        "",
        views.project_list,
        name="project_list",
    ),


    # CREATE PROJECT

    path(
        "create/",
        views.project_create,
        name="project_create",
    ),


    # PROJECT DASHBOARD

    path(
        "project/<int:project_id>/dashboard/",
        views.project_dashboard,
        name="project_dashboard",
    ),

]