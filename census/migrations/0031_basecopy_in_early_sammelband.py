# Generated by Django 2.0.9 on 2020-02-25 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0030_auto_20190927_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='basecopy',
            name='in_early_sammelband',
            field=models.BooleanField(default=False),
        ),
    ]
