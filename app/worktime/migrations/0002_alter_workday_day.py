# Generated by Django 4.2.7 on 2023-11-14 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worktime', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workday',
            name='day',
            field=models.IntegerField(choices=[(0, 'Normal'), (1, 'Weekend'), (2, 'Times off'), (3, 'Sick leave'), (4, 'Public holiday'), (5, 'Job Travel')], default='0'),
        ),
    ]