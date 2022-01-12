# Generated by Django 2.2.9 on 2021-11-28 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20211127_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(verbose_name='Описание группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='адрес группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(
                max_length=200, verbose_name='Название группы'
            ),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='posts',
                to='posts.Group',
            ),
        ),
    ]
