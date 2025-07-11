# Generated by Django 4.2.7 on 2025-06-27 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0007_forumthread_forumpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField()),
                ('link', models.URLField()),
                ('published_at', models.DateTimeField()),
            ],
        ),
    ]
