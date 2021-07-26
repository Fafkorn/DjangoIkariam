from datetime import datetime

from django.db import models


class UserStatus(models.Model):
    user_status_name = models.CharField(max_length=40)

    def __str__(self):
        return self.user_status_name


class User(models.Model):
    user_name = models.CharField(max_length=50)
    user_status = models.ForeignKey(UserStatus, on_delete=models.SET_NULL, default=None, null=True)
    shipping_future = models.IntegerField(default=0)
    economy_future = models.IntegerField(default=0)
    science_future = models.IntegerField(default=0)
    military_future = models.IntegerField(default=0)

    score = models.IntegerField(default=0)
    master_builders = models.IntegerField(default=0)
    building_levels = models.IntegerField(default=0)
    scientists = models.IntegerField(default=0)
    research_level = models.IntegerField(default=0)
    generals = models.IntegerField(default=0)
    gold = models.BigIntegerField(default=0)
    offensive = models.IntegerField(default=0)
    defensive = models.IntegerField(default=0)
    trading = models.IntegerField(default=0)
    resources = models.IntegerField(default=0)
    donations = models.IntegerField(default=0)
    piracy = models.IntegerField(default=0)

    alliance = models.CharField(max_length=50, default='', null=True)
    last_visit = models.DateTimeField(default=datetime(2015, 10, 9, 23, 55, 59, 342380))

    def __str__(self):
        return self.user_name

    def get_population(self):
        return self.score - (self.master_builders + self.scientists + self.generals)


class Resource(models.Model):
    name = models.CharField(max_length=50)
    image_path = models.ImageField(upload_to='img')
    mine_image_path = models.ImageField(upload_to='img', default='')

    def __str__(self):
        return str(self.name)


class Miracle(models.Model):
    name = models.CharField(max_length=50)
    image_path = models.ImageField(upload_to='img')

    def __str__(self):
        return str(self.name)


class Island(models.Model):
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    name = models.CharField(max_length=50, default='Brak')
    wood_resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='wood_resource_fk')
    wood_level = models.IntegerField(default=0)
    luxury_resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='luxury_resource_fk', null=True)
    luxury_level = models.IntegerField(default=0)
    miracle = models.ForeignKey(Miracle, on_delete=models.CASCADE, null=True)
    miracle_level = models.IntegerField(default=0)
    version = models.IntegerField(default=0)
    has_tower = models.BooleanField(default=False)

    def __str__(self):
        return str('[' + str(self.x) + ':' + str(self.y) + ']')


class SawMillWorkers(models.Model):
    level = models.IntegerField(default=0)
    workers = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return str('Level ' + str(self.level))


class MineWorkers(models.Model):
    level = models.IntegerField(default=0)
    workers = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return str('Level ' + str(self.level))


class Town(models.Model):
    town_name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    island = models.ForeignKey(Island, on_delete=models.CASCADE, null=True)
    in_game_id = models.IntegerField(default=0)
    no_units = models.BooleanField(default=False)
    no_ships = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        is_new = True if not self.id else False
        super(Town, self).save(*args, **kwargs)
        if is_new:
            self.create_related_objects()

    def __str__(self):
        return str(self.town_name + '(' + self.user.user_name + ')')

    def create_related_objects(self):
        buildings_to_save = []
        building_types = Building.objects.all()
        for building_type in building_types:
            building_instance = BuildingInstance(building_type=building_type, building_town=self)
            buildings_to_save.append(building_instance)
        BuildingInstance.objects.bulk_create(buildings_to_save)

        units_to_save = []
        unit_types = Unit.objects.all()
        for unit_type in unit_types:
            unit_instance = UnitInstance(unit=unit_type, town=self)
            units_to_save.append(unit_instance)
        UnitInstance.objects.bulk_create(units_to_save)

        ships_to_save = []
        ship_types = Ship.objects.all()
        for ship_type in ship_types:
            ship_instance = ShipInstance(ship=ship_type, town=self)
            ships_to_save.append(ship_instance)
        ShipInstance.objects.bulk_create(ships_to_save)

        town_resources = TownResources(town=self)
        town_resources.save()


class Building(models.Model):
    building_name = models.CharField(max_length=50)
    image_path = models.ImageField(upload_to='img')
    image_icon_path = models.ImageField(upload_to='img', default=None)
    max_level = models.IntegerField()
    order = models.IntegerField(default=0)
    description = models.CharField(max_length=500, default='')

    def save(self, *args, **kwargs):
        is_new = True if not self.id else False
        super(Building, self).save(*args, **kwargs)
        if is_new:
            towns = Town.objects.all()
            for town in towns:
                building_instance = BuildingInstance(building_type=self, building_town=town)
                building_instance.save()

    def __str__(self):
        return self.building_name


class BuildingInstance(models.Model):
    building_type = models.ForeignKey(Building, on_delete=models.CASCADE)
    building_town = models.ForeignKey(Town, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    is_upgraded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.building_type.building_name + ' (' + str(self.level) + ') ' + '(' + self.building_town.town_name + ')')


class TownResources(models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    wood = models.IntegerField(default=0)
    wine = models.IntegerField(default=0)
    marble = models.IntegerField(default=0)
    crystal = models.IntegerField(default=0)
    sulfur = models.IntegerField(default=0)
    wood_production = models.IntegerField(default=0)
    wine_production = models.IntegerField(default=0)
    marble_production = models.IntegerField(default=0)
    crystal_production = models.IntegerField(default=0)
    sulfur_production = models.IntegerField(default=0)
    tavern_expenses = models.IntegerField(default=0)
    save_time = models.DateTimeField(default=datetime(2015, 10, 9, 23, 55, 59, 342380))

    def __str__(self):
        return str(self.town.town_name + ' ' + 'Resources')

    def calc_time_left(self):
        if self.wine_production >= self.tavern_expenses:
            return 'Nigdy'
        else:
            hours_left = int(self.wine / (self.tavern_expenses - self.wine_production))
            if hours_left > 24:
                return str(int(hours_left/24)) + 'D ' + str(hours_left % 24) + 'h'
            return str(hours_left) + 'h'


class Unit(models.Model):
    name = models.CharField(max_length=50)
    image_path = models.ImageField(upload_to='img')
    hour_costs = models.IntegerField(default=0)
    points = models.FloatField(default=0.0)

    big_image_path = models.ImageField(upload_to='img', null=True)
    wood_costs = models.IntegerField(default=0)
    wine_costs = models.IntegerField(default=0)
    crystal_costs = models.IntegerField(default=0)
    sulfur_costs = models.IntegerField(default=0)
    men_costs = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    barracks_level = models.IntegerField(default=0)
    hit_points = models.IntegerField(default=0)
    armor = models.IntegerField(default=0)
    armor_upgrade = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)
    damage_upgrade = models.IntegerField(default=0)
    ammunition = models.IntegerField(default=0)
    size = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class UnitInstance(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)

    def __str__(self):
        return str(self.unit.name + ' (' + str(self.town.town_name) + ')')


class Ship(models.Model):
    name = models.CharField(max_length=50)
    image_path = models.ImageField(upload_to='img')
    hour_costs = models.IntegerField(default=0)
    points = models.FloatField(default=0.0)

    big_image_path = models.ImageField(upload_to='img', null=True)
    wood_costs = models.IntegerField(default=0)
    wine_costs = models.IntegerField(default=0)
    crystal_costs = models.IntegerField(default=0)
    sulfur_costs = models.IntegerField(default=0)
    men_costs = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    shipyard_level = models.IntegerField(default=0)
    hit_points = models.IntegerField(default=0)
    armor = models.IntegerField(default=0)
    armor_upgrade = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    damage = models.IntegerField(default=0)
    damage_upgrade = models.IntegerField(default=0)
    ammunition = models.IntegerField(default=0)
    size = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class ShipInstance(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)

    def __str__(self):
        return str(self.ship.name + ' (' + str(self.town.town_name) + ')')


class AchievementCategory(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return str(self.name)


class Achievement(models.Model):
    name = models.CharField(max_length=60)
    category = models.ForeignKey(AchievementCategory, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    progress = models.CharField(max_length=100, null=True)
    image_path = models.ImageField(upload_to='img')
    max_level = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class AchievementLevel(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    description = models.CharField(max_length=120)
    level = models.IntegerField(default=0)

    def __str__(self):
        return str(self.achievement.name + ' - ' + self.description)


class RegisterKey(models.Model):
    key = models.CharField(max_length=20)


class DefaultUsersConnection(models.Model):
    auth_user = models.IntegerField(null=True)
    game_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
