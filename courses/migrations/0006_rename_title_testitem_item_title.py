# Generated by Django 3.2.8 on 2021-12-11 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_test_testitem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testitem',
            old_name='title',
            new_name='item_title',
        ),
    ]
