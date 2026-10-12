from core.content_validation import load_content
from core.learning_tasks import sentence_cards, cloze, overview_choices, shuffled
from core.review_schedule import reviews_from_attempts


def test_tasks_cover_verified_models_without_losing_text():
    for e in load_content()[1]:
        if e['status']!='verified':continue
        cards=sentence_cards(e)
        assert len({c['id'] for c in cards})==len(cards)
        assert shuffled(cards,e['exercise_id'])!=cards
        paragraphs,blanks=cloze(e)
        assert blanks
        for (role,text),original in zip(paragraphs,e['paragraphs'].values()):
            for i,b in enumerate(blanks,1):text=text.replace(f'【{i}】',b['answer'])
            assert text==original
        correct,options=overview_choices(e)
        assert len(correct)>=1 and set(correct).issubset(options)


def test_flashcard_self_review_schedules():
    a=dict(exercise_id='q001',task_id='flash-intro',grading_type='flashcard',score=1,max_score=1,submitted_at='2026-10-12T10:00:00+07:00')
    r=reviews_from_attempts([a])['q001:flash-intro']
    assert r['next_review_date']=='2026-10-13'
    assert r['scheduling_basis']=='flashcard'
