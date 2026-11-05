from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='EriLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cn', models.CharField(blank=True, max_length=255)),
                ('stir', models.CharField(blank=True, max_length=9)),
                ('pinfl', models.CharField(blank=True, max_length=14)),
                ('serial', models.CharField(blank=True, max_length=128)),
                ('verified_by', models.CharField(max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
