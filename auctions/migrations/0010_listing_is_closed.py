# Generated by Django 5.1.7 on 2025-04-18 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_remove_listing_is_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
