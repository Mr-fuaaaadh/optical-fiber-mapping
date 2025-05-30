# Generated by Django 5.2 on 2025-05-10 11:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('office', '0005_branch_created_by_office_created_by'),
        ('opticalfiber_app', '0003_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('address', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='office.office')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='opticalfiber_app.staff')),
            ],
        ),
    ]
