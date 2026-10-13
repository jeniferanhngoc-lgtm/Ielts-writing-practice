import json
from datetime import datetime
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from core.content_validation import load_content, ROOT
from core.learning import (sentence_cards, sentences, shuffled, grade_order,
                          grade_categories, cloze_model, grade_cloze, overview_task,
                          reverse_task, grouping_grade, flashcards)
from core.review_schedule import reviews_from_attempts, TZ
from ui.readable import readable_text

def test_learning_content_and_closed_answers():
    structures,exercises=load_content()
    for e in exercises:
        if e['status']!='verified':continue
        cards=sentence_cards(e)
        assert ' '.join(c['text'] for c in cards)==' '.join(e['paragraphs'].values())
        assert grade_order(cards,[c['id'] for c in cards])==(len(cards),len(cards))
        with pytest.raises(ValueError):grade_order(cards,[cards[0]['id']]*len(cards))
        assert shuffled(cards,e['exercise_id'])!=cards
        assert shuffled(cards,e['exercise_id'])==shuffled(cards,e['exercise_id'])
        assert grade_categories(cards,{c['id']:c['role'] for c in cards})==(len(cards),len(cards))
        paras,blanks=cloze_model(e)
        assert blanks
        reconstructed=dict(paras)
        for b in reversed(blanks):
            reconstructed={r:t.replace('［'+b['id']+'］',b['answer']) for r,t in reconstructed.items()}
        assert reconstructed==e['paragraphs']
        assert grade_cloze(blanks,{b['id']:b['answer'].upper() for b in blanks})==(len(blanks),len(blanks))
        ov=overview_task(e)
        assert ov and len(set(ov['accepted_answers']))==2
        metadata=json.loads((ROOT/'content/learning_tasks.json').read_text(encoding='utf-8'))
        grouping=metadata[e['exercise_id']]['grouping']
        assert len(grouping['items'])==len(set(grouping['items']))
        assert grouping_grade(grouping,grouping['accepted_assignments'][0])==(1,1)
    assert len(flashcards(structures))==len(structures)+4
    assert sentences('It rose to 1.4 million. It then fell.')==['It rose to 1.4 million.','It then fell.']


def test_grouping_functions_reverse_and_flash_schedule():
    _,exercises=load_content()
    e=next(e for e in exercises if e['exercise_id']=='q014')
    meta=json.loads((ROOT/'content/learning_tasks.json').read_text(encoding='utf-8'))['q014']
    cards=sentence_cards(e)
    assert set(meta['sentence_functions'])==set(c['id'] for c in cards)
    for c in cards:c['accepted_functions']=meta['sentence_functions'][c['id']]
    assignment={c['id']:c['accepted_functions'][0] for c in cards}
    assert grade_categories(cards,assignment,True)==(len(cards),len(cards))
    g=meta['grouping']
    assert grouping_grade(g,g['accepted_assignments'][0])==(1,1)
    wrong=dict(g['accepted_assignments'][0]);wrong[g['items'][0]]='body2'
    assert grouping_grade(g,wrong)==(0,1)
    r=reverse_task(e)
    assert '235,088' in r['answers'][0] and '466,089' in r['answers'][0]
    a={'exercise_id':'flashcards','task_id':'flash-peak','grading_type':'flashcard',
       'score':None,'max_score':None,'submitted_at':'2026-10-12T20:00:00+07:00',
       'self_assessed_passed':True}
    assert reviews_from_attempts([a])['flashcards:flash-peak']['next_review_date']=='2026-10-13'
    a2=dict(a,submitted_at='2026-10-13T20:00:00+07:00')
    assert reviews_from_attempts([a,a2])['flashcards:flash-peak']['next_review_date']=='2026-10-16'
    a3=dict(a,submitted_at='2026-10-14T20:00:00+07:00',self_assessed_passed=False)
    assert reviews_from_attempts([a,a2,a3])['flashcards:flash-peak']['streak']==0
    assert readable_text(['One answer.'])=='One answer.'


def app(mode=None,exercise='q014'):
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
    at.secrets['storage_mode']='demo';at.run()
    at.sidebar.radio[0].set_value('Luyện tập').run()
    next(x for x in at.selectbox if x.label=='Chọn đề').set_value(exercise).run()
    if mode in ('Quiz','Học thuộc','Vận dụng'):
        next(x for x in at.selectbox if x.label=='Dạng luyện tập').set_value('Viết & học thuộc').run()
        next(x for x in at.radio if x.label=='Cách luyện').set_value(mode).run()
    elif mode:next(x for x in at.selectbox if x.label=='Dạng luyện tập').set_value(mode).run()
    assert not at.exception
    return at

def click(at,label):
    next(x for x in at.button if x.label==label).click().run()
    assert not at.exception


def test_all_modes_and_plain_quiz_answer():
    from ui.learning_modes import MODES
    at=app()
    for mode in MODES:
        next(x for x in at.selectbox if x.label=='Dạng luyện tập').set_value(mode).run()
        assert not at.exception,mode
    at=app('Quiz')
    next(x for x in at.radio if x.label=='Câu trả lời').set_value(
        next(e for e in load_content()[1] if e['exercise_id']=='q014')['quizzes'][0]['accepted_answers'][0])
    click(at,'Nộp bài')
    assert not at.get('json')
    assert any('Đáp án' in x.value for x in at.markdown)


def test_cloze_submit_retry_and_no_duplicate_rerun():
    at=app('Điền khung cấu trúc')
    e=next(e for e in load_content()[1] if e['exercise_id']=='q014')
    blanks=cloze_model(e)[1]
    for b in blanks:
        next(x for x in at.selectbox if x.label.startswith('Ô '+b['id']+' —')).set_value(b['answer'])
    click(at,'Chấm bài điền khung')
    assert at.session_state.events[-1]['data']['score']==len(blanks)
    count=len(at.session_state.events);at.run()
    assert len(at.session_state.events)==count
    click(at,'Làm lại bài này')
    assert any(x.label=='Chấm bài điền khung' for x in at.button)
    next(x for x in at.radio if x.label=='Cách điền').set_value('Gõ cụm từ').run()
    assert at.text_input


def test_category_fallback_and_order_validation():
    at=app('Ghép khung & kéo-thả')
    next(x for x in at.radio if x.label=='Cách thao tác').set_value('Chọn bằng ô nhập').run()
    click(at,'Chấm bài ghép khung')
    assert at.warning
    assert not at.session_state.events
    cards=sentence_cards(next(e for e in load_content()[1] if e['exercise_id']=='q014'))
    next(x for x in at.multiselect if x.label.startswith('Chọn các câu')).set_value([c['id'] for c in cards])
    click(at,'Chấm bài ghép khung')
    assert at.session_state.events[-1]['data']['score']==len(cards)
    next(x for x in at.radio if x.label=='Bài ghép khung').set_value('Phân loại câu').run()
    next(x for x in at.radio if x.label=='Cách thao tác').set_value('Chọn bằng ô nhập').run()
    for c in cards:
        next(x for x in at.selectbox if x.label==c['text']).set_value(c['role'])
    click(at,'Chấm bài ghép khung')
    assert at.session_state.events[-1]['data']['score']==len(cards)


def test_reverse_open_and_correction_export():
    at=app('Dịch ngược — 3 cách')
    for x in at.text_area:x.set_value('My alternative sentence.')
    click(at,'Nộp 3 câu và đối chiếu mẫu')
    attempt=at.session_state.events[-1]['data']
    assert attempt['grading_type']=='open' and attempt['score'] is None
    assert len(attempt['answer'])==3 and attempt['task_context']
    at.sidebar.radio[0].set_value('Chữa bài & viết lại').run()
    assert not at.exception
    assert 'Số liệu của' in at.text_area[0].value


def test_micro_all_four_steps():
    at=app('Quy trình 4 bước')
    at.text_area[0].set_value('The table compares car production in three countries.')
    click(at,'Nộp bước 1');click(at,'Sang bước tiếp theo')
    e=next(e for e in load_content()[1] if e['exercise_id']=='q014')
    next(x for x in at.multiselect if x.label=='Chọn đúng 2 nhận xét nổi bật').set_value(overview_task(e)['accepted_answers'])
    click(at,'Nộp bước 2');click(at,'Sang bước tiếp theo')
    g=json.loads((ROOT/'content/learning_tasks.json').read_text(encoding='utf-8'))['q014']['grouping']
    for name,role in g['accepted_assignments'][0].items():
        next(x for x in at.selectbox if x.label==name).set_value(role)
    click(at,'Nộp bước 3');click(at,'Sang bước tiếp theo')
    for x in at.text_area:x.set_value('A paragraph to compare with the reference.')
    click(at,'Nộp bước 4')
    assert len(at.session_state.events)==4
    assert any('hoàn thành 4 bước' in x.value for x in at.success)
    assert not at.get('json')
    click(at,'Bắt đầu lượt 4 bước mới')
    assert at.text_area
    assert len(at.session_state.events)==4


def test_flash_flip_is_not_completion_and_schedule_is_self_reported():
    at=app('Flashcard & ôn lại')
    assert not at.session_state.events
    click(at,'Lật thẻ — xem mặt sau')
    assert not at.session_state.events
    click(at,'Đã nhớ')
    a=at.session_state.events[-1]['data']
    assert a['grading_type']=='flashcard' and a['score'] is None
    assert a['self_assessed_passed']
    assert len(reviews_from_attempts([a]))==1
    count=len(at.session_state.events);at.run()
    assert len(at.session_state.events)==count
    at.sidebar.radio[0].set_value('Hôm nay').run()
    assert not at.exception
