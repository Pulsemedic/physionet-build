# Generated by Django 2.1.9 on 2019-08-06 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0028_auto_20190725_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='publishedproject',
            name='display_publications',
            field=models.BooleanField(default=True),
        ),
    ]
