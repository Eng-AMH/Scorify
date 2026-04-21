from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(choices=[('free','Free'),('pro','Pro'),('vip','VIP')], default='free', max_length=10)),
                ('pro_since', models.DateTimeField(blank=True, null=True)),
                ('pro_expires', models.DateTimeField(blank=True, null=True)),
                ('total_uploads', models.IntegerField(default=0)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('job_title', models.CharField(blank=True, max_length=100)),
                ('industry', models.CharField(blank=True, max_length=100)),
                ('bio', models.TextField(blank=True, max_length=300)),
                ('career_goal', models.CharField(blank=True, max_length=200)),
                ('skills_tags', models.TextField(blank=True)),
                ('best_score', models.IntegerField(default=0)),
                ('public_profile', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='CVAnalysis',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_key', models.CharField(blank=True, max_length=64, null=True)),
                ('original_filename', models.CharField(max_length=255)),
                ('overall_score', models.IntegerField(null=True)),
                ('verdict', models.CharField(blank=True, max_length=100)),
                ('analysis_data', models.JSONField(null=True)),
                ('is_preview', models.BooleanField(default=False)),
                ('plan_used', models.CharField(default='free', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('processing_time', models.FloatField(null=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analyses', to='auth.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField()),
                ('code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('pending_analysis_id', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
