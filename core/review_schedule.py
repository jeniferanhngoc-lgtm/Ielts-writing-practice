from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Asia/Ho_Chi_Minh')


def now():
    return datetime.now(TZ)


def schedule(previous, passed, moment=None, basis='quiz'):
    moment = moment or now()
    streak = min((previous or {}).get('streak', 0) + 1, 4) if passed else 0
    interval = [1, 1, 3, 7, 14][streak]
    return {'streak':streak, 'next_review_date':(moment.date()+timedelta(days=interval)).isoformat(),
            'last_review_at':moment.isoformat(), 'mastery_state':'reviewing' if passed else 'learning',
            'scheduling_basis':basis}


def reviews_from_attempts(attempts):
    reviews = {}
    for attempt in sorted(attempts, key=lambda a:a['submitted_at']):
        if attempt['grading_type'] not in ('quiz','memory','flashcard'):
            continue
        key = attempt['exercise_id'] + ':' + attempt['task_id']
        passed = (attempt.get('self_assessed_passed',False) if attempt['grading_type']=='flashcard'
                  else attempt['score'] == attempt['max_score'])
        reviews[key] = dict(schedule(reviews.get(key),passed,datetime.fromisoformat(attempt['submitted_at']).astimezone(TZ),attempt['grading_type']),exercise_id=attempt['exercise_id'],task_id=attempt['task_id'])
    return reviews
