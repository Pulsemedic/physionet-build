# Generated by Django 2.1.7 on 2019-02-20 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20190215_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publishedproject',
            name='compressed_storage_size',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='main_storage_size',
            field=models.BigIntegerField(default=0),
        ),
    ]
