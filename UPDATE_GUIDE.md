# Cập nhật 5 chế độ luyện Task 1

## Những gì đã thêm

Trong **Luyện tập → Cách luyện**, ngoài Học thuộc / Vận dụng / Quiz có:

1. **Ghép khung & kéo-thả**
   - Sắp xếp các câu của bài mẫu từ Introduction đến Body 2.
   - Phân loại theo vị trí đoạn.
   - Phân loại theo chức năng: introduction, overview, xu hướng, so sánh, cả hai hoặc thông tin khác.
   - Kéo-thả thực sự qua component cục bộ; có nút lên/xuống và danh sách chọn.
   - Có chế độ ô nhập dự phòng cho thiết bị không hỗ trợ kéo-thả.
   - Sắp xếp câu chấm mức khớp thứ tự mẫu, không kết luận mọi thứ tự khác đều sai logic.

2. **Điền khung cấu trúc**
   - Bài mẫu có các ô trống đánh số.
   - Chọn cụm từ hoặc gõ cụm từ theo gợi ý tiếng Việt.
   - Tối đa 4 ô mỗi đoạn để không dồn toàn bộ bài luyện vào đoạn đầu.
   - Sau nộp: xem câu trả lời, cụm mẫu và gợi ý.
   - Điểm là mức nhớ cụm mẫu, không phải band hay đánh giá mọi paraphrase hợp lệ.

3. **Dịch ngược — 3 cách**
   - Câu tiếng Việt + ba khung để viết cùng ý.
   - Nếu đề có chuỗi dữ liệu phù hợp, dùng đầu/cuối của dữ liệu đó.
   - 19 đề hiện có dữ liệu phù hợp cho bài dịch ngược đầu–cuối.
   - Các đề khác dùng bài bổ sung tự tạo có bảng/sơ đồ nhỏ, ghi rõ độc lập với ảnh đề bên trái.
   - Có mẫu riêng cho maps, process, natural process, future, static và mechanism.
   - Không tự chấm ngữ pháp: nộp đủ ba câu để mở ba mẫu đối chiếu.
   - Khi xuất sang ChatGPT, gói chữa bài chứa ngữ cảnh bài dịch ngược để tránh chấm theo nhầm ảnh đề.

4. **Quy trình 4 bước**
   - Mở bài: tự viết, đối chiếu.
   - Overview: chọn hai ý từ bài mẫu.
   - Gom nhóm: chọn Body 1/Body 2 theo chiến lược đã biên tập.
   - Viết overview và hai body; lưu riêng từng bước.
   - Có mục tiêu thời gian 2/3/3/10 phút; không ép hết giờ.
   - Có thể quay về bước trước, làm lại từng bước hoặc bắt đầu lượt mới.
   - 71 đề sẵn sàng học có bộ nhóm theo dàn ý mẫu. Bài nhập thêm chưa có metadata được tự đối chiếu thay vì tự đoán đáp án.

5. **Flashcard & ôn lại**
   - 17 thẻ cấu trúc + 4 thẻ về paraphrase, đạt đỉnh, number/amount/proportion và to/by.
   - Mặt trước không hiện công thức; lật thẻ mới thấy mẫu.
   - “Đã nhớ” / “Cần ôn lại” là tự đánh giá, không tính điểm quiz.
   - Lịch 1–3–7–14 ngày; thẻ xuất hiện trong lịch ôn ở Hôm nay.
   - Xem/lật thẻ không tính là hoàn thành.
   - Lưu qua cơ chế Events hiện có, không yêu cầu thêm tab Sheets hoặc API.

## Sửa lỗi hiển thị đáp án

Trước đây `st.write(list)` hiển thị danh sách như JSON có chỉ số, dấu ngoặc và nút/code.
Đã đổi đáp án quiz, mẫu trong lịch sử, bài nhiều câu và lỗi cần tránh sang văn bản/danh sách dễ đọc.
Quiz sắp xếp câu hiện thứ tự kèm nội dung câu, thay vì mảng mã “1, 2, 3”.
Khung cấu trúc cũng hiển thị như nội dung học, không dùng khối code.

## Phạm vi chấm cần biết

- Phân loại **vị trí đoạn** chấm được cho toàn bộ bài mẫu sẵn sàng.
- Phân loại **chức năng câu** có nhãn đã biên tập để chấm ở q014.
- Các đề khác vẫn làm được chức năng câu nhưng dùng tự đối chiếu, vì câu có thể có nhiều chức năng.
- Không dùng heuristic để tự gắn nhãn và coi đó là đáp án đúng.
- Có thể mở rộng nhãn trong `content/learning_tasks.json`.
- Các bài đóng theo bài mẫu đo mức khớp mẫu, không đo band IELTS.
- Không có AI, API key AI hay phụ thuộc kéo-thả mới cần cài.

## Cách cập nhật GitHub và Streamlit

1. Giải nén ZIP.
2. Trong repo GitHub hiện tại, thay các file đã sửa và thêm các file mới bên dưới.
3. Giữ đúng thư mục: `core/`, `ui/`, `content/`, `tests/`. Không upload ZIP làm mã nguồn.
4. Không tạo thêm một thư mục `Ielts-writing-practice-main` bao quanh `app.py` trong repo.
5. Commit thay đổi vào đúng branch mà Streamlit đang dùng.
6. Mở ứng dụng và kiểm tra phần Luyện tập. Nếu chưa nhận bản mới, dùng Reboot app trong quản lý Streamlit.
7. Giữ nguyên Secrets hiện có; bản này không cần đổi cấu hình Sheets.

File hiện có đã sửa:
- `ui/practice.py`
- `ui/screens.py`
- `core/review_schedule.py`
- `core/export_prompt.py`
- `README.md`

File mới:
- `core/learning.py`
- `ui/learning_modes.py`
- `ui/readable.py`
- `ui/drag_component.py`
- `ui/drag_frontend/index.html` — bắt buộc giữ nguyên vị trí.
- `content/learning_tasks.json`
- `tests/test_learning.py`
- `tests/test_drag_frontend.cjs`
- `UPDATE_GUIDE.md`

Không thay `content/exercises.json`, `content/structures.json`, ảnh đề hay PDF gốc.
Không thay secrets và không xóa lịch sử.
Nếu repo đã được chỉnh sau khi tải ZIP nguồn, đối chiếu các file sửa trước khi ghi đè.

## Kiểm tra nhanh sau triển khai

Chọn **q014**:
- Ghép khung → dùng kéo-thả; thử nút lên/xuống; nộp rồi làm lại.
- Phân loại → Chức năng câu → chọn hộp, nộp và xem bảng chữa.
- Điền khung → thử cả chọn cụm và gõ.
- Dịch ngược → nộp ba câu, xem mẫu có đúng số liệu Argentina.
- Quy trình → hoàn thành cả bốn bước.
- Flashcard → lật, chọn Đã nhớ, xem lịch ôn.
- Quiz cũ → nộp câu dàn ý; đáp án không còn xuất hiện kiểu JSON.
- Với Sheets đã cấu hình: mở phiên mới, kiểm tra lịch sử vẫn đọc được.
- Thử một maps/process để thấy bài dịch ngược bổ sung được gắn nhãn rõ.

## Kiểm thử đã thực hiện

- 23 kiểm thử Python: logic chấm, nội dung, lịch ôn, Sheets giả lập và luồng giao diện Streamlit AppTest.
- 2 kiểm thử JavaScript: nút sắp xếp, handler kéo-thả, phân loại, payload và render lại, bằng DOM giả lập.
- JavaScript đã kiểm tra cú pháp.
- Chưa kiểm tra thao tác chuột trong trình duyệt thật: môi trường kiểm tra không tải được Chromium.
- Chưa kiểm tra Google Sheets thật hoặc triển khai repo của người dùng.

Chạy kiểm tra:

```bash
python -m pytest -q
node --test tests/test_drag_frontend.cjs
```

Node chỉ cần cho kiểm thử JavaScript, không cần để chạy ứng dụng Streamlit.
