# Generated by Django 4.0.4 on 2023-10-04 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automail', '0007_alter_emailtemplate_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailconfiguration',
            name='name',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
    ]
