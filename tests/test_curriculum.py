import json
from core.content_validation import ROOT,load_content
from core.learning import flashcards


def test_approved_curriculum_rebuild_source_and_flashcards_agree():
    structures,exercises=load_content()
    source=json.loads((ROOT/'content/structure_curriculum.json').read_text(encoding='utf8'))
    assert structures==source
    ids=[s['structure_id'] for s in structures]
    assert len(ids)==len(set(ids))
    byid={s['structure_id']:s for s in structures}
    for ident in ['intro-count','intro-amount','overview-all','overview-overtake','conversely','static-exceeds','map-links','process-purpose','mixed-intro']:
        card=next(c for c in flashcards(structures) if c['id']==ident)
        assert card['back']==byid[ident]['template']
        assert card['example']==byid[ident]['examples'][0]
    assert 'maps' not in byid['intro-count']['categories']
    assert 'in order to [verb]' in byid['process-purpose']['template']
    for e in exercises:
        if e['exercise_id'] in ('q014','q090'):
            assert 'how many' in e['paragraphs']['introduction']
            assert 'intro-count' in e['target_structure_ids']
