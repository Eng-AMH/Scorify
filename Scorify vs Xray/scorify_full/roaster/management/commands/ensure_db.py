"""
Management command: ensure_db
──────────────────────────────
Safely creates any missing tables without running full migrations.
Use this if migrate fails due to existing tables.
Run: python manage.py ensure_db
"""
from django.core.management.base import BaseCommand
from django.db import connection


TABLES_TO_CHECK = [
    ('roaster_cvcache', """
        CREATE TABLE IF NOT EXISTS "roaster_cvcache" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "cv_hash" varchar(64) NOT NULL UNIQUE,
            "plan" varchar(10) NOT NULL,
            "analysis_data" text NOT NULL CHECK ((JSON_VALID("analysis_data") OR "analysis_data" IS NULL)),
            "hit_count" integer NOT NULL,
            "created_at" datetime NOT NULL
        )"""),
    ('roaster_ratelimitrecord', """
        CREATE TABLE IF NOT EXISTS "roaster_ratelimitrecord" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "ip" char(39) NOT NULL,
            "created_at" datetime NOT NULL
        )"""),
    ('roaster_referralcode', """
        CREATE TABLE IF NOT EXISTS "roaster_referralcode" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "code" varchar(12) NOT NULL UNIQUE,
            "total_referrals" integer NOT NULL,
            "bonus_uploads_earned" integer NOT NULL,
            "created_at" datetime NOT NULL,
            "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id")
        )"""),
    ('roaster_referraluse', """
        CREATE TABLE IF NOT EXISTS "roaster_referraluse" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "referral_code_id" integer NOT NULL REFERENCES "roaster_referralcode" ("id"),
            "referred_user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id")
        )"""),
    ('roaster_sharecard', """
        CREATE TABLE IF NOT EXISTS "roaster_sharecard" (
            "id" char(32) NOT NULL PRIMARY KEY,
            "is_public" bool NOT NULL,
            "view_count" integer NOT NULL,
            "created_at" datetime NOT NULL,
            "analysis_id" char(32) NOT NULL REFERENCES "roaster_cvanalysis" ("id")
        )"""),
    ('roaster_blogpost', """
        CREATE TABLE IF NOT EXISTS "roaster_blogpost" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "title" varchar(200) NOT NULL,
            "slug" varchar(50) NOT NULL UNIQUE,
            "excerpt" varchar(300) NOT NULL,
            "content" text NOT NULL,
            "cover_image" varchar(100),
            "tags" varchar(200) NOT NULL,
            "published" bool NOT NULL,
            "view_count" integer NOT NULL,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "author_id" integer REFERENCES "auth_user" ("id")
        )"""),
]

COLUMNS_TO_ADD = [
    ('roaster_userprofile', 'onboarding_done', 'ALTER TABLE "roaster_userprofile" ADD COLUMN "onboarding_done" bool NOT NULL DEFAULT 0'),
    ('roaster_userprofile', 'bonus_uploads',   'ALTER TABLE "roaster_userprofile" ADD COLUMN "bonus_uploads" integer NOT NULL DEFAULT 0'),
]

INDEXES_TO_ADD = [
    ('roaster_cvcache', 'roaster_cvcache_cv_hash', 'CREATE INDEX IF NOT EXISTS "roaster_cvcache_cv_hash" ON "roaster_cvcache" ("cv_hash")'),
    ('roaster_ratelimitrecord', 'roaster_ratelimitrecord_ip', 'CREATE INDEX IF NOT EXISTS "roaster_ratelimitrecord_ip" ON "roaster_ratelimitrecord" ("ip")'),
]


class Command(BaseCommand):
    help = 'Safely create any missing tables and columns for v2 features'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            existing = {row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

            # Create missing tables
            for table, sql in TABLES_TO_CHECK:
                if table not in existing:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'  Created table: {table}'))
                else:
                    self.stdout.write(f'  OK (exists): {table}')

            # Add missing columns
            for table, col, sql in COLUMNS_TO_ADD:
                if table in existing:
                    cols = {row[1] for row in cursor.execute(f'PRAGMA table_info("{table}")').fetchall()}
                    if col not in cols:
                        try:
                            cursor.execute(sql)
                            self.stdout.write(self.style.SUCCESS(f'  Added column: {table}.{col}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'  Skip column {table}.{col}: {e}'))
                    else:
                        self.stdout.write(f'  OK (exists): {table}.{col}')

            # Create indexes
            for table, idx_name, sql in INDEXES_TO_ADD:
                try:
                    cursor.execute(sql)
                    self.stdout.write(f'  Index OK: {idx_name}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  Index skip: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database structure verified!'))
