# Generated by Django 2.0.9 on 2019-09-26 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0028_auto_20190916_1825'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='provenanceownership',
            options={'verbose_name_plural': 'Provenance Ownership Records'},
        ),
        migrations.AddField(
            model_name='basecopy',
            name='rasmussen_west',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='basecopy',
            name='rasmussen_west_history',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]