"""Escaped, inline comparison; differences are not grammar judgments."""
import difflib
import html
import re

def answer_diff_html(answer, reference, independent=False):
    pattern=r"\w+(?:['’]\w+)*|[^\w\s]"
    actual=list(re.finditer(pattern,answer))
    expected=list(re.finditer(pattern,reference))
    colors=('#9a3412','#ffedd5') if independent else ('#b91c1c','#fee2e2')
    chunks=[]; cursor=0
    for op,a,b,c,d in difflib.SequenceMatcher(None,[m[0] for m in expected],[m[0] for m in actual],autojunk=False).get_opcodes():
        start=actual[c].start() if c<len(actual) else len(answer)
        end=actual[d-1].end() if d>c else start
        chunks.append(html.escape(answer[cursor:start]))
        text=html.escape(answer[start:end])
        if op=='equal':chunks.append(text)
        elif op=='delete':
            missing=html.escape(reference[expected[a].start():expected[b-1].end()])
            label='Mẫu có' if independent else 'Thiếu'
            chunks.append(f'<mark style="color:{colors[0]};background:{colors[1]}">[{label}: {missing}]</mark>')
        else:
            label='Khác mẫu' if independent else ('Thừa' if op=='insert' else 'Khác mẫu')
            chunks.append(f'<mark title="{label}" style="color:{colors[0]};background:{colors[1]};text-decoration:underline">{text}</mark>')
        cursor=end
    chunks.append(html.escape(answer[cursor:]))
    return '<div style="white-space:pre-wrap;line-height:1.9">'+''.join(chunks)+'</div>'
