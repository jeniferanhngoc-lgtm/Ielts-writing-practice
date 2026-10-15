# Học thuộc bài Task 1 từ tài liệu cá nhân

Giao diện mặc định có hai mục ở cột trái: **Học cấu trúc** và **Học thuộc bài**. Mọi lựa chọn dạng, bài và chế độ nằm trong cột trái; vùng chính dành cho câu hỏi hoặc bài viết.

**Học cấu trúc:** chọn bộ Biểu đồ, Maps hoặc Process rồi trả lời câu hỏi trắc nghiệm. Sau khi nộp có đáp án, khung hoàn chỉnh, ví dụ và giải thích. Bấm **Cấu trúc tiếp theo** để học tiếp.

**Học thuộc bài:** chọn **Ôn tập · Chép theo mẫu** để xem sẵn văn bản và chép vào ô nhập. Chọn **Luyện tập · Tự nhớ và viết** để ẩn mẫu đến khi nộp. Chọn dạng đề (line, bar, table, pie, mixed, maps, process, vòng đời), chọn một bài, rồi chọn Introduction/Overview/Body 1/Body 2 hoặc **Cả bài**. Bấm **Chọn bài ngẫu nhiên** để đổi sang bài khác trong dạng đang lọc; chọn **Tất cả** để lấy từ cả ngân hàng. Dạng chỉ có một bài sẽ không bật nút ngẫu nhiên.

Bấm **Chấm bài** để xem độ khớp và phần thiếu/thừa/khác mẫu, cùng bài đã viết và mẫu đối chiếu. Không phân biệt hoa/thường và dấu câu. Điểm là độ nhớ theo văn bản gốc, không phải điểm IELTS. Lượt chép mẫu và lượt luyện lại sau khi đã xem đáp án được ghi là có hỗ trợ. Tiến độ dùng cơ chế lưu của ứng dụng; mặc định demo chỉ giữ trong phiên. Ảnh đề và lưu ý nguồn nằm trong mục có thể mở khi cần.

Bộ bài lấy từ `dap an va bai lam .docx` và 18 ảnh trong `Quiz bank - task 1`, ghép theo mã 1.1–1.18. Toàn bộ văn bản gốc được giữ trong JSON và bản Word ở `assets/reference/personal-answers.docx`. Các chức năng mở rộng bên dưới vẫn ở **Công cụ khác → Học thuộc bài của tôi**. Lịch sử, cài đặt và sao lưu cũng nằm trong **Công cụ khác**.

## Các dạng học

| Dạng | Cách học |
| --- | --- |
| Đọc & hiểu bài | Xem ảnh đề, bốn đoạn bài mẫu, chức năng từng đoạn và giải thích nguồn. |
| Thẻ cấu trúc | Tự nhớ công thức rồi lật thẻ xem điều kiện sử dụng. |
| Điền khuyết | Điền cụm cấu trúc hoặc số liệu; chấm theo văn bản gốc. |
| Nhớ từng câu | Viết lại từng câu, có tùy chọn gợi ý chữ cái đầu. |
| Sắp xếp câu | Nhập thứ tự để dựng lại mạch bài mẫu. |
| Viết lại từ trí nhớ | Viết Introduction, Overview, Body hoặc cả bài; xem từ thiếu/thừa/khác mẫu. |
| Quiz & giải thích | Chọn đáp án về đoạn bài, tỷ lệ, từ nối, mức tăng và dự báo. |
| Hỏi ChatGPT | Sao chép prompt hoặc gửi bài kèm ảnh qua API để giải thích. |

Buổi học gợi ý 25 phút: 5 phút đọc hiểu → 5 phút thẻ/điền khuyết → 5 phút nhớ câu → 10 phút tự viết. Ôn theo lịch 1–3–7–14 ngày sau các lượt khớp hoàn toàn, quay về 1 ngày nếu chưa khớp. Lịch trong trang này dùng chung lịch sử và cơ chế lưu của ứng dụng. Xem gợi ý rồi ẩn lại vẫn được ghi là có hỗ trợ trong lượt đó. Nút **Bắt đầu lượt kiểm tra mới** mở lượt mới.

Điểm nhớ chỉ đo mức khớp văn bản, không đánh giá band hay khẳng định bài nguồn đúng. Các câu hỏi quiz về kiến thức là câu hỏi biên tập; 18 ảnh là ngân hàng đề gốc, không phải 18 câu trắc nghiệm đã OCR. Bài nguồn có lỗi hoặc chỗ chưa tự nhiên; lưu ý riêng được hiển thị trước khi luyện. Các bộ đề cũ được giữ nguyên.

## Chạy trên máy

Python 3.12 trở lên. Trong thư mục repository:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Để lưu tiến độ trên máy, tạo `.streamlit/secrets.toml` (đã được Git bỏ qua):

```toml
storage_mode = "local"
# Tùy chọn: chỉ cần khi dùng nút gửi API trực tiếp.
# OPENAI_API_KEY = "YOUR_API_KEY"
# OPENAI_MODEL = "gpt-4.1-mini"
```

Mặc định là demo: tiến độ chỉ trong phiên. Có thể xuất/nhập JSON ở **Cài đặt & dữ liệu**. Khi triển khai Cloud, dùng cấu hình Google Sheets đã có để giữ tiến độ qua redeploy. Ứng dụng dành cho một người học, chưa có hệ thống tài khoản.

## Đưa lên Streamlit Community Cloud

Chọn repository `jeniferanhngoc-lgtm/Ielts-writing-practice`, branch `main`, entrypoint `app.py`. Trong Settings → Secrets, cấu hình `storage_mode` và API key nếu dùng. Không commit key hoặc tệp tiến độ. Chọn model có quyền truy cập trên tài khoản API của bạn. API chỉ được gọi khi bấm nút gửi; bài viết, câu hỏi và ảnh đề được gửi trong lần gọi đó. Key nhập trên giao diện không ghi vào SQLite/Sheets/JSON. Không sử dụng thông báo lỗi API nguyên văn để tránh lộ dữ liệu nhạy cảm.

API được triển khai theo [OpenAI Python quickstart](https://developers.openai.com/api/docs/quickstart) với Responses API; gọi với `store=False`. Kiểm thử giao diện dùng [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest). API có thể tính phí riêng; chưa có khóa API thì toàn bộ phần học offline và xuất prompt vẫn hoạt động.

## Cập nhật tài liệu nguồn

```powershell
python tools/import_personal_bank.py --docx "D:\Ielts_chatgpt\dap an va bai lam .docx" --images "D:\Ielts_chatgpt\Quiz bank - task 1"
```

Importer kiểm tra đủ 18 mã và bốn đoạn mỗi bài, giữ nguyên câu chữ, nhập ảnh và lưu SHA-256 của Word. Sau khi thay cấu trúc tài liệu, chạy kiểm thử để phát hiện đoạn bị bỏ sót. Sửa lời giải học tập nên ghi rõ bản biên tập thay vì sửa âm thầm nguồn gốc.

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
