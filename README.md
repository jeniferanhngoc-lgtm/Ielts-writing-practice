# Học thuộc cấu trúc và bài mẫu

Giao diện chính chỉ có **Học cấu trúc** và **Học bài mẫu**. Mỗi lần học một khung hoặc một đoạn, theo ba bước **Xem mẫu → Điền khuyết → Tự viết lại**. Khung có ví dụ và giải thích; bài mẫu lấy từ tài liệu Word của bạn. Chọn **Cả bài** sau khi đã nhớ từng đoạn. Quiz, ChatGPT, thống kê và cài đặt được gom vào **Công cụ khác** trong thanh bên.

## Bộ học thuộc cá nhân mở rộng

Mục **Học thuộc bài của tôi** có 18 bài từ Word và 18 ảnh đề mã 1.1–1.18, kèm 8 dạng học: đọc hiểu, thẻ cấu trúc, điền khuyết, nhớ câu, sắp xếp câu, viết lại, quiz giải thích và hỏi ChatGPT (API tùy chọn). Xem [hướng dẫn chạy và cấu hình](PERSONAL_BANK_GUIDE.md). Bài gốc được giữ nguyên, có lưu ý lỗi nguồn trước khi luyện; điểm nhớ không phải band IELTS.

# IELTS Task 1 Studio

Ứng dụng Streamlit một người học, giao diện tiếng Việt. Học thuộc khung câu rồi vận dụng vào đề mới; có gia sư OpenAI API tùy chọn trong mục Học thuộc bài của tôi, không quy đổi điểm luyện tập thành band IELTS.

## Bản cập nhật: 5 chế độ luyện

Luyện tập có thêm **Ghép khung & kéo-thả**, **Điền khung cấu trúc**, **Dịch ngược — 3 cách**, **Quy trình 4 bước** và **Flashcard & ôn lại**. Đáp án hiển thị bằng văn bản, không còn dạng danh sách JSON/code.

Xem [UPDATE_GUIDE.md](UPDATE_GUIDE.md) để biết cách thay file, phạm vi chấm và kiểm tra sau triển khai. Phân loại chức năng câu tự động hiện có nhãn biên tập cho q014; các đề khác tự đối chiếu. Bộ gom nhóm theo dàn ý mẫu có cho 71 đề sẵn sàng.

## Nội dung hiện có

- Đã rà soát 100 ảnh: **71 đề có full bài, dàn ý, giải thích và quiz; 3 ảnh lặp; 26 ảnh cần xác nhận nguồn**. Xem [CONTENT_REVIEW.md](CONTENT_REVIEW.md).
- Mỗi bài sẵn sàng có 4 đoạn, ít nhất 150 từ, từ vựng thông dụng và thuật ngữ cần thiết theo hình.
- 17 cấu trúc đã chuẩn hóa theo PDF 52 trang. Các ví dụ là nội dung luyện tập biên soạn; không gắn band giám khảo.
- Hai chế độ: nhớ đúng mẫu (câu/đoạn/cả bài) và tự viết/đổi dữ liệu. Quiz có chọn overview, điền từ, sắp xếp mệnh đề, chọn dàn ý và đọc số liệu ở các đề có dữ liệu chắc chắn.
- Ngân hàng có cả bản ảnh trùng để truy vết; mục Luyện tập ẩn bản trùng và chặn chấm đề cần kiểm tra.

## Chạy trên Windows

Cần **Python 3.12** (Python 3.8 có sẵn trên máy không phù hợp bộ thư viện này).

```powershell
cd F:\Ielts_chatgpt\ielts_task1_trainer
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Trên máy hiện tại, môi trường `.venv` đã được tạo bằng Python 3.12 đi kèm Codex, thư viện đã cài. Có thể chạy trực tiếp:

```powershell
cd F:\Ielts_chatgpt\ielts_task1_trainer
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Hoặc chạy `start.ps1`. Mở địa chỉ localhost mà terminal hiển thị. Không đóng terminal trong lúc dùng.

## Cách học một buổi

1. Vào **Hôm nay**, bấm **Bắt đầu / Tiếp tục**.
2. Vào **Luyện tập**, chọn đề. Đọc ảnh, phần phân tích và dàn ý.
3. Chọn **Quiz** để đọc số liệu và điền từ. Mỗi câu có giải thích sau khi nộp.
4. Chọn **Học thuộc**, hiện mẫu để hiểu rồi ẩn mẫu và viết lại câu/đoạn. Nộp để xem từ thiếu, thừa hoặc khác mẫu. Thử lại tạo bản ghi mới.
5. Chọn **Vận dụng**, tự viết overview/body/bài hoàn chỉnh. Đây là bài mở, không chấm đúng/sai bằng so chuỗi. Bài đổi dữ liệu được ghi rõ là bổ sung tự tạo.
6. **Chữa bài & viết lại**: copy gói đề/bài, tự mở ChatGPT và đính kèm ảnh. Dán nhận xét về và lưu bản viết lại. Không có truyền dữ liệu tự động.
7. Trở lại **Hôm nay** để tạm dừng hoặc kết thúc buổi. Xem thống kê ở **Lịch sử & sổ lỗi**.

Điểm nhớ mẫu = 100 × (1 − khoảng cách chỉnh sửa token / độ dài token lớn hơn), chặn dưới ở 0. Token gồm từ và dấu câu. Mặc định phân biệt hoa/thường và dấu câu, bỏ qua khoảng trắng; có tùy chọn đổi quy tắc. Điểm 100 chỉ có nghĩa khớp mẫu. Câu khác mẫu vẫn có thể đúng tiếng Anh.

Quiz một lựa chọn: đúng được 1, không đúng được 0. Nhiều lựa chọn: phải đúng toàn bộ tập lựa chọn. Điền từ ngoài tập đáp án được ghi **chưa được xác nhận**, không kết luận mọi cách viết khác đều sai. Số gần đúng có sai số công bố trong câu hỏi. Xem mẫu không tạo lần làm bài.

## Lưu tiến độ

Sao chép `.streamlit/secrets.example.toml` thành `.streamlit/secrets.toml` và chọn một chế độ:

- `storage_mode = "demo"`: chỉ trong phiên. Cần xuất JSON trước khi đóng/tải lại trang.
- `storage_mode = "local"`: SQLite ở `private_data/progress.sqlite3`. Phù hợp máy cá nhân, đọc lại được ở phiên mới. **Máy hiện tại đã dùng chế độ này**.
- `storage_mode = "sheets"`: lưu Google Sheets. Cấu hình theo phần dưới.

Lịch sử dùng sự kiện append-only và UUID, không ghi đè các lần thử. Bài mẫu/đáp án tại thời điểm nộp cũng được lưu cùng phiên bản nội dung. Import JSON gộp theo UUID và từ chối nội dung khác có cùng ID.

Đồng hồ buổi học tính khoảng giữa bắt đầu và tạm dừng/kết thúc, kể cả khi chuyển trang hoặc để tab nền. Nó **không tự nhận biết bạn rời máy**. Thời gian trong lịch sử buổi chỉ được ghi khi kết thúc buổi. Nếu refresh/đóng phiên lúc đồng hồ đang chạy thì phần buổi chưa kết thúc chưa được lưu. Thời gian từng lần làm là khoảng mở bài đến nộp, có thể gồm thời gian rời trang; không cộng nó với thời gian buổi để tránh đếm đôi.

Lịch ôn dùng ngày `Asia/Ho_Chi_Minh`, sau các lần đúng liên tiếp là 1, 3, 7, 14 ngày; lần chưa đạt quay về 1 ngày. Chỉ quiz và nhớ mẫu tự lên lịch. Bài mở lưu tự đánh giá và nhận xét riêng. Ngày học theo lịch không đồng nghĩa ngày hoàn thành. Lịch 30 ngày là gợi ý; chưa có ngày thi của người học.

## Google Sheets

1. Tạo Google Cloud project và bật Google Sheets API cùng Google Drive API.
2. Tạo service account và khóa JSON trên máy của bạn. Không gửi khóa trong chat, không commit.
3. Tạo Google Sheet riêng, chia sẻ quyền **Editor** cho `client_email` của service account.
4. Điền `spreadsheet_id` và bảng `[gcp_service_account]` trong secrets; đổi chế độ thành `sheets`.
5. Khởi động lại Streamlit. Ứng dụng tạo tab `Events` nếu cần, đọc lịch sử và ghi sự kiện dưới dạng RAW text. Chuỗi dài chia thành các phần nhỏ để tránh giới hạn ô.
6. Thử nộp một bài, kết thúc buổi và tạo phiên trình duyệt mới. Chỉ coi kết nối hoàn tất khi phiên mới đọc lại đúng bản ghi. **Chưa thực hiện bước xác nhận trên tài khoản thật của bạn.**

Nếu Sheets lỗi, ứng dụng giữ bài trong phiên, báo chưa lưu và cho thử lại/xuất JSON. Giữ tab mở khi lỗi. UUID và chỉ số phần giúp retry sau timeout mà không nhân đôi dữ liệu theo ID. Đây là MVP một người học; không bảo đảm giao dịch nhiều người ghi đồng thời. Chuyển từ local sang Sheets bằng xuất/nhập JSON, không tự chuyển hoặc xóa lịch sử.

## Repo private và Streamlit Community Cloud

Repo: **[jeniferanhngoc-lgtm/Ielts-writing-practice](https://github.com/jeniferanhngoc-lgtm/Ielts-writing-practice)**. Đã kiểm tra cờ **private** qua GitHub API ngày 12/10/2026. Các ảnh nằm trong `assets/questions`, PDF tham khảo nằm trong `assets/reference`, theo yêu cầu lưu tài liệu vào repo private. Không công khai repo/tài liệu khi chưa xác nhận quyền chia sẻ.

- Chỉ push thư mục dự án này. `.gitignore` loại secrets, dữ liệu cá nhân, `.venv`, file tạm.
- Triển khai từ repo private lên Streamlit, entrypoint `app.py`, Python 3.12.
- Thêm secrets trong giao diện quản lý Streamlit; dùng `sheets` trên cloud.
- **Repo private không tự bảo đảm ứng dụng web private.** Kiểm tra quyền truy cập ứng dụng và chỉ cho người học truy cập trước khi đưa dữ liệu cá nhân vào.
- Không dùng SQLite trên máy chủ cloud để hứa lưu qua redeploy.
- Người dùng đã triển khai Streamlit Cloud. Kết nối Google Sheets thật cần cấu hình Secrets và kiểm tra trên tài khoản người dùng.

## Bổ sung nội dung

Ngân hàng chính ở `content/structures.json` và `content/exercises.json`. Nhập JSON trong **Cài đặt & dữ liệu** được kiểm tra schema, thêm vào phiên và có thể xuất lại. Tệp ảnh/PDF tải lên chỉ để xem; không tự tạo đáp án. CSV và biên tập đầy đủ qua biểu mẫu chưa có trong bản này.

Các bài nguồn biên soạn nằm ở `tools/corpus/`. `tools/build_content.py` là công cụ chạy offline để ráp ngân hàng; không có AI/API. Công cụ cần `tmp/inventory.json` và thư mục ảnh gốc cạnh dự án. Trong ứng dụng, **không cần chạy lại công cụ này** vì JSON và ảnh đã có sẵn. Không đặt verified cho đề còn mâu thuẫn. Sau sửa nội dung, tăng `content_version`.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Kiểm tra chấm bài, ôn lặp, múi giờ, pause/resume, SQLite qua phiên, schema, độ dài bài mẫu, dữ liệu dễ nhầm, Sheets giả lập timeout/chia ô, và luồng giao diện qua Streamlit AppTest. Kiểm thử Sheets giả lập không thay cho kiểm tra kết nối Google thực tế.

Tài liệu kỹ thuật: [Streamlit installation](https://docs.streamlit.io/get-started/installation/command-line), [gspread worksheet API](https://docs.gspread.org/en/latest/api/models/worksheet.html). Dependency đã kiểm tra và cài ngày 12/10/2026.

## Cập nhật giao diện

Luyện tập đặt đề bên trái và bài làm bên phải, mỗi khung cuộn riêng. Dữ liệu đề hiển thị bằng bảng thay vì JSON. Cài đặt dùng lịch chọn ngày thi và giữ lựa chọn khi chuyển trang. Hướng dẫn Google Cloud Console và mẫu Secrets có ngay trong Cài đặt & dữ liệu.


## Các dạng luyện tập mới

- Ghép nối khung bài: kéo-thả câu của toàn bài, phân loại vào introduction/overview/body 1/body 2; có lựa chọn bàn phím. Chấm theo bài mẫu, không kết luận các thứ tự khác đều sai tiếng Anh.
- Điền cấu trúc: toàn bài được đục lỗ tối đa bốn cụm mỗi đoạn, có chọn cụm hoặc gõ lại và gợi ý tiếng Việt.
- Dịch ngược: ba khung và ba câu tham khảo; dùng số liệu đầu–cuối của đề khi có dữ liệu phù hợp; các đề còn lại dùng ví dụ bổ sung có bảng/sơ đồ riêng và nhãn rõ ràng.
- Luyện bốn bước: introduction → hai ý overview → gom thẻ thông tin vào body → viết đoạn. Thời lượng 2/3/3/10 phút là gợi ý, không phải giới hạn nộp bài. Gom nhóm dùng dữ liệu biên tập trong content/learning_tasks.json; đề mới chưa có metadata sẽ chuyển sang tự đối chiếu.
- Flashcard: lọc theo dạng, lật xem cấu trúc và ví dụ, tự đánh giá để lên lịch 1–3–7–14 ngày. Không cộng điểm tự đánh giá vào độ chính xác quiz.
- Viết & học thuộc: giữ chức năng cũ. Checklist chỉ ở bài hoàn chỉnh, kiểm tra đủ trước khi ghi nhận lần nộp. Làm lại tạo checklist mới.

Các dạng mới lưu lịch sử bằng cùng kho local/Sheets đang cấu hình. Dạng luyện và kết quả được lưu riêng; chưa gửi bài thì không tạo lần làm.


## Giao diện học tập và kiểm tra

Trang chủ dùng thẻ nhiệm vụ và nút học/kiểm tra. Chuỗi ngày tính theo ngày có lần nộp; mục tiêu 5 lượt/ngày là gợi ý. Thư viện hiển thị khung, điều kiện, ví dụ và nút luyện hoặc kiểm tra câu ví dụ riêng. Bộ cốt lõi có Conversely; Maps, Process, Mixed chart có khung riêng.

Chế độ Ôn tập giữ năm dạng bài và gợi ý. Chế độ Kiểm tra độc lập hiện kiểm tra nhớ mẫu theo phần/cả bài: ẩn gợi ý, chỉ mở mẫu khi nộp, tùy chọn đếm ngược. Hết giờ vẫn giữ bản nháp và cho nộp với nhãn quá giờ. Đồng hồ bắt đầu khi bấm Bắt đầu làm bài; đổi tùy chọn sau đó không thay giới hạn của lượt đang làm.

Lần ôn có hỗ trợ được lưu nhưng không tăng lịch thành thạo; kiểm tra độc lập cập nhật lịch, flashcard vẫn dùng tự đánh giá. Dữ liệu cũ giữ cách tính trước cập nhật và có nhãn lịch sử cũ. Điểm chỉ đo khớp mẫu, không phải chấm ngữ pháp hay band IELTS. Bản nháp chưa nộp nằm trong phiên, không bảo đảm còn khi đóng/tải lại trình duyệt.


## Phân tích overview

Ôn tập → Phân tích & viết overview: ghi có/không thay đổi theo thời gian, xu hướng chung, cao/thấp nhất, thay đổi mạnh nhất, ổn định, xu hướng giống/ngược; chọn 2–3 ý rồi viết overview. Nhận xét được lưu dạng tự đối chiếu, không chấm so chuỗi. q085 có đáp án chi tiết tám mục; các đề khác đối chiếu phân tích, body và overview đã biên tập, chưa có đáp án đóng cho từng mục. Có thể ghi Không áp dụng với quy trình/bản đồ hoặc tiêu chí không có trong đề.

Ngày 13/10/2026 cập nhật 21 overview số liệu theo khung xu hướng + đặc điểm nổi bật, đồng bộ quiz và tăng phiên bản nội dung. Bản mẫu trong lịch sử cũ được giữ nguyên. Các overview bản đồ, quy trình và so sánh tĩnh giữ khung đúng loại đề. Meanwhile có thể nối bằng dấu chấm phẩy hoặc đứng đầu câu mới; consistently chỉ khi đúng tại mọi mốc, generally khi có ngoại lệ.


## Bộ khung người học chốt

Thư viện có 37 mục gồm khung chuẩn và khung nền giữ lại để tương thích lịch sử. Ưu tiên mục “Khung chuẩn đã chốt”; không cần học cả 37 ngay. Đã tách introduction đếm được/không đếm được/phần trăm, ba tình huống overview, năm phản xạ body, so sánh tĩnh, Maps, Process và Mixed chart. Luyện câu ví dụ, flashcard và gợi ý lấy cùng nguồn structures.json; structure_curriculum.json bảo toàn bộ khung khi chạy công cụ dựng nội dung.

Đợt này đồng bộ introduction mẫu của q010, q011, q014 và q090. Không thay hàng loạt mọi bài bằng cùng một câu hoặc ép dùng khung không phù hợp dữ liệu. Mẫu trong các lần làm cũ vẫn giữ nguyên. Màu cam nhận diện cụm cấu trúc, không xác nhận câu đúng ngữ pháp.
