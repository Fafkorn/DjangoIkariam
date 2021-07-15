from django_filters import CharFilter, FilterSet, OrderingFilter, NumberFilter, ModelChoiceFilter
from django.forms import TextInput, Select
from ..models import *


class IslandFilter(FilterSet):
    order_by = OrderingFilter(
        fields=(
            ('wood_level', 'Tartak'),
            ('luxury_level', 'Kopalnia'),
            ('towns', 'Miasta'),
        )
    )

    wood_level = NumberFilter(field_name='wood_level', lookup_expr='gt')
    luxury_level = NumberFilter(field_name='luxury_level', lookup_expr='gt')

    class Meta:
        model = Island
        fields = ['x', 'y', 'luxury_resource', 'has_tower']


class UserFilter(FilterSet):
    user_name = CharFilter(field_name='user_name',
                          lookup_expr='icontains',
                          label="Nazwa użytkownika",
                          widget=TextInput(attrs={'class': 'form-control'}))

    alliance = CharFilter(field_name='alliance',
                          lookup_expr='icontains',
                          label="Sojusz",
                          widget=TextInput(attrs={'class': 'form-control'}))

    user_status = ModelChoiceFilter(queryset=UserStatus.objects.all(),
                                    label="Status",
                                    widget=Select(attrs={'class': 'form-control'}))

    order_by = OrderingFilter(
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
        ),
        label="Sortuj"
    )

    order_by.descending_fmt = False

    class Meta:
        model = User
        fields = []
        ordering = ['score', 'master_builders', 'building_levels']






