# Generated by Django 2.1.2 on 2018-10-25 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='version',
            field=models.IntegerField(default=1),
        ),
    ]