import copy
from datetime import datetime
import pytest
from core.grading import memory_grade, grade_quiz, word_count
from core.review_schedule import TZ, schedule, reviews_from_attempts
from core.timer import start, pause, elapsed
from core.content_validation import load_content,full_model,validate_exercise
from storage.store import LocalStore,merge_events


def test_memory_insert_delete_order_and_case():
    assert memory_grade('The  figure rose.','The figure rose.')['score']==100
    assert memory_grade('the figure rose.','The figure rose.')['score']<100
    assert memory_grade('the figure rose','The figure rose.',False,False)['score']==100
    for answer in ['The rose figure.','The figure.','The figure rose rose.','']:
        assert memory_grade(answer,'The figure rose.')['score']<100


def test_no_false_open_grading():
    quiz=dict(kind='fill',accepted_answers=['rose','increased'])
    assert grade_quiz(quiz,' INCREASED ')['score']==1
    assert grade_quiz(quiz,'went up')['outcome']=='unconfirmed'
    assert grade_quiz(quiz,'rose',status='draft')['score'] is None


def test_multi_numeric_and_order():
    assert grade_quiz(dict(kind='multi',accepted_answers=['a','b']),['b','a'])['score']==1
    assert grade_quiz(dict(kind='multi',accepted_answers=['a','b']),['a'])['score']==0
    q=dict(kind='numeric',accepted_answers=[58],tolerance=2)
    assert grade_quiz(q,'60')['score']==1
    assert grade_quiz(q,'61')['score']==0
    assert grade_quiz(q,'nan')['score']==0
    assert grade_quiz(dict(kind='order',accepted_answers=[['2','1']]),'2, 1')['score']==1


def test_review_intervals_and_vietnam_midnight():
    moment=datetime(2026,10,12,0,10,tzinfo=TZ)
    previous=None
    for delta in [1,3,7,14,14]:
        previous=schedule(previous,True,moment)
        assert (datetime.fromisoformat(previous['next_review_date']).date()-moment.date()).days==delta
    assert schedule(previous,False,moment)['next_review_date']=='2026-10-13'
    a=dict(exercise_id='q1',task_id='t',grading_type='quiz',score=1,max_score=1,submitted_at='2026-10-11T18:00:00+00:00')
    assert reviews_from_attempts([a])['q1:t']['next_review_date']=='2026-10-13'


def test_timer_pause_resume_not_double_counted():
    timer={'seconds':0,'running_since':None}
    start(timer,100); start(timer,110)
    assert elapsed(timer,120)==20
    pause(timer,130); pause(timer,180)
    assert elapsed(timer,200)==30
    start(timer,220); pause(timer,230)
    assert timer['seconds']==40


def test_store_idempotent_and_survives_new_instance(tmp_path):
    path=tmp_path/'progress.db'
    event={'id':'uuid','kind':'session','data':{'duration_seconds':42}}
    store=LocalStore(path); store.save(event); store.save(event)
    assert LocalStore(path).load()==[event]
    with pytest.raises(ValueError): store.save(dict(event,data={'duration_seconds':99}))
    assert merge_events([event],[event])==[event]
    with pytest.raises(ValueError): merge_events([event],[dict(event,data={})])


def test_all_content_has_models_and_valid_quizzes():
    structures,exercises=load_content()
    assert len(exercises)==100
    for e in exercises:
        if e['status']=='verified':
            assert word_count(full_model(e))>=150,e['exercise_id']
            assert len(e['quizzes'])>=5,e['exercise_id']
            assert len({q['quiz_id'] for q in e['quizzes']})==len(e['quizzes'])
            for q in e['quizzes']:
                answer=q['accepted_answers'][0] if q['kind']!='multi' else q['accepted_answers']
                assert grade_quiz(q,answer)['score']==1,(e['exercise_id'],q['quiz_id'])
        elif e['status']=='needs_review':
            assert e['review_reason']
    example=copy.deepcopy(next(e for e in exercises if e['status']=='verified'))
    example['asset_reference']='../secret.txt'
    with pytest.raises(ValueError): validate_exercise(example,{s['structure_id'] for s in structures})


def test_source_regressions():
    _,exercises=load_content(); byid={e['exercise_id']:e for e in exercises}
    assert byid['q014']['data']['Australia'][0]==452163
    assert byid['q014']['data']['years'][1]==2006
    assert byid['q090']['data']['years'][1]==2005
    assert byid['q017']['data']['timber']==[23,9,18,20,30]
    assert byid['q066']['data']['Korea'][0] is None
