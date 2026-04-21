"""
Management command: send_weekly_digest
───────────────────────────────────────
Schedule this on PythonAnywhere Tasks tab to run every Monday:
    python /home/YOUR_USERNAME/scorify/manage.py send_weekly_digest

It sends a personalised weekly stats email to every active user who
has an email address and uploaded at least one CV in the last 30 days.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Count

from roaster.models import CVAnalysis, UserProfile
from roaster.emails import send_weekly_digest


class Command(BaseCommand):
    help = 'Send weekly progress digest emails to active users'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Print stats without sending emails')

    def handle(self, *args, **options):
        dry_run  = options['dry_run']
        now      = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago= now - timedelta(days=30)

        # Only users active in last 30 days with a valid email
        active_user_ids = (
            CVAnalysis.objects
            .filter(created_at__gte=month_ago, user__isnull=False)
            .values_list('user_id', flat=True)
            .distinct()
        )
        users = User.objects.filter(
            id__in=active_user_ids,
            email__isnull=False,
        ).exclude(email='')

        sent = skipped = 0
        for user in users:
            try:
                week_analyses = CVAnalysis.objects.filter(
                    user=user,
                    created_at__gte=week_ago,
                    overall_score__isnull=False,
                )
                agg = week_analyses.aggregate(
                    best=Max('overall_score'),
                    avg=Avg('overall_score'),
                    count=Count('id'),
                )

                # Score trend: compare this week avg to previous week avg
                prev_week_start = week_ago - timedelta(days=7)
                prev_avg = (
                    CVAnalysis.objects
                    .filter(user=user, created_at__gte=prev_week_start, created_at__lt=week_ago,
                            overall_score__isnull=False)
                    .aggregate(avg=Avg('overall_score'))['avg']
                )
                if agg['avg'] and prev_avg:
                    trend = 'up' if agg['avg'] > prev_avg else ('down' if agg['avg'] < prev_avg else 'neutral')
                else:
                    trend = 'neutral'

                # Grab the most recent top fix
                last_analysis = CVAnalysis.objects.filter(user=user, overall_score__isnull=False).order_by('-created_at').first()
                top_fix = None
                if last_analysis and last_analysis.analysis_data:
                    fixes = last_analysis.analysis_data.get('top_fixes', [])
                    top_fix = fixes[0] if fixes else None

                total_all_time = CVAnalysis.objects.filter(user=user).count()

                stats = {
                    'uploads_this_week':    agg['count'],
                    'best_score_this_week': agg['best'],
                    'avg_score_this_week':  agg['avg'],
                    'score_trend':          trend,
                    'top_fix':              top_fix,
                    'total_all_time':       total_all_time,
                }

                if dry_run:
                    self.stdout.write(f"[DRY RUN] {user.email}: {stats}")
                else:
                    send_weekly_digest(user, stats)
                sent += 1

            except Exception as e:
                self.stderr.write(f"Error for {user.email}: {e}")
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Weekly digest {'simulated' if dry_run else 'sent'}: {sent} users, {skipped} skipped"
        ))
