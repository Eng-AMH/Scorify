from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('roaster', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # UserProfile — add new fields
        migrations.AddField(model_name='userprofile', name='onboarding_done',
            field=models.BooleanField(default=False)),
        migrations.AddField(model_name='userprofile', name='bonus_uploads',
            field=models.IntegerField(default=0)),

        # CVCache
        migrations.CreateModel(name='CVCache', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('cv_hash', models.CharField(db_index=True, max_length=64, unique=True)),
            ('plan', models.CharField(default='free', max_length=10)),
            ('analysis_data', models.JSONField()),
            ('hit_count', models.IntegerField(default=0)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ], options={'ordering': ['-created_at']}),

        # RateLimitRecord
        migrations.CreateModel(name='RateLimitRecord', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('ip', models.GenericIPAddressField(db_index=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ], options={'ordering': ['-created_at']}),

        # ReferralCode
        migrations.CreateModel(name='ReferralCode', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('code', models.CharField(db_index=True, max_length=12, unique=True)),
            ('total_referrals', models.IntegerField(default=0)),
            ('bonus_uploads_earned', models.IntegerField(default=0)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                related_name='referral_code', to='auth.user')),
        ]),

        # ReferralUse
        migrations.CreateModel(name='ReferralUse', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('referral_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                related_name='uses', to='roaster.referralcode')),
            ('referred_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                related_name='referred_by', to='auth.user')),
        ]),

        # ShareCard
        migrations.CreateModel(name='ShareCard', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
            ('is_public', models.BooleanField(default=True)),
            ('view_count', models.IntegerField(default=0)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                related_name='share_cards', to='roaster.cvanalysis')),
        ]),

        # BlogPost
        migrations.CreateModel(name='BlogPost', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('title', models.CharField(max_length=200)),
            ('slug', models.SlugField(blank=True, unique=True)),
            ('excerpt', models.TextField(blank=True, max_length=300)),
            ('content', models.TextField()),
            ('cover_image', models.ImageField(blank=True, null=True, upload_to='blog/')),
            ('tags', models.CharField(blank=True, max_length=200)),
            ('published', models.BooleanField(default=False)),
            ('view_count', models.IntegerField(default=0)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('author', models.ForeignKey(blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
        ], options={'ordering': ['-created_at']}),
    ]
