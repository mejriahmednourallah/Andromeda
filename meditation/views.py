import json
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import FocusCategory, FocusSession


@login_required
def focus_timer_page(request):
    return render(request, 'meditation/focus.html')


@login_required
def get_categories(request):
    categories = FocusCategory.objects.all().values('id', 'name', 'color')
    categories_list = list(categories)
    if not categories_list:
        # Create default categories if none exist
        defaults = [
            {'name': 'Work', 'color': '#FF6B35'},
            {'name': 'Study', 'color': '#4CAF50'},
            {'name': 'Exercise', 'color': '#2196F3'},
            {'name': 'Reading', 'color': '#9C27B0'},
            {'name': 'Meditation', 'color': '#FF9800'},
        ]
        for cat_data in defaults:
            cat = FocusCategory.objects.create(**cat_data)
            categories_list.append({'id': cat.id, 'name': cat.name, 'color': cat.color})
    return JsonResponse({'categories': categories_list})


@login_required
@require_http_methods(["POST"])
def start_session(request):
    data = json.loads(request.body)
    category_id = data.get('category_id')

    # End any ongoing session first
    FocusSession.objects.filter(user=request.user, status='ongoing').update(
        status='completed',
        end_time=timezone.now()
    )

    session = FocusSession.objects.create(
        user=request.user,
        category_id=category_id,
        status='ongoing'
    )

    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'category': session.category.name if session.category else None
    })


@login_required
@require_http_methods(["POST"])
def pause_session(request, session_id):
    try:
        session = FocusSession.objects.get(id=session_id, user=request.user)
        session.status = 'paused'
        session.save()
        return JsonResponse({'success': True})
    except FocusSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def resume_session(request, session_id):
    try:
        session = FocusSession.objects.get(id=session_id, user=request.user)
        session.status = 'ongoing'
        session.save()
        return JsonResponse({'success': True})
    except FocusSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def complete_session(request, session_id):
    try:
        data = json.loads(request.body)
        session = FocusSession.objects.get(id=session_id, user=request.user)

        session.status = 'completed'
        session.end_time = timezone.now()
        session.notes = data.get('notes', '')

        duration = (session.end_time - session.start_time).total_seconds() / 60
        session.duration = int(duration)
        session.save()

        return JsonResponse({'success': True, 'duration': session.duration})
    except FocusSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


@login_required
def get_sessions(request):
    filter_type = request.GET.get('filter', 'today')
    sessions = FocusSession.objects.filter(user=request.user)
    now = timezone.now()
    if filter_type == 'today':
        sessions = sessions.filter(start_time__date=now.date())
    elif filter_type == 'week':
        week_ago = now - timedelta(days=7)
        sessions = sessions.filter(start_time__gte=week_ago)
    elif filter_type == 'month':
        month_ago = now - timedelta(days=30)
        sessions = sessions.filter(start_time__gte=month_ago)

    data = sessions.values('id', 'category__name', 'start_time', 'duration', 'status', 'notes')
    return JsonResponse({'sessions': list(data)})


@login_required
def get_stats(request):
    now = timezone.now()
    user = request.user

    today_sessions = FocusSession.objects.filter(user=user, start_time__date=now.date(), status='completed')
    today_minutes = sum(s.duration for s in today_sessions)

    week_ago = now - timedelta(days=7)
    week_sessions = FocusSession.objects.filter(user=user, start_time__gte=week_ago, status='completed')
    week_minutes = sum(s.duration for s in week_sessions)

    from django.db.models import Count
    favorite = FocusSession.objects.filter(user=user, status='completed').values('category__name').annotate(count=Count('id')).order_by('-count').first()

    return JsonResponse({
        'today_minutes': today_minutes,
        'today_sessions': today_sessions.count(),
        'week_minutes': week_minutes,
        'week_sessions': week_sessions.count(),
        'favorite_category': favorite['category__name'] if favorite else 'None'
    })
