import django_filters
from django import forms

from ..models import *


class IslandFilter(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=(
            ('wood_level', 'Tartak'),
            ('luxury_level', 'Kopalnia'),
            ('towns', 'Miasta'),
        )
    )

    wood_level = django_filters.NumberFilter(field_name='wood_level', lookup_expr='gt')
    luxury_level = django_filters.NumberFilter(field_name='luxury_level', lookup_expr='gt')

    class Meta:
        model = Island
        fields = ['x', 'y', 'luxury_resource', 'has_tower']
        # exclude = ['miracle_level', 'miracle', 'wood_resource']


class UserFilter(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=(
            ('score', 'Całkowity wynik'),
            ('master_builders', 'Mistrzowie budowy'),
            ('building_levels', 'Poziomy budynków'),
            ('scientists', 'Naukowcy'),
            ('research_level', 'Poziomy badań'),
            ('generals', 'Generałowie'),
            ('gold', 'Złoto'),
            ('offensive', 'Punkty ofensywy'),
            ('defensive', 'Punkty defensywy'),
            ('trading', 'Handlarz'),
            ('resources', 'Surowce'),
            ('donations', 'Datki'),
            ('piracy', 'Puntky abordażu'),
        )
    )
    order_by.descending_fmt = False

