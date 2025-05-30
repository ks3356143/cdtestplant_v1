# Generated by Django 4.2.17 on 2024-12-13 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dict', '0005_remove_fragment_unique_name_belong_doc_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='fragment',
            name='unique_name_belong_doc',
        ),
        migrations.RemoveField(
            model_name='fragment',
            name='belong_doc',
        ),
        migrations.AddConstraint(
            model_name='fragment',
            constraint=models.UniqueConstraint(fields=('name', 'project_id'), name='unique_name'),
        ),
    ]
