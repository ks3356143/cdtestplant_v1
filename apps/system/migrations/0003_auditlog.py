from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_securitypolicy'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, help_text='事件主体账号', max_length=50, null=True, verbose_name='主体账号')),
                ('role', models.CharField(blank=True, help_text='事件主体角色', max_length=30, null=True, verbose_name='主体角色')),
                ('event_type', models.CharField(help_text='EVENT_* 常量', max_length=40, verbose_name='事件类型')),
                ('detail', models.CharField(help_text='事件描述', max_length=500, verbose_name='事件内容')),
                ('success', models.BooleanField(default=True, help_text='成功/失败', verbose_name='操作结果')),
                ('ip', models.CharField(blank=True, help_text='操作IP', max_length=32, null=True, verbose_name='操作IP')),
                ('user_agent', models.CharField(blank=True, help_text='User-Agent', max_length=500, null=True, verbose_name='设备信息')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, blank=True, help_text='事件时间', null=True, verbose_name='事件时间')),
                ('actor', models.ForeignKey(blank=True, db_constraint=False, help_text='事件主体用户', null=True, on_delete=django.db.models.deletion.SET_NULL, related_query_name='audit_actor', to='user.users', verbose_name='主体用户')),
            ],
            options={
                'verbose_name': '统一审计日志',
                'verbose_name_plural': '统一审计日志',
                'db_table': 'system_audit_log',
                'ordering': ('-create_datetime',),
            },
        ),
    ]
