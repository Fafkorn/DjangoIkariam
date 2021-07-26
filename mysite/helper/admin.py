from django.contrib import admin

from .models import User, Town, Building, BuildingInstance, \
    TownResources, Resource, Unit, UnitInstance, Ship, ShipInstance, Island, Miracle, \
    AchievementCategory, Achievement, AchievementLevel, SawMillWorkers, MineWorkers, \
    UserStatus, RegisterKey, DefaultUsersConnection

admin.site.register(User)
admin.site.register(Town)
admin.site.register(Building)
admin.site.register(BuildingInstance)
admin.site.register(TownResources)
admin.site.register(Resource)
admin.site.register(Unit)
admin.site.register(UnitInstance)
admin.site.register(Ship)
admin.site.register(ShipInstance)
admin.site.register(Island)
admin.site.register(Miracle)
admin.site.register(AchievementCategory)
admin.site.register(Achievement)
admin.site.register(AchievementLevel)
admin.site.register(SawMillWorkers)
admin.site.register(MineWorkers)
admin.site.register(UserStatus)
admin.site.register(RegisterKey)
admin.site.register(DefaultUsersConnection)

