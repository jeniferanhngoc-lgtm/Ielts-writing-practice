from datetime import date
import json
import uuid
import streamlit as st
from core.content_validation import CATEGORIES, ROOT, validate_exercise
from core.review_schedule import now, reviews_from_attempts
from core.timer import elapsed, start, pause
from core.export_prompt import make_prompt
from storage.store import merge_events
from ui.state import records, emit
from ui.readable import show_answer


def timer_panel():
    timer=st.session_state.timer
    st.metric('Thời gian buổi hiện tại',f'{int(elapsed(timer))//60:02}:{int(elapsed(timer))%60:02}')
    st.caption('Đồng hồ tính từ Bắt đầu đến Tạm dừng/Kết thúc; hãy tạm dừng khi rời máy. Bấm cập nhật để xem thời gian mới.')
    a,b,c,d=st.columns(4)
    if a.button('Bắt đầu / Tiếp tục',disabled=timer.get('running_since') is not None):
        if 'session_id' not in timer:
            timer.update(session_id=str(uuid.uuid4()),started_at=now().isoformat())
        start(timer); st.rerun()
    if b.button('Tạm dừng',disabled=timer.get('running_since') is None):
        pause(timer); st.rerun()
    if c.button('Kết thúc buổi',disabled='session_id' not in timer):
        pause(timer)
        emit('session',dict(session_id=timer['session_id'],started_at=timer['started_at'],ended_at=now().isoformat(),duration_seconds=round(timer['seconds']),completed=True),timer['session_id'])
        st.session_state.timer={'seconds':0,'running_since':None}; st.rerun()
    d.button('Cập nhật đồng hồ')


def today(exercises):
    st.title('Mỗi ngày, một bước tiến')
    st.write('IELTS Academic Writing Task 1 · học cấu trúc, hiểu dữ liệu, tự viết.')
    settings=st.session_state.settings
    days=max(1,(now().date()-date.fromisoformat(settings['start_date'])).days+1)
    a,b,c=st.columns(3)
    a.metric('Ngày theo lịch',days)
    b.metric('Mục tiêu mỗi ngày',f"{settings['daily_minutes']} phút")
    c.metric('Đề sẵn sàng học',sum(e['status']=='verified' for e in exercises))
    plan=json.loads((ROOT/'content/plan_30_days.json').read_text(encoding='utf-8'))
    row=plan[min(days,30)-1]
    st.info(f"Gợi ý ngày {min(days,30)}: {row['focus']} — {row['task']}")
    if now().weekday()==6 and not settings['sundays']:
        st.caption('Chủ nhật nghỉ theo cài đặt. Có thể ôn tự chọn; tiến độ không bị xóa.')
    st.markdown('**Buổi học đề xuất:** ôn cũ 5′ · đọc đề 5′ · viết câu 10′ · overview/body 10′ · sửa và viết lại 10′.')
    timer_panel()
    due=[r for r in reviews_from_attempts(records('attempt')).values() if r['next_review_date']<=now().date().isoformat()]
    st.subheader(f'Đến lịch ôn · {len(due)} bài nhỏ')
    if due:
        st.dataframe(due,hide_index=True,width='stretch')
    else:
        st.write('Chưa có bài đến hạn. Bắt đầu một quiz hoặc học một đoạn mẫu ở Luyện tập.')
    st.caption('Lịch 1–3–7–14 ngày dựa trên lần làm đã nộp. Mở trang/xem mẫu không tính là hoàn thành. Ngày bỏ lỡ giữ nguyên trong hàng ôn.')


def library(structures):
    st.title('Thư viện cấu trúc')
    st.write('Ít từ khó hơn. Dùng đúng cấu trúc, đúng ngữ cảnh.')
    category=st.selectbox('Lọc dạng bài',['all']+list(CATEGORIES),format_func=lambda x:'Tất cả' if x=='all' else CATEGORIES[x])
    role=st.selectbox('Chức năng',['all','introduction','overview','body'])
    for s in structures:
        if (category!='all' and category not in s['categories']) or (role!='all' and role!=s['paragraph_role']):
            continue
        with st.expander(f"{s['structure_id']} · {s['title']}"):
            st.write(s['explanation_vi']); st.caption(s['usage_conditions'])
            if st.checkbox('Hiện khung và ví dụ',key=s['structure_id']):
                st.info(s['template'])
                st.write(s['examples'][0])
            st.markdown('**Lỗi cần tránh**')
            show_answer(s['common_errors'])
            st.caption(s['source_reference']+' · '+s['editorial_note'])


def corrections(exercises,structures):
    st.title('Chữa bài & viết lại')
    attempts=[a for a in records('attempt') if a['grading_type'] in ['open','memory']]
    if not attempts:
        st.info('Nộp một bài viết ở Luyện tập trước.'); return
    byid={a['attempt_id']:a for a in attempts}
    selected=st.selectbox('Chọn lần làm',list(reversed(byid)),format_func=lambda ident:f"{byid[ident]['submitted_at'][:19]} · {byid[ident]['exercise_id']} · {byid[ident]['task_id']} · {ident[:8]}")
    a=byid[selected]
    e=next((e for e in exercises if e['exercise_id']==a['exercise_id']),None)
    if not e:
        st.warning('Không tìm thấy phiên bản đề này trong ngân hàng hiện tại.'); return
    prompt=make_prompt(e,a,structures)
    st.text_area('Chọn và copy nội dung sau sang ChatGPT',prompt,height=220)
    st.download_button('Tải gói chữa bài TXT',prompt,file_name=a['exercise_id']+'-chua-bai.txt')
    st.link_button('Mở ChatGPT', 'https://chatgpt.com/')
    st.caption('Tự dán nội dung và đính kèm ảnh đề. Ứng dụng không gửi hoặc lấy nhận xét tự động.')
    old=next((c for c in reversed(records('correction')) if c['attempt_id']==a['attempt_id']),{})
    with st.form('correction-'+a['attempt_id']):
        feedback=st.text_area('Nhận xét từ bên ngoài',old.get('external_feedback',''),height=160,max_chars=100000)
        tags=st.text_input('Lỗi cần nhớ (phân cách bằng dấu phẩy)',', '.join(old.get('error_tags',[])))
        rewritten=st.text_area('Bản viết lại',old.get('rewritten_answer',''),height=220,max_chars=20000)
        assessment=st.selectbox('Tự đánh giá',['Chưa chắc','Cần ôn lại','Đã hiểu và dùng được'])
        targets=st.multiselect('Tự xác nhận cấu trúc đã dùng',e['target_structure_ids'])
        submitted=st.form_submit_button('Lưu nhận xét và bản viết lại')
    if submitted:
        emit('correction',dict(correction_id=str(uuid.uuid4()),attempt_id=a['attempt_id'],exercise_id=e['exercise_id'],external_feedback=feedback,error_tags=[t.strip() for t in tags.split(',') if t.strip()],rewritten_answer=rewritten,self_review_state=assessment,target_structures_used=targets,status='rewritten' if rewritten.strip() else ('corrected' if feedback.strip() else 'not_corrected'),updated_at=now().isoformat()))
        st.success('Đã ghi nhận trong phiên. Trạng thái lưu lâu dài hiển thị ở cuối trang.')


def progress(exercises):
    st.title('Lịch sử & sổ lỗi')
    attempts=records('attempt'); sessions=records('session')
    quiz=[a for a in attempts if a['grading_type']=='quiz' and a['score'] is not None]
    seconds=sum(s['duration_seconds'] for s in sessions)
    a,b,c,d=st.columns(4)
    a.metric('Thời gian buổi đã kết thúc',f'{seconds//3600} giờ {(seconds%3600)//60} phút')
    b.metric('Buổi đã học',len(sessions))
    c.metric('Lần nộp bài',len(attempts))
    d.metric('Độ chính xác quiz',f"{100*sum(x['score'] for x in quiz)/sum(x['max_score'] for x in quiz):.0f}%" if quiz else '—')
    st.caption('Quiz tính trên mọi lần thử. Điểm nhớ mẫu, tự đánh giá và nhận xét được lưu riêng; không quy đổi band IELTS.')
    if attempts:
        st.dataframe([{k:a.get(k) for k in ['submitted_at','exercise_id','task_id','grading_type','score','max_score','duration_seconds','retry_of']} for a in reversed(attempts)],hide_index=True,width='stretch')
        byid={a['attempt_id']:a for a in attempts}
        selected=st.selectbox('Xem nội dung một lần làm',list(reversed(byid)),format_func=lambda ident:byid[ident]['submitted_at'][:19]+' · '+byid[ident]['exercise_id']+' · '+byid[ident]['task_id']+' · '+ident[:8])
        chosen=byid[selected]
        show_answer(chosen['answer'])
        with st.expander('Mẫu/đáp án tại thời điểm làm'):
            show_answer(chosen.get('reference_snapshot',''))
    if sessions:
        st.subheader('Thời gian từng buổi'); st.dataframe(sessions,hide_index=True,width='stretch')
    if records('correction'):
        st.subheader('Sổ lỗi và các lần viết lại')
        st.dataframe(records('correction'),hide_index=True,width='stretch')
    reviews=list(reviews_from_attempts(attempts).values())
    if reviews:
        st.subheader('Lịch ôn'); st.dataframe(reviews,hide_index=True,width='stretch')


def settings_page(structures,exercises):
    st.title('Cài đặt & dữ liệu')
    settings=st.session_state.settings
    with st.form('settings_form'):
        start_date=st.date_input('Ngày bắt đầu',date.fromisoformat(settings['start_date']))
        minutes=st.number_input('Phút mỗi ngày',10,180,int(settings['daily_minutes']),5)
        sundays=st.checkbox('Học cả Chủ nhật',settings['sundays'])
        meanings=['Chưa xác định','Đến ngày thi','Một đợt ôn 30 ngày']
        meaning=st.selectbox('Mốc 30 ngày là gì?',meanings,index=meanings.index(settings.get('target_meaning','Chưa xác định')))
        target_day=st.date_input('Ngày thi nếu đã biết',value=date.fromisoformat(settings['target_date']) if settings.get('target_date') else None)
        target=target_day.isoformat() if target_day else ''
        save=st.form_submit_button('Lưu cài đặt')
    if save:
        try:
            if target: date.fromisoformat(target)
            if target and date.fromisoformat(target)<start_date: raise ValueError()
        except ValueError:
            st.error('Ngày thi phải hợp lệ và không trước ngày bắt đầu.')
        else:
            settings=dict(settings,start_date=start_date.isoformat(),daily_minutes=minutes,sundays=sundays,target_date=target,target_meaning=meaning)
            emit('settings',settings); st.session_state.settings=settings
            st.success('Đã ghi nhận cài đặt trong phiên.')
    from ui.sheets_setup import sheets_panel
    sheets_panel()
    st.subheader('Sao lưu tiến độ')
    export={'schema_version':1,'exported_at':now().isoformat(),'events':st.session_state.events}
    st.download_button('Xuất toàn bộ tiến độ JSON',json.dumps(export,ensure_ascii=False,indent=2),file_name='ielts-progress-'+now().date().isoformat()+'.json',mime='application/json')
    backup=st.file_uploader('Khôi phục JSON tiến độ',type=['json'])
    if backup and st.button('Kiểm tra và nhập tiến độ'):
        try:
            data=json.loads(backup.getvalue())
            if data.get('schema_version')!=1: raise ValueError('Sai phiên bản sao lưu')
            merged=merge_events(st.session_state.events,data['events'])
            # Validate all before mutating; each UUID remains stable on retry.
            for event in merged:
                emit(event['kind'],event['data'],event['id'])
            restored=records('settings')
            if restored: st.session_state.settings=restored[-1]
            st.success('Đã nhập, không nhân đôi ID. Kiểm tra trạng thái lưu ở cuối trang.')
        except (ValueError,KeyError,TypeError) as exc:
            st.error(f'Không nhập: {exc}')
    st.subheader('Nhập nội dung đã biên tập')
    st.caption('JSON danh sách đề theo mẫu content/exercises.json. CSV chưa hỗ trợ trong bản này. Chỉ người biên tập mới nên đặt verified.')
    uploaded=st.file_uploader('Ngân hàng JSON',type=['json'],key='content_import')
    if uploaded and st.button('Kiểm tra và thêm vào phiên'):
        try:
            items=json.loads(uploaded.getvalue())
            if not isinstance(items,list): raise ValueError('Cần một danh sách đề')
            seen={e['exercise_id'] for e in exercises}
            for item in items:
                validate_exercise(item,{s['structure_id'] for s in structures})
                if item['exercise_id'] in seen: raise ValueError('Trùng ID đề')
                seen.add(item['exercise_id'])
            st.session_state.extra_exercises=st.session_state.get('extra_exercises',[])+items
            st.success('Đã thêm vào phiên. Xuất ngân hàng bên dưới để giữ nội dung.')
        except (ValueError,KeyError,TypeError) as exc:
            st.error(f'Không nhập: {exc}')
    st.download_button('Xuất ngân hàng nội dung JSON',json.dumps(exercises,ensure_ascii=False,indent=2),file_name='exercises.json',mime='application/json')
    asset=st.file_uploader('Xem đề mới (chưa có đáp án tự động)',type=['png','jpg','jpeg','pdf'])
    if asset:
        if asset.type!='application/pdf': st.image(asset)
        else: st.download_button('Tải / mở PDF',asset.getvalue(),file_name=asset.name)
        st.info('Tệp mới ở trạng thái draft. Cần biên tập dữ liệu, bài mẫu và đáp án trước khi đưa vào chế độ chấm.')
