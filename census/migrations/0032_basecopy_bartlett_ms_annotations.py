from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('census', '0031_basecopy_in_early_sammelband'),
    ]

    operations = [
        migrations.AddField(
            model_name='basecopy',
            name='Bartlett_MS_Annotations',
            field=models.TextField(null=True, blank=True, default='')
        ),
    ]
