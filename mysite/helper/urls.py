from django.urls import path

from .views import users, building, user_buildings, user_resources, user_units, user_ships, user_account, island,\
    user_towns, islands, admin, resources_rank, units, ships, achievements, statistics

app_name = 'helper'


urlpatterns = [
    path('users/', users.get_users, name='users'),
    path('users/add_user', users.add_user, name='add_user'),

    path('users/buildings/<int:pk>', user_buildings.UserBuildingsView.as_view(), name='user_buildings'),
    path('users/buildings/compare_with_player', user_buildings.UserBuildingsView.compare_with_player, name='compare_with_player'),

    path('building/<int:pk>/', building.BuildingView.as_view(), name='building'),
    path('building/<int:instance_building_id>/update_building', building.update_building, name='update_building'),
    path('building/<int:instance_building_id>/start_develop_building', building.start_develop_building, name='start_develop_building'),
    path('building/<int:instance_building_id>/stop_develop_building', building.stop_develop_building, name='stop_develop_building'),

    path('users/resources/<int:pk>', user_resources.UserResourcesView.as_view(), name='user_resources'),
    path('users/resources/<int:user_id>/save_resources', user_resources.save_resources, name='save_resources'),
    path('users/resources/<int:user_id>/send_resources', user_resources.send_resources, name='send_resources'),
    path('users/resources/<int:user_id>/add_all', user_resources.add_all, name='add_all'),

    path('users/units/<int:pk>', user_units.UserUnitsView.as_view(), name='user_units'),
    path('users/units/<int:user_id>/save_units', user_units.save_units, name='save_units'),
    path('users/units/<int:user_id>/toggle_no_units', user_units.toggle_no_units, name='toggle_no_units'),

    path('users/ships/<int:pk>', user_ships.UserShipsView.as_view(), name='user_ships'),
    path('users/ships/<int:user_id>/save_ships', user_ships.save_ships, name='save_ships'),
    path('users/ships/<int:user_id>/toggle_no_ships', user_ships.toggle_no_ships, name='toggle_no_ships'),

    path('users/account/<int:pk>', user_account.UserAccountView.as_view(), name='user_account'),
    path('users/account/<int:user_id>/save_researches', user_account.save_researches, name='save_researches'),
    path('users/account/<int:user_id>/edit_user_info', user_account.edit_user_info, name='edit_user_info'),
    path('users/account/<int:user_id>/delete_user', user_account.delete_user, name='delete_user'),
    path('users/account/<int:user_id>/enable_towns', user_account.enable_towns, name='enable_towns'),

    path('users/island/<int:pk>/<int:user_id>', island.IslandView.as_view(), name='island'),
    path('users/island/edit_island', island.edit_island, name='edit_island'),
    path('users/island/add_town', island.add_town, name='add_town'),
    path('users/island/delete_island', island.delete_island, name='delete_island'),

    path('users/towns/<int:user_id>', user_towns.get_user_towns, name='user_towns'),
    path('users/towns/<int:user_id>/add_town', user_towns.add_town, name='add_town'),
    path('users/towns/<int:user_id>/update_town', user_towns.update_town, name='update_town'),
    path('users/towns/<int:user_id>/delete_town', user_towns.delete_town, name='delete_town'),

    path('users/islands/<int:user_id>', islands.get_islands, name='islands'),

    path('users/resources_rank/<int:user_id>', resources_rank.get_resources_rank, name='resources_rank'),

    path('admin', admin.admin_site, name='admin'),
    path('admin/web_scrap', admin.web_scrap, name='web_scrap'),
    path('admin/web_scrap_island', admin.web_scrap_island, name='web_scrap_island'),
    path('admin/web_scrap_town', admin.web_scrap_town, name='web_scrap_town'),
    path('admin/web_scrap_all_islands', admin.web_scrap_all_islands, name='web_scrap_all_islands'),
    path('admin/set_all_users_deleted', admin.set_all_users_deleted, name='set_all_users_deleted'),

    path('guide/units', units.get_units, name='units'),
    path('guide/ships', ships.get_ships, name='ships'),
    path('guide/achievements/<int:category_id>', achievements.get_achievements, name='achievements_category'),
    path('guide/achievements/level_up', achievements.level_up, name='achievements_level_up'),
    path('guide/achievements/confirm_progress', achievements.confirm_progress, name='confirm_progress'),

    path('guide/statistics/<int:user_id>', statistics.get_statistics, name='statistics'),


]


# TODO
#  budynki - design
#  surowce - kolory, hover, 1 000
#  robotnicy/poziom
#  paging/wyszukiwanie
#  zarządzanie id usera
