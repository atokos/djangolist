# Generated by Django 2.1.2 on 2018-10-19 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20181018_1525'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auction',
            options={'permissions': (('ban_auction', 'Can ban an auction'), ('view_banned_auctions', 'Can view banned auctions'))},
        ),
    ]