from core.personal_bank import ROOT, load_bank, reference, sentences, cloze
from tools.import_personal_bank import extract_lessons, paragraphs


def test_import_preserves_source_and_all_images():
    lessons = load_bank()
    assert [x['id'] for x in lessons] == [f'1.{i}' for i in range(1, 19)]
    source = ROOT/'assets/reference/personal-answers.docx'
    rebuilt = extract_lessons(source, ROOT/'assets/personal')
    assert rebuilt == lessons
    source_lines = paragraphs(source)
    for lesson in lessons:
        assert (ROOT/lesson['image']).is_file()
        assert set(lesson['sections']) == {'introduction', 'overview', 'body1', 'body2'}
        for section in lesson['sections'].values():
            assert all(p in source_lines for p in section.split('\n\n'))
    # These essays have two paragraphs under Body 1; neither may be dropped.
    assert 'Similarly,' in lessons[8]['sections']['body1']
    assert 'Similarly,' in lessons[9]['sections']['body1']


def test_exercises_work_for_every_lesson_and_part():
    for lesson in load_bank():
        for part in ['introduction', 'overview', 'body1', 'body2', 'full']:
            text = reference(lesson, part)
            assert sentences(text)
            for hard in [False, True]:
                prompt, answers = cloze(text, hard)
                assert answers
                for i, answer in enumerate(answers, 1):
                    prompt = prompt.replace(f'【{i}】', answer)
                assert prompt == text
    assert sentences('It rose to 3.5 million. Then it fell.') == ['It rose to 3.5 million.', 'Then it fell.']
