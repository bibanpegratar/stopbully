# Generated by Django 4.0.4 on 2022-05-08 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_detection', '0002_alter_image_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
    ]
