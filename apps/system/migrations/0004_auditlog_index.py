from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_auditlog'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['create_datetime'], name='auditlog_time_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['event_type'], name='auditlog_type_idx'),
        ),
    ]
