# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-27 17:07
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar', models.ImageField(blank=True, default=b'avatar/default.jpg', max_length=400, null=True, upload_to=b'avatar/%Y/%m', verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\xa4\xb4\xe5\x83\x8f')),
                ('sessionid', models.CharField(blank=True, default=b'', max_length=255, null=True)),
                ('isonline', models.IntegerField(default=0)),
                ('login_times', models.IntegerField(default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'default_permissions': ('read', 'change', 'add', 'delete'),
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AppInstall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(error_messages={b'blank': b'\xe5\x90\x8d\xe7\xa7\xb0: \xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba\xef\xbc\x81', b'invalid': b'\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xa1\xab\xe5\x86\x99\xe5\x90\x88\xe6\xb3\x95\xe7\x9a\x84\xe6\x95\xb4\xe6\x95\xb0\xe5\x80\xbc', b'max_length': b'\xe5\x90\x8d\xe7\xa7\xb0:\xe9\x95\xbf\xe5\xba\xa6\xe8\xb6\x85\xe8\xbf\x87\xe6\x8c\x87\xe5\xae\x9a\xe8\x8c\x83\xe5\x9b\xb4\xef\xbc\x81', b'unique': b'\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x81'}, help_text=b'\xe5\x90\x8d\xe7\xa7\xb0', max_length=200, unique=True)),
                ('version', models.CharField(blank=True, error_messages={b'blank': b'\xe7\x89\x88\xe6\x9c\xac: \xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba\xef\xbc\x81', b'invalid': b'\xe7\x89\x88\xe6\x9c\xac: \xe5\xa1\xab\xe5\x86\x99\xe5\x90\x88\xe6\xb3\x95\xe7\x9a\x84\xe6\x95\xb4\xe6\x95\xb0\xe5\x80\xbc', b'max_length': b'\xe7\x89\x88\xe6\x9c\xac:\xe9\x95\xbf\xe5\xba\xa6\xe8\xb6\x85\xe8\xbf\x87\xe6\x8c\x87\xe5\xae\x9a\xe8\x8c\x83\xe5\x9b\xb4\xef\xbc\x81', b'unique': b'\xe7\x89\x88\xe6\x9c\xac: \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x81'}, help_text=b'\xe7\x89\x88\xe6\x9c\xac', max_length=100, null=True)),
                ('app_image', models.ImageField(blank=True, default=b'app_images/default.jpg', help_text=b'app\xe7\x9a\x84\xe5\x9b\xbe\xe7\x89\x87', max_length=500, null=True, upload_to=b'app_images/')),
                ('description', models.CharField(blank=True, help_text=b'\xe8\xaf\xb4\xe6\x98\x8e', max_length=500, null=True)),
                ('app_sls_pkg', models.ImageField(blank=True, help_text=b'app\xe7\x9a\x84sls\xe5\x8c\x85', max_length=500, null=True, upload_to=b'app_sls_pkgs/')),
            ],
            options={
                'db_table': 'app_install',
            },
        ),
        migrations.CreateModel(
            name='AppInstallStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[(b'0', b'\xe5\xae\x89\xe8\xa3\x85\xe4\xb8\xad'), (b'1', b'\xe5\xae\x89\xe8\xa3\x85\xe6\x88\x90\xe5\x8a\x9f'), (b'2', b'\xe5\xae\x89\xe8\xa3\x85\xe5\x87\xba\xe9\x94\x99'), (b'3', b'\xe7\xad\x89\xe5\xbe\x85\xe4\xb8\xad')], default=b'0', help_text=b'\xe7\x8a\xb6\xe6\x80\x81', max_length=20, null=True)),
                ('error_message', models.CharField(blank=True, help_text=b'\xe9\x94\x99\xe8\xaf\xaf\xe4\xbf\xa1\xe6\x81\xaf', max_length=500, null=True)),
                ('used_time', models.CharField(blank=True, help_text=b'\xe7\x94\xa8\xe6\x97\xb6', max_length=200, null=True)),
                ('app_install', models.ForeignKey(help_text=b'app\xe7\x9a\x84\xe5\x90\x8d\xe7\xa7\xb0', on_delete=django.db.models.deletion.CASCADE, to='firstapp.AppInstall')),
            ],
            options={
                'db_table': 'app_install_status',
            },
        ),
        migrations.CreateModel(
            name='BusinessAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topology', models.IntegerField(choices=[(0, '\u4e8c\u7ea7\u62d3\u6251'), (1, '\u4e09\u7ea7\u62d3\u6251')], help_text=b'\xe6\x8b\x93\xe6\x89\x91\xe7\xbb\x93\xe6\x9e\x84\xef\xbc\x880-\xe4\xba\x8c\xe7\xba\xa7\xe6\x8b\x93\xe6\x89\x91\xef\xbc\x8c 1-\xe4\xb8\x89\xe7\xba\xa7\xe6\x8b\x93\xe6\x89\x91\xef\xbc\x89')),
                ('name', models.CharField(error_messages={b'blank': b'\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x90\x8d\xe7\xa7\xb0: \xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba\xef\xbc\x81', b'invalid': b'\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xa1\xab\xe5\x86\x99\xe5\x90\x88\xe6\xb3\x95\xe7\x9a\x84\xe6\x95\xb4\xe6\x95\xb0\xe5\x80\xbc', b'max_length': b'\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x90\x8d\xe7\xa7\xb0:\xe9\x95\xbf\xe5\xba\xa6\xe8\xb6\x85\xe8\xbf\x87\xe6\x8c\x87\xe5\xae\x9a\xe8\x8c\x83\xe5\x9b\xb4\xef\xbc\x81', b'unique': b'\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x81'}, help_text=b'\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x90\x8d\xe7\xa7\xb0', max_length=255, unique=True)),
                ('create_user', models.CharField(blank=True, help_text=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba\xe5\x91\x98', max_length=255, null=True)),
                ('create_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('lifecycle', models.IntegerField(blank=True, choices=[(0, '\u505c\u8fd0'), (1, '\u6d4b\u8bd5'), (2, '\u8fd0\u8425')], default=1, help_text=b'\xe7\x94\x9f\xe5\x91\xbd\xe5\x91\xa8\xe6\x9c\x9f\xef\xbc\x880-\xe5\x81\x9c\xe8\xbf\x90\xef\xbc\x8c1-\xe6\xb5\x8b\xe8\xaf\x95\xef\xbc\x8c 2-\xe8\xbf\x90\xe8\x90\xa5\xef\xbc\x89', null=True)),
                ('product_user', models.CharField(blank=True, help_text=b'\xe4\xba\xa7\xe5\x93\x81\xe4\xba\xba\xe5\x91\x98', max_length=255, null=True)),
                ('develop_user', models.CharField(blank=True, help_text=b'\xe5\xbc\x80\xe5\x8f\x91\xe4\xba\xba\xe5\x91\x98', max_length=255, null=True)),
                ('operation_user', models.CharField(blank=True, help_text=b'\xe8\xbf\x90\xe7\xbb\xb4\xe4\xba\xba\xe5\x91\x98', max_length=255, null=True)),
                ('test_user', models.CharField(blank=True, help_text=b'\xe6\xb5\x8b\xe8\xaf\x95\xe4\xba\xba\xe5\x91\x98', max_length=255, null=True)),
            ],
            options={
                'db_table': 'business_admin',
            },
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text=b'\xe9\x9b\x86\xe7\xbe\xa4\xe5\x90\x8d\xe5\xad\x97', max_length=100)),
                ('env_type', models.IntegerField(choices=[(0, '\u6d4b\u8bd5'), (1, '\u4f53\u9a8c'), (2, '\u6b63\u5f0f')], default=0, help_text=b'\xe7\x8e\xaf\xe5\xa2\x83\xe7\xb1\xbb\xe5\x9e\x8b')),
                ('service_status', models.BooleanField(default=True, help_text=b'\xe6\x9c\x8d\xe5\x8a\xa1\xe7\x8a\xb6\xe6\x80\x81')),
                ('cn_name', models.CharField(blank=True, help_text=b'\xe4\xb8\xad\xe6\x96\x87\xe5\x90\x8d\xe5\xad\x97', max_length=100, null=True)),
                ('description', models.CharField(blank=True, help_text=b'\xe6\x8f\x8f\xe8\xbf\xb0', max_length=500, null=True)),
                ('business', models.ForeignKey(help_text=b'\xe4\xb8\x9a\xe5\x8a\xa1', on_delete=django.db.models.deletion.CASCADE, related_name='clusters', to='firstapp.BusinessAdmin')),
            ],
            options={
                'db_table': 'cluster',
            },
        ),
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('parent_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='firstapp.GroupProfile')),
            ],
            options={
                'db_table': 'group_profile',
            },
        ),
        migrations.CreateModel(
            name='HostPs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.CharField(blank=True, help_text=b'\xe8\xbf\x9b\xe7\xa8\x8bPID\xe5\x8f\xb7', max_length=255, null=True)),
                ('user', models.CharField(blank=True, help_text=b'\xe8\xbf\x9b\xe7\xa8\x8b\xe7\x94\xa8\xe6\x88\xb7', max_length=255, null=True)),
                ('cpu_rate', models.CharField(blank=True, help_text=b'CPU\xe8\xb5\x84\xe6\xba\x90\xe5\x8d\xa0\xe7\x94\xa8\xe6\xaf\x94\xe7\x8e\x87', max_length=100, null=True)),
                ('mem_rate', models.CharField(blank=True, help_text=b'MEM\xe8\xb5\x84\xe6\xba\x90\xe5\x8d\xa0\xe7\x94\xa8\xe6\xaf\x94\xe7\x8e\x87', max_length=100, null=True)),
                ('stat', models.CharField(blank=True, help_text=b'\xe8\xbf\x9b\xe7\xa8\x8b\xe7\x8a\xb6\xe6\x80\x81', max_length=100, null=True)),
                ('run_time', models.CharField(blank=True, help_text=b'\xe8\xbf\x90\xe8\xa1\x8c\xe6\x97\xb6\xe9\x97\xb4', max_length=100, null=True)),
                ('command', models.CharField(blank=True, help_text=b'\xe8\xbf\x9b\xe7\xa8\x8b\xe5\x91\xbd\xe4\xbb\xa4', max_length=3000, null=True)),
                ('view_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text=b'\xe6\x9f\xa5\xe8\xaf\xa2\xe6\x97\xb6\xe9\x97\xb4', null=True)),
            ],
            options={
                'db_table': 'host_ps',
            },
        ),
        migrations.CreateModel(
            name='JenkinsJobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jenkins_server_url', models.CharField(help_text=b'Jenkins\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x9c\xb0\xe5\x9d\x80', max_length=2000)),
                ('user_id', models.CharField(blank=True, help_text=b'Jenkins\xe7\x94\xa8\xe6\x88\xb7id', max_length=500, null=True)),
                ('password', models.CharField(blank=True, help_text=b'Jenkins\xe7\x94\xa8\xe6\x88\xb7\xe5\xaf\x86\xe7\xa0\x81\xe6\x88\x96token', max_length=500, null=True)),
                ('job_url', models.CharField(blank=True, help_text=b'Jenkins\xe7\x9a\x84\xe8\xbf\x9e\xe6\x8e\xa5', max_length=1000, null=True)),
                ('color', models.CharField(blank=True, help_text=b'\xe9\xa2\x9c\xe8\x89\xb2\xe7\x8a\xb6\xe6\x80\x81', max_length=100, null=True)),
                ('job_name', models.CharField(blank=True, help_text=b'job\xe5\x90\x8d\xe7\xa7\xb0', max_length=500, null=True)),
                ('job_description', models.CharField(blank=True, help_text=b'job\xe6\x8f\x8f\xe8\xbf\xb0', max_length=2000, null=True)),
                ('last_completed_build', models.CharField(blank=True, help_text=b'\xe4\xb8\x8a\xe6\xac\xa1\xe5\xae\x8c\xe6\x88\x90\xe6\x9e\x84\xe5\xbb\xba', max_length=4000, null=True)),
                ('last_successful_build', models.CharField(blank=True, help_text=b'\xe4\xb8\x8a\xe6\xac\xa1\xe6\x88\x90\xe5\x8a\x9f\xe6\x9e\x84\xe5\xbb\xba', max_length=4000, null=True)),
                ('last_unsuccessful_build', models.CharField(blank=True, help_text=b'\xe4\xb8\x8a\xe6\xac\xa1\xe5\xa4\xb1\xe8\xb4\xa5\xe6\x9e\x84\xe5\xbb\xba', max_length=4000, null=True)),
                ('buildable', models.NullBooleanField(help_text=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x9e\x84\xe5\xbb\xba')),
                ('last_completed_build_info', models.TextField(blank=True, help_text=b'\xe6\x9c\x80\xe5\x90\x8e\xe5\xae\x8c\xe6\x88\x90\xe6\x9e\x84\xe5\xbb\xba\xe4\xbf\xa1\xe6\x81\xaf', null=True)),
                ('last_successful_build_info', models.TextField(blank=True, help_text=b'\xe6\x9c\x80\xe5\x90\x8e\xe6\x88\x90\xe5\x8a\x9f\xe6\x9e\x84\xe5\xbb\xba\xe4\xbf\xa1\xe6\x81\xaf', null=True)),
                ('last_unsuccessful_build_info', models.TextField(blank=True, help_text=b'\xe6\x9c\x80\xe5\x90\x8e\xe5\xa4\xb1\xe8\xb4\xa5\xe6\x9e\x84\xe5\xbb\xba\xe4\xbf\xa1\xe6\x81\xaf', null=True)),
                ('health_report_score', models.IntegerField(blank=True, help_text=b'\xe5\x81\xa5\xe5\xba\xb7\xe7\x8a\xb6\xe6\x80\x81\xe5\x88\x86\xe6\x95\xb0', null=True)),
                ('health_report_description', models.CharField(blank=True, help_text=b'\xe5\x81\xa5\xe5\xba\xb7\xe7\x8a\xb6\xe6\x80\x81\xe6\x8f\x8f\xe8\xbf\xb0', max_length=1000, null=True)),
                ('next_build_number', models.CharField(blank=True, help_text=b'\xe4\xb8\x8b\xe4\xb8\x80\xe4\xb8\xaa\xe6\x9e\x84\xe5\xbb\xba\xe5\x8f\xb7', max_length=100, null=True)),
            ],
            options={
                'db_table': 'jenkins_jobs',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('description', models.CharField(default=b'', max_length=255)),
                ('icon', models.CharField(default=b'', max_length=255)),
                ('remark', models.CharField(default=b'', max_length=255)),
                ('ordernum', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=1)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='firstapp.Menu')),
            ],
            options={
                'default_permissions': ('read', 'change', 'add', 'delete'),
                'db_table': 'menu',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text=b'\xe6\xa8\xa1\xe5\x9d\x97\xe5\x90\x8d\xe5\xad\x97', max_length=100)),
                ('maintain_user', models.CharField(blank=True, help_text=b'\xe7\xbb\xb4\xe6\x8a\xa4\xe4\xba\xba', max_length=255, null=True)),
                ('description', models.CharField(blank=True, help_text=b'\xe6\x8f\x8f\xe8\xbf\xb0', max_length=500, null=True)),
                ('business', models.ForeignKey(help_text=b'\xe4\xb8\x9a\xe5\x8a\xa1', on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='firstapp.BusinessAdmin')),
                ('cluster', models.ForeignKey(blank=True, help_text=b'\xe9\x9b\x86\xe7\xbe\xa4', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='firstapp.Cluster')),
            ],
            options={
                'db_table': 'module',
            },
        ),
        migrations.CreateModel(
            name='OperationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, help_text=b'\xe6\x93\x8d\xe4\xbd\x9c\xe7\x94\xa8\xe6\x88\xb7', max_length=100, null=True)),
                ('operate', models.CharField(blank=True, help_text=b'\xe6\x89\xa7\xe8\xa1\x8c\xe6\x93\x8d\xe4\xbd\x9c', max_length=500, null=True)),
                ('operate_result', models.TextField(blank=True, help_text=b'\xe6\x93\x8d\xe4\xbd\x9c\xe7\xbb\x93\xe6\x9e\x9c', null=True)),
            ],
            options={
                'db_table': 'operation_log',
            },
        ),
        migrations.CreateModel(
            name='ProjectCenter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(error_messages={b'blank': b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0: \xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba\xef\xbc\x81', b'invalid': b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xa1\xab\xe5\x86\x99\xe5\x90\x88\xe6\xb3\x95\xe7\x9a\x84\xe6\x95\xb4\xe6\x95\xb0\xe5\x80\xbc', b'max_length': b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0:\xe9\x95\xbf\xe5\xba\xa6\xe8\xb6\x85\xe8\xbf\x87\xe6\x8c\x87\xe5\xae\x9a\xe8\x8c\x83\xe5\x9b\xb4\xef\xbc\x81', b'unique': b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x81'}, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0', max_length=255, unique=True)),
                ('version', models.CharField(blank=True, help_text=b'\xe7\x89\x88\xe6\x9c\xac', max_length=100, null=True)),
                ('description', models.CharField(blank=True, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe7\xae\x80\xe4\xbb\x8b', max_length=500, null=True)),
                ('head', models.CharField(blank=True, help_text=b'\xe8\xb4\x9f\xe8\xb4\xa3\xe4\xba\xba', max_length=255, null=True)),
                ('code_lib_type', models.CharField(choices=[(b'0', b'Git'), (b'1', b'SVN')], default=b'0', help_text=b'\xe4\xbb\xa3\xe7\xa0\x81\xe4\xbb\x93\xe5\xba\x93', max_length=10)),
                ('lib_url', models.CharField(help_text=b'\xe4\xbb\xa3\xe7\xa0\x81\xe5\xba\x93\xe5\x9c\xb0\xe5\x9d\x80', max_length=500)),
                ('lib_branch', models.CharField(blank=True, help_text=b'\xe5\x88\x86\xe6\x94\xaf\xe5\x90\x8d', max_length=200, null=True)),
                ('lib_path', models.CharField(blank=True, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe6\x89\x80\xe5\x9c\xa8\xe4\xbb\x93\xe5\xba\x93\xe8\xb7\xaf\xe5\xbe\x84\xef\xbc\x88\xe7\xbb\x9d\xe5\xaf\xb9\xe8\xb7\xaf\xe5\xbe\x84\xef\xbc\x89', max_length=300, null=True)),
                ('lib_deploy_path', models.CharField(blank=True, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe4\xb8\xad\xe9\x9c\x80\xe8\xa6\x81\xe9\x83\xa8\xe7\xbd\xb2\xe8\xb7\xaf\xe5\xbe\x84\xef\xbc\x88\xe7\x9b\xb8\xe5\xaf\xb9lib_path\xe8\xb7\xaf\xe5\xbe\x84\xef\xbc\x89', max_length=300, null=True)),
                ('lib_username', models.CharField(blank=True, help_text=b'\xe4\xbb\xa3\xe7\xa0\x81\xe5\xba\x93\xe8\xb4\xa6\xe6\x88\xb7', max_length=255, null=True)),
                ('lib_password', models.CharField(blank=True, help_text=b'\xe4\xbb\xa3\xe7\xa0\x81\xe5\xba\x93\xe5\xaf\x86\xe7\xa0\x81', max_length=255, null=True)),
                ('develop_type', models.CharField(choices=[(b'0', b'java'), (b'1', b'python'), (b'2', b'node.js')], default=b'0', help_text=b'\xe5\xbc\x80\xe5\x8f\x91\xe8\xaf\xad\xe8\xa8\x80', max_length=20)),
                ('deploy_time', models.DateTimeField(blank=True, help_text=b'\xe9\x83\xa8\xe7\xbd\xb2\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('deploy_status', models.CharField(blank=True, choices=[(b'0', b'\xe7\xad\x89\xe5\xbe\x85\xe4\xb8\xad'), (b'1', b'\xe4\xbb\xbb\xe5\x8a\xa1\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad'), (b'2', b'\xe4\xbb\xbb\xe5\x8a\xa1\xe5\xae\x8c\xe6\x88\x90'), (b'3', b'\xe9\x83\xa8\xe7\xbd\xb2\xe6\x9c\x89\xe4\xbb\xbb\xe5\x8a\xa1\xe5\xa4\xb1\xe8\xb4\xa5')], help_text=b'\xe7\x8a\xb6\xe6\x80\x81', max_length=100, null=True)),
                ('deploy_port', models.IntegerField(blank=True, help_text=b'\xe9\x83\xa8\xe7\xbd\xb2\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8\xe7\xab\xaf\xe5\x8f\xa3', null=True)),
                ('is_start_service', models.NullBooleanField(default=False, help_text=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\x90\xaf\xe5\x8a\xa8\xe6\x9c\x8d\xe5\x8a\xa1')),
                ('deploy_docker_run', models.CharField(blank=True, help_text=b'\xe9\x83\xa8\xe7\xbd\xb2\xe7\x9a\x84docker run\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2', max_length=1000, null=True)),
                ('success_image_callback', models.CharField(blank=True, help_text=b'\xe6\x88\x90\xe5\x8a\x9f\xe7\x94\x9f\xe6\x88\x90\xe9\x95\x9c\xe5\x83\x8f\xe5\x90\x8e\xe7\x9a\x84\xe6\x93\x8d\xe4\xbd\x9c', max_length=2000, null=True)),
                ('docker_img_name', models.CharField(blank=True, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe9\x95\x9c\xe5\x83\x8f\xe5\x90\x8d\xe7\xa7\xb0', max_length=500, null=True)),
                ('deploy_container_name', models.CharField(blank=True, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\xae\xb9\xe5\x99\xa8\xe5\x90\x8d\xe7\xa7\xb0', max_length=500, null=True)),
            ],
            options={
                'db_table': 'project_center',
            },
        ),
        migrations.CreateModel(
            name='ProjectDeployInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minion_id', models.CharField(blank=True, help_text=b'\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8minion_id', max_length=1000, null=True)),
                ('step', models.IntegerField(blank=True, help_text=b'\xe6\xad\xa5\xe9\xaa\xa4', null=True)),
                ('step_status', models.CharField(blank=True, choices=[(b'0', b'\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad'), (b'1', b'\xe6\x88\x90\xe5\x8a\x9f'), (b'2', b'\xe5\xa4\xb1\xe8\xb4\xa5')], help_text=b'\xe6\xad\xa5\xe9\xaa\xa4\xe7\x9a\x84\xe9\x83\xa8\xe7\xbd\xb2\xe7\x8a\xb6\xe6\x80\x81', max_length=10, null=True)),
                ('title', models.CharField(blank=True, help_text=b'\xe6\xa0\x87\xe9\xa2\x98', max_length=500, null=True)),
                ('content', models.TextField(blank=True, help_text=b'\xe5\x86\x85\xe5\xae\xb9', null=True)),
            ],
            options={
                'db_table': 'project_deploy_info',
            },
        ),
        migrations.CreateModel(
            name='ProjectDockerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.CharField(blank=True, help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe6\x89\x80\xe5\x9c\xa8\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8\xe7\xab\xaf\xe5\x8f\xa3', max_length=100, null=True)),
                ('docker_img', models.CharField(help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe9\x95\x9c\xe5\x83\x8f\xe5\x90\x8d\xe7\xa7\xb0', max_length=500)),
                ('docker_container', models.CharField(help_text=b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\xae\xb9\xe5\x99\xa8\xe5\x90\x8d\xe7\xa7\xb0', max_length=500)),
                ('deploy_docker_run', models.CharField(blank=True, help_text=b'\xe5\x90\xaf\xe5\x8a\xa8\xe5\xae\xb9\xe5\x99\xa8\xe7\x9a\x84\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2', max_length=1000, null=True)),
                ('progress', models.IntegerField(blank=True, default=0, help_text=b'\xe8\xbf\x9b\xe5\xba\xa6', null=True)),
                ('status', models.CharField(blank=True, choices=[(b'0', b'\xe7\xad\x89\xe5\xbe\x85\xe4\xb8\xad'), (b'1', b'\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad'), (b'2', b'\xe6\x88\x90\xe5\x8a\x9f'), (b'3', b'\xe5\xa4\xb1\xe8\xb4\xa5')], help_text=b'\xe7\x8a\xb6\xe6\x80\x81', max_length=100, null=True)),
                ('message', models.CharField(blank=True, help_text=b'\xe7\x8a\xb6\xe6\x80\x81\xe4\xbf\xa1\xe6\x81\xaf', max_length=255, null=True)),
                ('is_start_service', models.NullBooleanField(default=False, help_text=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\x90\xaf\xe5\x8a\xa8\xe6\x9c\x8d\xe5\x8a\xa1')),
                ('generated_time', models.DateTimeField(blank=True, help_text=b'\xe7\x94\x9f\xe6\x88\x90\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('time_consume', models.CharField(blank=True, help_text=b'\xe8\x80\x97\xe6\x97\xb6', max_length=255, null=True)),
                ('project', models.ForeignKey(help_text=b'\xe9\xa1\xb9\xe7\x9b\xae', on_delete=django.db.models.deletion.CASCADE, to='firstapp.ProjectCenter')),
            ],
            options={
                'db_table': 'project_docker_info',
            },
        ),
        migrations.CreateModel(
            name='ProjectImageSave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.IntegerField(blank=True, default=0, help_text=b'\xe8\xbf\x9b\xe5\xba\xa6', null=True)),
                ('status', models.CharField(blank=True, choices=[(b'0', b'\xe7\xad\x89\xe5\xbe\x85\xe4\xb8\xad'), (b'1', b'\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad'), (b'2', b'\xe6\x88\x90\xe5\x8a\x9f'), (b'3', b'\xe5\xa4\xb1\xe8\xb4\xa5')], help_text=b'\xe7\x8a\xb6\xe6\x80\x81', max_length=100, null=True)),
                ('message', models.CharField(blank=True, help_text=b'\xe7\x8a\xb6\xe6\x80\x81\xe4\xbf\xa1\xe6\x81\xaf', max_length=255, null=True)),
                ('save_time', models.DateTimeField(blank=True, help_text=b'\xe7\x94\x9f\xe6\x88\x90\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('project', models.ForeignKey(help_text=b'\xe9\xa1\xb9\xe7\x9b\xae', on_delete=django.db.models.deletion.CASCADE, to='firstapp.ProjectCenter')),
            ],
            options={
                'db_table': 'project_image_save',
            },
        ),
        migrations.CreateModel(
            name='ReceiverHooks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_receiver', models.CharField(blank=True, help_text=b'\xe5\xaf\xbc\xe5\x85\xa5\xe6\x95\xb0\xe6\x8d\xae\xe7\x9a\x84\xe6\x8e\xa5\xe6\x94\xb6\xe5\x99\xa8\xe5\x9c\xb0\xe5\x9d\x80', max_length=500, null=True)),
                ('env', models.CharField(choices=[(b'dev', b'\xe5\xbc\x80\xe5\x8f\x91\xe7\x8e\xaf\xe5\xa2\x83'), (b'fat', b'\xe6\xb5\x8b\xe8\xaf\x95\xe7\x8e\xaf\xe5\xa2\x83'), (b'pro', b'\xe6\xad\xa3\xe5\xbc\x8f\xe7\x8e\xaf\xe5\xa2\x83')], default=b'dev', help_text=b'\xe6\x89\x80\xe5\xb1\x9e\xe7\x8e\xaf\xe5\xa2\x83', max_length=255)),
                ('name', models.CharField(help_text=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe5\x90\x8d\xe7\xa7\xb0', max_length=255)),
                ('description', models.CharField(blank=True, help_text=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe6\x8f\x8f\xe8\xbf\xb0', max_length=1000, null=True)),
                ('upgrade_url', models.CharField(help_text=b'\xe8\xa7\xa6\xe5\x8f\x91\xe6\x9b\xb4\xe6\x96\xb0\xe5\x9c\xb0\xe5\x9d\x80', max_length=500)),
                ('image_label', models.CharField(help_text=b'\xe9\x95\x9c\xe5\x83\x8f\xe6\xa0\x87\xe7\xad\xbe', max_length=100)),
                ('image_lib', models.CharField(help_text=b'\xe9\x95\x9c\xe5\x83\x8f\xe5\x9c\xb0\xe5\x9d\x80', max_length=500)),
                ('upgrade_time', models.DateTimeField(blank=True, help_text=b'\xe6\x9b\xb4\xe6\x96\xb0\xe5\xba\x94\xe7\x94\xa8\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('target_docker_hub', models.CharField(blank=True, help_text=b'\xe7\x9b\xae\xe6\xa0\x87\xe9\x95\x9c\xe5\x83\x8f\xe5\xba\x93', max_length=300, null=True)),
                ('load_docker_hub', models.CharField(blank=True, help_text=b'\xe8\xa2\xab\xe5\xaf\xbc\xe5\x85\xa5\xe7\x9a\x84\xe9\x95\x9c\xe5\x83\x8f', max_length=300, null=True)),
                ('is_backup', models.CharField(blank=True, default=b'1', help_text=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xa4\x87\xe4\xbb\xbd\xe5\x8e\x9f\xe6\x9c\x89\xe9\x95\x9c\xe5\x83\x8f', max_length=10, null=True)),
                ('target_docker_hub_label', models.CharField(blank=True, help_text=b'\xe5\xa4\x87\xe4\xbb\xbd\xe7\x9a\x84\xe9\x95\x9c\xe5\x83\x8f\xe6\xa0\x87\xe7\xad\xbe', max_length=300, null=True)),
                ('target_docker_hub_username', models.CharField(blank=True, help_text=b'\xe7\x9b\xae\xe6\xa0\x87\xe9\x95\x9c\xe5\x83\x8f\xe5\xba\x93\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d', max_length=300, null=True)),
                ('target_docker_hub_password', models.CharField(blank=True, help_text=b'\xe7\x9b\xae\xe6\xa0\x87\xe9\x95\x9c\xe5\x83\x8f\xe5\xba\x93\xe7\x94\xa8\xe6\x88\xb7\xe5\xaf\x86\xe7\xa0\x81', max_length=300, null=True)),
                ('salt_minion_id', models.CharField(blank=True, help_text=b'\xe6\x93\x8d\xe4\xbd\x9c\xe4\xb8\xbb\xe6\x9c\xba', max_length=300, null=True)),
                ('push_docker_hub_time', models.DateTimeField(blank=True, help_text=b'\xe5\x8f\x91\xe5\xb8\x83\xe9\x95\x9c\xe5\x83\x8f\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('push_docker_hub_content', models.TextField(blank=True, help_text=b'\xe5\x8f\x91\xe5\xb8\x83\xe9\x95\x9c\xe5\x83\x8f\xe8\xbf\x87\xe7\xa8\x8b', null=True)),
            ],
            options={
                'db_table': 'receiver_hooks',
            },
        ),
        migrations.CreateModel(
            name='SaltMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(error_messages={b'blank': b'\xe5\x90\x8d\xe7\xa7\xb0: \xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba\xef\xbc\x81', b'invalid': b'\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xa1\xab\xe5\x86\x99\xe5\x90\x88\xe6\xb3\x95\xe7\x9a\x84\xe6\x95\xb4\xe6\x95\xb0\xe5\x80\xbc', b'max_length': b'\xe5\x90\x8d\xe7\xa7\xb0:\xe9\x95\xbf\xe5\xba\xa6\xe8\xb6\x85\xe8\xbf\x87\xe6\x8c\x87\xe5\xae\x9a\xe8\x8c\x83\xe5\x9b\xb4\xef\xbc\x81', b'unique': b'\xe5\x90\x8d\xe7\xa7\xb0: \xe5\xb7\xb2\xe7\xbb\x8f\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x81'}, help_text=b'\xe5\x90\x8d\xe7\xa7\xb0', max_length=200, unique=True)),
                ('api_url', models.CharField(help_text=b'salt-api url\xe5\x9c\xb0\xe5\x9d\x80', max_length=500)),
                ('username', models.CharField(blank=True, help_text=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d', max_length=200, null=True)),
                ('password', models.CharField(blank=True, help_text=b'\xe5\xaf\x86\xe7\xa0\x81', max_length=200, null=True)),
                ('eauth', models.CharField(blank=True, help_text=b'\xe7\x94\xa8\xe6\x88\xb7\xe7\xbb\x84', max_length=200, null=True)),
                ('self_minion_id', models.CharField(blank=True, help_text=b'\xe6\x9c\xac\xe8\xba\xab\xe4\xbd\x9c\xe4\xb8\xbaminion\xe7\x9a\x84id', max_length=200, null=True)),
                ('token', models.CharField(blank=True, help_text=b'\xe7\x99\xbb\xe5\xbd\x95\xe6\x88\x90\xe5\x8a\x9f\xe5\x90\x8e\xe8\x8e\xb7\xe5\x8f\x96\xe7\x9a\x84token', max_length=300, null=True)),
                ('description', models.CharField(blank=True, help_text=b'\xe5\xa4\x87\xe6\xb3\xa8', max_length=500, null=True)),
            ],
            options={
                'db_table': 'salt_master',
            },
        ),
        migrations.CreateModel(
            name='SaltMinion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('online', models.NullBooleanField(default=True, help_text=b'\xe5\x9c\xa8\xe7\xba\xbf\xe7\x8a\xb6\xe6\x80\x81')),
                ('monitor_ps', models.CharField(blank=True, default=b'0', help_text=b'\xe6\x98\xaf\xe5\x90\xa6\xe7\x9b\x91\xe6\x8e\xa7\xe8\xbf\x9b\xe7\xa8\x8b(0-\xe5\x85\xb3\xef\xbc\x8c1-\xe5\xbc\x80)', max_length=10, null=True)),
                ('minion_id', models.CharField(blank=True, help_text=b'minion\xe5\xae\xa2\xe6\x88\xb7\xe7\xab\xafid', max_length=255, null=True, unique=True)),
                ('host_name', models.CharField(blank=True, help_text=b'\xe4\xb8\xbb\xe6\x9c\xba\xe5\x90\x8d', max_length=500, null=True)),
                ('host_osarch', models.CharField(blank=True, help_text=b'\xe7\xb3\xbb\xe7\xbb\x9f\xe4\xbd\x8d\xe6\x95\xb0', max_length=100, null=True)),
                ('host_system', models.CharField(blank=True, help_text=b'\xe6\x93\x8d\xe4\xbd\x9c\xe7\xb3\xbb\xe7\xbb\x9f', max_length=500, null=True)),
                ('host_kernel', models.CharField(blank=True, help_text=b'\xe4\xb8\xbb\xe6\x9c\xba\xe5\x86\x85\xe6\xa0\xb8', max_length=500, null=True)),
                ('host_cpu_type', models.CharField(blank=True, help_text=b'CPU\xe7\xb1\xbb\xe5\x9e\x8b', max_length=500, null=True)),
                ('host_cpu_num', models.IntegerField(blank=True, help_text=b'CPU\xe6\x95\xb0\xe9\x87\x8f', null=True)),
                ('lan_ip', models.GenericIPAddressField(blank=True, help_text=b'\xe5\x86\x85\xe7\xbd\x91ip', null=True)),
                ('wan_ip', models.GenericIPAddressField(blank=True, help_text=b'\xe5\xa4\x96\xe7\xbd\x91ip', null=True)),
                ('host_mem_total', models.IntegerField(blank=True, help_text=b'\xe5\x86\x85\xe5\xad\x98\xe6\x80\xbb\xe9\x87\x8f', null=True)),
                ('module', models.ManyToManyField(blank=True, help_text=b'\xe6\x89\x80\xe5\xb1\x9e\xe6\xa8\xa1\xe5\x9d\x97', related_name='salt_minions', to='firstapp.Module')),
                ('salt_master', models.ForeignKey(blank=True, help_text=b'salt-master\xe6\x9c\x8d\xe5\x8a\xa1\xe7\xab\xaf', null=True, on_delete=django.db.models.deletion.CASCADE, to='firstapp.SaltMaster')),
            ],
            options={
                'db_table': 'salt_minion',
            },
        ),
        migrations.AddField(
            model_name='projectdockerinfo',
            name='salt_minion',
            field=models.ForeignKey(help_text=b'\xe4\xb8\xbb\xe6\x9c\xba\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8', on_delete=django.db.models.deletion.CASCADE, to='firstapp.SaltMinion'),
        ),
        migrations.AddField(
            model_name='projectdeployinfo',
            name='project_docker',
            field=models.ForeignKey(help_text=b'\xe9\xa1\xb9\xe7\x9b\xaeDocker\xe4\xbf\xa1\xe6\x81\xaf', on_delete=django.db.models.deletion.CASCADE, to='firstapp.ProjectDockerInfo'),
        ),
        migrations.AddField(
            model_name='projectcenter',
            name='deploy_salt_minion',
            field=models.ManyToManyField(blank=True, help_text=b'\xe9\x83\xa8\xe7\xbd\xb2\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8', to='firstapp.SaltMinion'),
        ),
        migrations.AddField(
            model_name='operationlog',
            name='salt_minion',
            field=models.ForeignKey(help_text=b'\xe6\x93\x8d\xe4\xbd\x9c\xe4\xb8\xbb\xe6\x9c\xba', on_delete=django.db.models.deletion.CASCADE, to='firstapp.SaltMinion'),
        ),
        migrations.AddField(
            model_name='hostps',
            name='salt_minion',
            field=models.ForeignKey(help_text=b'\xe4\xb8\xbb\xe6\x9c\xba', on_delete=django.db.models.deletion.CASCADE, to='firstapp.SaltMinion'),
        ),
        migrations.AddField(
            model_name='appinstallstatus',
            name='salt_minion',
            field=models.ForeignKey(help_text=b'salt-minion', on_delete=django.db.models.deletion.CASCADE, to='firstapp.SaltMinion'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups_profile',
            field=models.ManyToManyField(to='firstapp.GroupProfile'),
        ),
        migrations.AddField(
            model_name='user',
            name='parent_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
