# Generated by Django 2.2.9 on 2021-11-28 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20211128_1626'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
    ]
