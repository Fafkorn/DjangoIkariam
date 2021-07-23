# Generated by Django 3.0.8 on 2021-07-13 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0032_userstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_status',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='helper.UserStatus'),
        ),
    ]
