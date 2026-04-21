from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('',                      views.index,           name='index'),
    path('login/',                views.login_view,      name='login'),
    path('register/',             views.register_view,   name='register'),
    path('forgot-password/',      views.forgot_password_view, name='forgot_password'),
    path('logout/',               views.logout_view,     name='logout'),
    path('leaderboard/',          views.leaderboard_view,name='leaderboard'),
    path('blog/',                 views.blog_view,       name='blog'),
    path('blog/<slug:slug>/',     views.blog_post_view,  name='blog_post'),
    path('share/<uuid:card_id>/', views.share_view,      name='share_card'),

    # Auth user pages
    path('dashboard/',            views.dashboard,       name='dashboard'),
    path('profile/',              views.profile_view,    name='profile'),
    path('u/<str:username>/',     views.public_profile,  name='public_profile'),
    path('upgrade/',              views.upgrade_view,    name='upgrade'),
    path('payment/success/',      views.payment_success, name='payment_success'),
    path('paddle/webhook/',       views.paddle_webhook,  name='paddle_webhook'),
    path('compare/',              views.compare_view,    name='compare'),
    path('ats-optimizer/',        views.ats_optimizer_view, name='ats_optimizer'),
    path('cv-builder/',           views.cv_builder_view, name='cv_builder'),
    path('referral/',             views.referral_view,   name='referral'),

    # Auth APIs
    path('api/login/',                  views.login_submit,          name='login_submit'),
    path('api/register/set-password/',  views.register_set_password, name='register_set_password'),
    path('api/reset-password/',         views.reset_password_submit, name='reset_password_submit'),
    path('api/change-password/',        views.change_password_view,  name='change_password'),
    path('api/send-otp/',               views.send_otp,              name='send_otp'),
    path('api/verify-otp/',             views.verify_otp,            name='verify_otp'),
    path('api/onboarding-done/',        views.onboarding_done,       name='onboarding_done'),

    # CV APIs
    path('api/upload/',                          views.upload_cv,         name='upload_cv'),
    path('api/stats/',                           views.stats_view,        name='stats'),
    path('api/analysis/<uuid:analysis_id>/',     views.get_analysis,      name='get_analysis'),
    path('api/compare/',                         views.compare_submit,    name='compare_submit'),
    path('api/export/<uuid:analysis_id>/',       views.export_pdf,        name='export_pdf'),
    path('api/share/<uuid:analysis_id>/',        views.generate_share,    name='generate_share'),
    path('api/ats-optimizer/',                   views.ats_optimizer_submit, name='ats_optimizer_submit'),
    path('api/cv-builder/',                      views.cv_builder_submit, name='cv_builder_submit'),

    path('terms/',    views.terms_view,    name='terms'),
    path('privacy/',  views.privacy_view,  name='privacy'),
    path('refund/',   views.refund_view,   name='refund'),
]
