# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2020-05-09 16:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='菜单名称')),
                ('weight', models.IntegerField(default=100, verbose_name='权重')),
                ('icon', models.CharField(blank=True, max_length=32, null=True, verbose_name='图标')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=1000, verbose_name='路由地址')),
                ('title', models.CharField(max_length=32, verbose_name='路由名称')),
                ('icon', models.CharField(blank=True, max_length=32, null=True, verbose_name='菜单图标')),
                ('url_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='路由别名')),
                ('menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu', verbose_name='一级菜单')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Permission', verbose_name='二级菜单及权限')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('permissions', models.ManyToManyField(to='rbac.Permission')),
            ],
        ),
    ]