# Generated by Django 3.0.8 on 2020-08-26 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0005_unit_hour_costs'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image_path', models.ImageField(upload_to='img')),
                ('hour_costs', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ShipInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0)),
                ('ship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='helper.Ship')),
                ('town', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='helper.Town')),
            ],
        ),
    ]
