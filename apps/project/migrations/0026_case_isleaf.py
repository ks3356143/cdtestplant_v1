# Generated by Django 4.2.9 on 2024-03-13 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0025_remove_problem_case_problem_case'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='isLeaf',
            field=models.BooleanField(default=True, help_text='树状图最后一个节点', verbose_name='树状图最后一个节点'),
        ),
    ]