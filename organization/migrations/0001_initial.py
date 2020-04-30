# Generated by Django 2.2.5 on 2020-01-23 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(blank=True, default='default_pic/organization.png', null=True, upload_to='pictures/organization')),
                ('name', models.CharField(max_length=128, verbose_name='Organization Name')),
                ('description', models.TextField(blank=True, max_length=280, null=True, verbose_name='Organization description')),
                ('articles', models.ManyToManyField(blank=True, to='content.Article')),
                ('head', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='head', to='account.Profile')),
                ('profiles', models.ManyToManyField(blank=True, to='account.Profile')),
                ('sub_org', models.ManyToManyField(blank=True, related_name='_organization_sub_org_+', to='organization.Organization')),
                ('tags', models.ManyToManyField(blank=True, to='content.Tag')),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=256, verbose_name='Post name')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='organization.Organization')),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
    ]