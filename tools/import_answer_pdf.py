"""Import the user's 18 answers verbatim, normalizing PDF line wrapping only."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PARTS=('introduction','overview','body1','body2')

def normalize(text):
    # Preserve real hyphens (e.g. Sawn-Wood) broken at a PDF line boundary.
    text=re.sub(r'-\s*\n\s*(?=[A-Za-z])','-',text)
    return re.sub(r'\s+',' ',text).strip()

def extract(path):
    reader=PdfReader(path)
    lines=[]
    for page_no,page in enumerate(reader.pages,1):
        lines.extend((line.strip(),page_no) for line in page.extract_text().splitlines() if line.strip())
    starts=[i for i,(line,_) in enumerate(lines) if re.fullmatch(r'1\.\d+\.',line)]
    assert len(starts)==18
    lessons=[]
    for number,start in enumerate(starts,1):
        end=starts[number]-1 if number<len(starts) else len(lines)
        block=lines[start+1:end]
        first=next(i for i,(line,_) in enumerate(block) if re.match(r'^(?:Introduction|ntroduction)(?::|$)',line))
        heads=[first]
        for pattern in (r'^Overview(?::|$)',r'^Body 1(?:\s*\(|:)',r'^Body 2(?:\s*\(|:)'):
            heads.append(next(i for i in range(heads[-1]+1,len(block)) if re.match(pattern,block[i][0])))
        # Explanation begins with a Vietnamese heading, never part of the English essay.
        stop=next((i for i in range(heads[-1]+1,len(block)) if re.search(r'[À-ỹ]',block[i][0])),len(block))
        sections={}; labels={}
        for j,role in enumerate(PARTS):
            heading=block[heads[j]][0]
            boundary=heads[j+1] if j<3 else stop
            if j<2:
                match=re.match(r'^(?:Introduction|ntroduction|Overview):?\s*(.*)$',heading)
                inline=match[1]
                label=role.title()
            elif '):' in heading:
                label,inline=heading.rsplit('):',1)
                label+=')'
            else:
                label=heading;inline=''
            body=[inline]+[line for line,_ in block[heads[j]+1:boundary]]
            # A Vietnamese tip between introduction and overview is commentary.
            if role=='introduction':
                tip=next((i for i,line in enumerate(body) if re.search(r'[À-ỹ]',line)),len(body))
                body=body[:tip]
            sections[role]=normalize('\n'.join(body))
            labels[role]=label.strip()
            assert sections[role] and sections[role][-1] in '.!?', (number,role,sections[role])
            assert not re.search(r'[À-ỹ]',sections[role]),(number,role)
        pages=sorted({p for _,p in lines[start:end]})
        image=next((im for p in pages for im in reader.pages[p-1].images),None)
        assert image is not None,number
        lessons.append(dict(index=number,keywords=lines[start-1][0],paragraphs=sections,
            paragraph_titles=labels,pages=pages,analysis='\n'.join(t for t,_ in block[:first]),
            explanation='\n'.join(t for t,_ in block[stop:]),image=image))
    return lessons

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf',type=Path)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    lessons=extract(args.pdf)
    for l in lessons:
        print(l['index'],l['pages'],{k:len(v.split()) for k,v in l['paragraphs'].items()})
    if not args.write:return
    def read(name):return json.loads((ROOT/'content'/f'{name}.json').read_text(encoding='utf8'))
    def save(name,value):(ROOT/'content'/f'{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
    es=read('exercises'); bank=read('personal_bank'); tasks=read('learning_tasks')
    source=ROOT/'assets/reference/user-answers-current.pdf'
    shutil.copyfile(args.pdf,source)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    categories=['cot_lt4','cot_5plus','two_years','cot_4','cot_4','cot_5plus','two_years','cot_lt4','future','future','static','static','mixed','maps','maps','process','process','natural_process']
    for l,e,personal in zip(lessons,es,bank['lessons']):
        n=l['index']; paras=l['paragraphs']; im=l['image']
        asset=f'assets/personal/pdf-current-1-{n}{Path(im.name).suffix}'
        (ROOT/asset).write_bytes(im.data)
        # Source text is authoritative; previous authored explanations must not contradict it.
        notes={part:f"Theo mẫu PDF, mục 1.{n}, trang {', '.join(map(str,l['pages']))}. Xem phần giải thích cấu trúc nguyên văn bên dưới." for part in PARTS}
        outline=l['paragraph_titles']['body1']+'. '+l['paragraph_titles']['body2']
        e.update(category=categories[n-1],asset_reference=asset,source_sha256=hashlib.sha256(im.data).hexdigest(),
            content_version='2026-10-26.pdf-'+digest[:10],model_origin='user_pdf',verification_scope='source_transcription',
            source_filename=args.pdf.name,source_pdf_sha256=digest,source_pages=l['pages'],source_lesson_index=n,
            source_label='Mẫu nguyên văn PDF người dùng cung cấp',source_note='Giữ nguyên câu chữ của PDF; chỉ nối dòng do dàn trang. Ghi chú kiểm tra tách riêng, không thay đáp án. Nhãn band trong PDF là nhãn của tài liệu, không phải điểm web chấm.',
            transcription_policy='Nguyên văn PDF, chỉ chuẩn hóa khoảng trắng và nối từ bị ngắt dòng.',
            paragraphs=paras,paragraph_titles=l['paragraph_titles'],paragraph_notes=notes,sentence_notes=[],
            source_explanation_verbatim=l['explanation'],source_analysis_verbatim=l['keywords']+'\n'+l['analysis'],
            analysis_vi=l['analysis'] or l['keywords'],outline_vi=outline,
            prompt='Xem đề và số liệu trong ảnh gốc. Summarise the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.',
            checklist_vi=['Đối chiếu đúng bài và phần đã chọn.','Chép đúng câu chữ và dấu câu trong mẫu PDF.','Ghi chú kiểm tra là phần riêng, không thay đổi đáp án học thuộc.'])
        e['source_caveats']=[]
        intro_id='intro-count' if 'how many' in paras['introduction'] else 'intro-amount' if 'how much' in paras['introduction'] else 'intro'
        e['target_structure_ids']=[intro_id]+[s for s in e['target_structure_ids'] if not s.startswith('intro')]
        if n==3:e['source_caveats']=['PDF viết Handwriting ở School B tăng nhẹ, nhưng bảng cho 7% ở cả hai năm. Đáp án học thuộc vẫn giữ nguyên PDF.','Đơn vị là tỷ lệ %, còn how many thường diễn đạt số lượng.']
        if n==8:e['source_caveats']=['PDF dùng generally; biểu đồ cho Paper & Packaging cao nhất ở mọi mốc. Đáp án học thuộc giữ nguyên generally theo PDF.']
        e['quizzes']=[dict(quiz_id='source-overview',kind='single',prompt='Chọn overview nguyên văn trong PDF.',options=[paras['overview'],'Overall, all the figures remained unchanged.'],accepted_answers=[paras['overview']],explanation_vi='Đáp án nguyên văn mục 1.'+str(n)+'.'),dict(quiz_id='source-overall',kind='fill',prompt='Điền theo mẫu PDF: '+paras['overview'].replace('Overall','____',1),accepted_answers=['Overall'],explanation_vi='Overall mở đầu đoạn tổng quan trong mẫu.'),dict(quiz_id='source-outline',kind='single',prompt='Chọn dàn ý theo hai body của PDF.',options=[outline,'Body 1: ý kiến cá nhân. Body 2: nguyên nhân ngoài đề.'],accepted_answers=[outline],explanation_vi=outline)]
        personal.update(title=e['title'],keywords=l['keywords'],sections=paras,section_labels=l['paragraph_titles'],source_notes=l['explanation'].splitlines(),original_paragraphs=l['analysis'].splitlines(),image=asset,source_status='original_pdf_transcription')
        groups={l['paragraph_titles']['body1']:'body1',l['paragraph_titles']['body2']:'body2'}
        tasks[e['exercise_id']]={'grouping':{'instruction':'Phân loại theo tiêu đề hai đoạn thân bài trong PDF.','items':list(groups),'accepted_assignments':[groups]}}
    bank.update(source=str(source.relative_to(ROOT)).replace('\\','/'),source_sha256=digest)
    save('exercises',es);save('personal_bank',bank);save('learning_tasks',tasks)
    save('user_answer_source_20261020',dict(source_file=str(source.relative_to(ROOT)).replace('\\','/'),source_sha256=digest,transcription_policy='Nguyên văn PDF hiện tại; chỉ nối dòng.',lessons=[dict(exercise_id=e['exercise_id'],pages=e['source_pages'],paragraphs=e['paragraphs'],source_explanation_verbatim=e['source_explanation_verbatim']) for e in es],source_exercises=es))

if __name__=='__main__':main()


