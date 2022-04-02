import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ...models import User, Unit, UserAchievement, Ship
from mysite.helper.models import DefaultUsersConnection


@login_required(login_url='helper:login')
def get_statistics_achievements(request):
    connected_user = DefaultUsersConnection.objects.filter(auth_user=request.user.id)
    user = connected_user[0] if connected_user else User.objects.get(pk=1)
    unit_achievements = get_unit_achievements_data(user)
    ship_achievements = get_ship_achievements_data(user)

    context = {'unit_achievements': unit_achievements,
               'units_sum': get_units_sum(unit_achievements),
               'ship_achievements': ship_achievements,
               'ships_sum': get_ships_sum(ship_achievements),
               'user': user,
               'title': 'Statystyki - Osiągnięcia'}
    return render(request, 'helper/statistics/statistics_achievements.html', context)


def get_unit_achievements_data(user):
    unit_achievements_data = []
    unit_achievements = UserAchievement.objects.filter(user__id=user.id, achievement_level__achievement__category__id=6).order_by('achievement_level__achievement__order')
    skip_words = ['Niszczyciel', 'Spartan', 'Szpiedzy']
    unit_types = Unit.objects.all()
    for unit_achievement in unit_achievements:
        if any(skip_word in unit_achievement.achievement_level.achievement.name for skip_word in skip_words):
            continue
        correct_unit_type = get_correct_unit_type(unit_achievement, unit_types)
        remaining = get_remaining_units(unit_achievement, correct_unit_type)
        unit_achievements_data.append({'achievement': unit_achievement,
                                       'unit': correct_unit_type,
                                       'remains': remaining}
                                      )
    return unit_achievements_data


def get_correct_unit_type(achievement, unit_types):
    for unit_type in unit_types:
        if unit_type.name in achievement.achievement_level.achievement.name or (unit_type.name == 'Oszczepnik' and achievement.achievement_level.achievement.name == 'Producent: Oszczepnicy'):
            return unit_type
    return None


def get_remaining_units(unit_achievement, correct_unit_type):
    if not unit_achievement.progress:
        return None
    units_left = unit_achievement.achievement_level.requirements - int(unit_achievement.progress)
    units_required = unit_achievement.achievement_level.requirements
    return {'units': units_left,
            'units_percentage': math.floor(int(unit_achievement.progress) * 100 / unit_achievement.achievement_level.requirements),
            'wood_costs': units_left * correct_unit_type.wood_costs,
            'wood_costs_all': units_left * correct_unit_type.wood_costs,
            'wine_costs': units_left * correct_unit_type.wine_costs,
            'crystal_costs': units_left * correct_unit_type.crystal_costs,
            'sulfur_costs': units_left * correct_unit_type.sulfur_costs,
            'men_costs': units_left * correct_unit_type.men_costs,
            'time_costs': (units_left * correct_unit_type.time)/12,
            'all_time_costs': (units_required * correct_unit_type.time)/12,
            'all_resources_costs': units_required * (correct_unit_type.wood_costs + correct_unit_type.wine_costs +
                                                     correct_unit_type.crystal_costs + correct_unit_type.sulfur_costs),
            'all_men_costs': units_required * correct_unit_type.men_costs,
            }


def get_units_sum(unit_achievements):
    wood_costs = 0
    wine_costs = 0
    crystal_costs = 0
    sulfur_costs = 0
    men_costs = 0
    time_costs = 0
    all_men_costs = 0
    all_resources_costs = 0
    all_time_costs = 0
    for unit_achievement in unit_achievements:
        if unit_achievement['remains'] is not None:
            wood_costs += unit_achievement['remains']['wood_costs']
            wine_costs += unit_achievement['remains']['wine_costs']
            crystal_costs += unit_achievement['remains']['crystal_costs']
            sulfur_costs += unit_achievement['remains']['sulfur_costs']
            men_costs += unit_achievement['remains']['men_costs']
            time_costs += unit_achievement['remains']['time_costs']
            all_time_costs += unit_achievement['remains']['all_time_costs']
            all_resources_costs += unit_achievement['remains']['all_resources_costs']
            all_men_costs += unit_achievement['remains']['all_men_costs']
    return {
        'wood_costs': wood_costs,
        'wine_costs': wine_costs,
        'crystal_costs': crystal_costs,
        'sulfur_costs': sulfur_costs,
        'men_costs': men_costs,
        'time_costs': time_costs,
        'men_costs_percentage': int((all_men_costs - men_costs)*100/all_men_costs),
        'resources_costs_percentage': int((all_resources_costs - (wood_costs + wine_costs + crystal_costs + sulfur_costs))*100/all_resources_costs),
        'time_costs_percentage': int((all_time_costs - time_costs)*100/all_time_costs),
    }


def get_ship_achievements_data(user):
    ship_achievements_data = []
    ship_achievements = UserAchievement.objects.filter(user__id=user.id, achievement_level__achievement__category__id=7).order_by('achievement_level__achievement__order')
    skip_words = ['Niszczyciel', 'Statki handlowe']
    ship_types = Ship.objects.all()
    for ship_achievement in ship_achievements:
        if any(skip_word in ship_achievement.achievement_level.achievement.name for skip_word in skip_words):
            continue
        correct_ship_type = get_correct_ship_type(ship_achievement, ship_types)
        remaining = get_remaining_ships(ship_achievement, correct_ship_type)
        ship_achievements_data.append({'achievement': ship_achievement,
                                       'ship': correct_ship_type,
                                       'remains': remaining}
                                      )
    return ship_achievements_data


def get_correct_ship_type(achievement, ship_types):
    for ship_type in ship_types:
        if ship_type.name in achievement.achievement_level.achievement.name or (ship_type.name == 'Oszczepnik' and achievement.achievement_level.achievement.name == 'Producent: Oszczepnicy'):
            return ship_type
    return None


def get_remaining_ships(ship_achievement, correct_ship_type):
    if not ship_achievement.progress:
        return None
    ships_left = ship_achievement.achievement_level.requirements - int(ship_achievement.progress)
    ships_required = ship_achievement.achievement_level.requirements
    return {'ships': ships_left,
            'ships_percentage': math.floor(int(ship_achievement.progress) * 100 / ship_achievement.achievement_level.requirements),
            'wood_costs': ships_left * correct_ship_type.wood_costs,
            'wood_costs_all': ships_left * correct_ship_type.wood_costs,
            'wine_costs': ships_left * correct_ship_type.wine_costs,
            'crystal_costs': ships_left * correct_ship_type.crystal_costs,
            'sulfur_costs': ships_left * correct_ship_type.sulfur_costs,
            'men_costs': ships_left * correct_ship_type.men_costs,
            'time_costs': (ships_left * correct_ship_type.time)/12,
            'all_time_costs': (ships_required * correct_ship_type.time)/12,
            'all_resources_costs': ships_required * (correct_ship_type.wood_costs + correct_ship_type.wine_costs +
                                                     correct_ship_type.crystal_costs + correct_ship_type.sulfur_costs),
            'all_men_costs': ships_required * correct_ship_type.men_costs,
            }


def get_ships_sum(ship_achievements):
    wood_costs = 0
    wine_costs = 0
    crystal_costs = 0
    sulfur_costs = 0
    men_costs = 0
    time_costs = 0
    all_men_costs = 0
    all_resources_costs = 0
    all_time_costs = 0
    for ship_achievement in ship_achievements:
        if ship_achievement['remains'] is not None:
            wood_costs += ship_achievement['remains']['wood_costs']
            wine_costs += ship_achievement['remains']['wine_costs']
            crystal_costs += ship_achievement['remains']['crystal_costs']
            sulfur_costs += ship_achievement['remains']['sulfur_costs']
            men_costs += ship_achievement['remains']['men_costs']
            time_costs += ship_achievement['remains']['time_costs']
            all_time_costs += ship_achievement['remains']['all_time_costs']
            all_resources_costs += ship_achievement['remains']['all_resources_costs']
            all_men_costs += ship_achievement['remains']['all_men_costs']
    return {
        'wood_costs': wood_costs,
        'wine_costs': wine_costs,
        'crystal_costs': crystal_costs,
        'sulfur_costs': sulfur_costs,
        'men_costs': men_costs,
        'time_costs': time_costs,
        'men_costs_percentage': int((all_men_costs - men_costs)*100/all_men_costs),
        'resources_costs_percentage': int((all_resources_costs - (wood_costs + wine_costs + crystal_costs + sulfur_costs))*100/all_resources_costs),
        'time_costs_percentage': int((all_time_costs - time_costs)*100/all_time_costs),
    }
