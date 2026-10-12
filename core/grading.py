"""Deterministic practice scores, never IELTS band estimates."""
import difflib
import math
import re
import unicodedata


def normalize(text, case_sensitive=False):
    value = ' '.join(unicodedata.normalize('NFKC', str(text)).split())
    return value if case_sensitive else value.casefold()


def memory_grade(answer, reference, case_sensitive=True, punctuation=True):
    def tokens(text):
        text = normalize(text, case_sensitive)
        return re.findall(r"\w+(?:['’]\w+)*|[^\w\s]", text) if punctuation else re.findall(r"\w+(?:['’]\w+)*", text)
    expected, actual = tokens(reference), tokens(answer)
    if not expected:
        raise ValueError('Không có mẫu để chấm.')
    # Levenshtein distance penalises insertions as well as omissions.
    previous = list(range(len(actual) + 1))
    for i, word in enumerate(expected, 1):
        current = [i]
        for j, entered in enumerate(actual, 1):
            current.append(min(current[-1]+1, previous[j]+1, previous[j-1]+(word != entered)))
        previous = current
    edits = previous[-1]
    score = round(100 * max(0, 1-edits/max(len(expected),len(actual),1)), 1)
    changes = []
    for operation, a,b,c,d in difflib.SequenceMatcher(None, expected, actual, autojunk=False).get_opcodes():
        if operation != 'equal':
            changes.append({'loại': {'replace':'khác mẫu','delete':'thiếu','insert':'thừa'}[operation],
                            'mẫu':' '.join(expected[a:b]), 'bạn viết':' '.join(actual[c:d])})
    return dict(score=score, max_score=100, grading_type='memory', outcome='matched' if edits == 0 else 'not_matched', changes=changes)


def grade_quiz(question, answer, status='verified'):
    if status != 'verified':
        return dict(score=None, max_score=None, grading_type='ungraded', outcome='needs_review')
    kind = question['kind']
    accepted = question['accepted_answers']
    if kind == 'multi':
        correct = set(answer) == set(accepted)
    elif kind == 'numeric':
        try:
            number = float(str(answer).replace(',', '').strip())
            correct = math.isfinite(number) and any(abs(number-float(x)) <= question.get('tolerance', 0) for x in accepted)
        except (ValueError, TypeError):
            correct = False
    elif kind == 'order':
        supplied = [x.strip() for x in answer.split(',')] if isinstance(answer,str) else answer
        correct = any(supplied == option for option in accepted)
    else:
        correct = normalize(answer) in [normalize(x) for x in accepted]
    outcome = 'correct' if correct else ('unconfirmed' if kind in ('fill','correction') else 'incorrect')
    return dict(score=int(correct), max_score=1, grading_type='quiz', outcome=outcome)


def word_count(text):
    return len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", text))
