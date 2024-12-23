# Generated by Django 5.1.3 on 2024-12-16 15:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Debate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('start_time', models.DateTimeField(verbose_name='Start time')),
                ('end_time', models.DateTimeField(verbose_name='End time')),
                ('status', models.CharField(choices=[('Scheduled', 'Scheduled'), ('Ongoing', 'Ongoing'), ('Finished', 'Finished'), ('Canceled', 'Canceled')], default='Scheduled', max_length=20, verbose_name='Status')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_debates', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_debates', to='debate.category', verbose_name='Category')),
                ('participants', models.ManyToManyField(blank=True, related_name='participated_debates', to=settings.AUTH_USER_MODEL, verbose_name='Participants')),
            ],
        ),
        migrations.CreateModel(
            name='Argument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Text')),
                ('vote_count', models.IntegerField(default=0, verbose_name='Vote count')),
                ('side', models.CharField(choices=[('Pro', 'Pro'), ('Con', 'Con')], max_length=3, verbose_name='Side')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('winner', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('debate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debate_arguments', to='debate.debate', verbose_name='Debate')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('argument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='debate.argument', verbose_name='Argument')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_votes', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'unique_together': {('user', 'argument')},
            },
        ),
    ]
