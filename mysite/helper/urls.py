from django.urls import path

from .views import users, user_buildings, user_resources, user_army, user_account, island,\
    user_towns, islands, resources_rank, units, ships, user_achievements, login, register, logout,\
    key_manager, settings, sawmill, achievements
from mysite.helper.views.panel import panel
from mysite.helper.views.statistics import statistics_alliances, statistics_players, statistics_scores, statistics_achievements

app_name = 'helper'


urlpatterns = [
    path('helper/login/', login.get_login, name='login'),
    path('login/', login.get_login, name='login'),
    path('helper/register/', register.get_register, name='register'),
    path('register/', register.get_register, name='register'),
    path('logout/', logout.get_logout, name='logout'),

    path('users/', users.get_users, name='users'),
    path('users/add_user', users.add_user, name='add_user'),


    path('users/buildings/<int:user_id>', user_buildings.get_user_buildings, name='user_buildings'),
    path('users/update_building/', user_buildings.update_building, name='update_building'),

    path('users/resources/<int:user_id>', user_resources.get_user_resources, name='user_resources'),
    path('users/resources/<int:user_id>/save_resources', user_resources.save_resources, name='save_resources'),
    path('users/resources/<int:user_id>/send_resources', user_resources.send_resources, name='send_resources'),
    path('users/resources/<int:user_id>/add_all', user_resources.add_all, name='add_all'),

    path('users/army/<int:user_id>', user_army.get_user_army, name='user_army'),
    path('users/army/<int:user_id>/save_units', user_army.save_units, name='save_units'),
    path('users/army/<int:user_id>/toggle_no_units', user_army.toggle_no_units, name='toggle_no_units'),
    path('users/army/<int:user_id>/save_ships', user_army.save_ships, name='save_ships'),
    path('users/army/<int:user_id>/toggle_no_ships', user_army.toggle_no_ships, name='toggle_no_ships'),

    path('users/account/<int:user_id>', user_account.get_user_account, name='user_account'),
    path('users/account/<int:user_id>/save_researches', user_account.save_researches, name='save_researches'),
    path('users/account/<int:user_id>/edit_user_info', user_account.edit_user_info, name='edit_user_info'),
    path('users/account/<int:user_id>/delete_user', user_account.delete_user, name='delete_user'),
    path('users/account/<int:user_id>/enable_towns', user_account.enable_towns, name='enable_towns'),

    path('users/island/<int:user_id>/<int:island_id>', island.get_island, name='island'),
    path('users/island/edit_island', island.edit_island, name='edit_island'),

    path('users/towns/<int:user_id>', user_towns.get_user_towns, name='user_towns'),

    path('users/towns/<int:user_id>/update_town', user_towns.update_town, name='update_town'),
    path('users/towns/<int:user_id>/delete_town', user_towns.delete_town, name='delete_town'),

    path('users/islands/<int:user_id>', islands.get_islands, name='islands'),

    path('users/resources_rank/<int:user_id>', resources_rank.get_resources_rank, name='resources_rank'),

    path('panel', panel.panel_site, name='admin'),
    path('panel/web_scrap', panel.analyze_ranking_data, name='web_scrap'),
    path('panel/key_manager', key_manager.get_key_manager, name='key_manager'),
    path('panel/web_scrap_island', panel.analyze_island_data, name='web_scrap_island'),
    path('panel/web_scrap_town', panel.analyze_town_data, name='web_scrap_town'),
    path('panel/web_scrap_resources', panel.analyze_resources_data, name='web_scrap_resources'),
    path('panel/web_scrap_all_islands', panel.analyze_all_islands_data, name='web_scrap_all_islands'),
    path('panel/set_all_users_deleted', panel.set_all_users_deleted, name='set_all_users_deleted'),
    path('panel/update_users_ranking_score', panel.update_users_ranking_score, name='update_users_ranking_score'),

    path('guide/units', units.get_units, name='units'),
    path('guide/ships', ships.get_ships, name='ships'),
    path('guide/sawmill', sawmill.get_sawmill, name='sawmill'),

    path('guide/achievements/', achievements.get_achievements, name='achievements'),
    path('guide/achievements/web_scrap_achievements', achievements.analyze_achievements_data, name='web_scrap_achievements'),
    path('guide/user_achievements/<int:user_id>/<int:category_id>', user_achievements.get_user_achievements, name='achievements_category'),
    path('guide/user_achievements/level_up', user_achievements.level_up, name='achievements_level_up'),
    path('guide/user_achievements/confirm_progress', user_achievements.confirm_progress, name='confirm_progress'),

    path('statistics/players/<int:user_id>', statistics_players.get_statistics_players, name='statistics_players'),
    path('statistics/alliances/<int:user_id>', statistics_alliances.get_statistics_alliances, name='statistics_alliances'),
    path('statistics/scores/<int:user_id>', statistics_scores.get_statistics_scores, name='statistics_scores'),
    path('statistics/achievements', statistics_achievements.get_statistics_achievements,name='statistics_achievements'),
    path('statistics/save_users_statistics', statistics_players.save_users_statistics, name='save_users_statistics'),
    path('statistics/save_alliances_statistics', statistics_alliances.save_alliances_statistics, name='save_alliances_statistics'),
    path('settings/', settings.get_settings, name='settings')


]


# TODO
#  surowce - kolory, hover, 1 000
#  robotnicy/poziom
