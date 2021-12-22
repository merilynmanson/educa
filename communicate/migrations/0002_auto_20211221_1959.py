# Generated by Django 3.2.8 on 2021-12-21 12:59

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_rename_userscheckedtestitems_userstestitems'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communicate', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField()),
            ],
        ),
        migrations.DeleteModel(
            name='Discussion',
        ),
        migrations.AddField(
            model_name='comment',
            name='date',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2021, 12, 21, 12, 59, 5, 252603, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='module',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.module'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='replies_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='communicate.comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='text',
            field=models.TextField(default='Comment this is a comment!'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentvote',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communicate.comment'),
        ),
        migrations.AddField(
            model_name='commentvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together={('user', 'comment')},
        ),
    ]
