# Generated by Django 3.0.8 on 2020-08-27 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0006_ship_shipinstance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='townresources',
            name='crystal',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='townresources',
            name='marble',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='townresources',
            name='sulfur',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='townresources',
            name='wine',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='townresources',
            name='wood',
            field=models.IntegerField(default=0),
        ),
    ]
