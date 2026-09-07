# 🔬 KHOA HỌC TỰ NHIÊN 8 — TỰ HỌC THÔNG MINH (KẾT NỐI TRI THỨC)

> **Ứng dụng Web App Tự học Tương tác Thông minh** dành riêng cho môn Khoa học Tự nhiên lớp 8 (Bộ sách *Kết nối tri thức với cuộc sống*), tích hợp liên môn **Hóa học • Vật lý • Sinh học**, xây dựng trên nền tảng **Streamlit** và sẵn sàng triển khai toàn cầu trên **Streamlit Community Cloud**.

---

## 🌟 4 Đột Phá Sư Phạm Cốt Lõi Cho KHTN 8

1. **Chuẩn Hóa KaTeX Cho Phương Trình Hóa Học & Công Thức Vật Lý:**
   - Hóa học: Phương trình không bị in nghiêng tên nguyên tố, có mũi tên điều kiện nhiệt độ, xúc tác và trạng thái khí/kết tủa:
     $$\mathrm{Fe} + 2\mathrm{HCl} \rightarrow \mathrm{FeCl}_2 + \mathrm{H}_2 \uparrow$$
     $$2\mathrm{KClO}_3 \xrightarrow[\mathrm{MnO}_2]{t^\circ} 2\mathrm{KCl} + 3\mathrm{O}_2 \uparrow$$
   - Vật lý & Sinh học: Công thức chuẩn khối lượng riêng ($D = \frac{m}{V}$), áp suất ($p = d \cdot h$), lực đẩy Archimedes ($F_A = d \cdot V$), quy tắc đòn bẩy ($F_1 \cdot d_1 = F_2 \cdot d_2$).

2. **Tab 2 Sư Phạm: 🔬 Thí Nghiệm & Hiện Tượng Thực Tế:**
   - Chuyển đổi phương pháp giải trừu tượng thành việc khám phá thế giới thực nghiệm:
     - *Tại sao vôi sống gặp nước lại sôi sùng sục và tỏa nhiệt dữ dội?*
     - *Tại sao thợ lặn xuống sâu lại bị tức ngực và ù tai?*
     - *Tại sao mở lon nước ngọt có ga lại sủi bọt cuộn trào?*
     - *Tại sao con tàu thép vạn tấn nổi trên biển còn chiếc kim lại chìm?*
     - *Tại sao bị chuột rút khi bơi lội hoặc vận động thể thao mạnh?*
   - Cung cấp: Đặt vấn đề $\rightarrow$ Quan sát $\rightarrow$ Cơ chế phân tử / định luật vật lý $\rightarrow$ Ứng dụng & Cảnh báo an toàn.

3. **Kho Đa Phương Tiện Kép & Mô Phỏng Tương Tác PhET:**
   - **Video song hành:** Mỗi bài học trang bị cả Video bài giảng lý thuyết của giáo viên uy tín lẫn Clip quay thí nghiệm thực tế cận cảnh.
   - **Nhúng tương tác PhET Simulations (Đại học Colorado):** Học sinh thực hành kéo thả phân tử, cân bằng phương trình hóa học, thả chìm vật đo lực đẩy Archimedes, đo áp suất chất lỏng theo độ sâu ngay trên giao diện web app.

4. **Gia Sư AI Socratic — "Bác Học Newton & Marie Curie":**
   - **Marie Curie:** Chuyên gia Hóa học (hướng dẫn cân bằng PTHH, tính số mol $n = m/M = V/24{,}79$, nồng độ $C\%, C_M$).
   - **Isaac Newton:** Chuyên gia Vật lý & Cơ học (lực, áp suất, khối lượng riêng, đòn bẩy).
   - Phương pháp Socratic: Gợi mở tư duy từng bước, không giải tuột đáp án.
   - Hỗ trợ cả 2 chế độ: **Trực tuyến qua Google Gemini API thế hệ mới (Gemini 3.8 Flash & Gemini 3.7 Flash)** và **Smart Offline Engine** khi chưa có API Key.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Local

### 1. Yêu cầu môi trường
- Python 3.10 trở lên.
- Cài đặt các thư viện cần thiết:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Khởi chạy ứng dụng Web App
Từ thư mục `KHTN8-TuHoc`:
```bash
streamlit run app.py
```
Ứng dụng đã được cấu hình mặc định tại cổng riêng **8508** (để tránh xung đột với các ứng dụng khác đang chạy ở cổng 8501).
Truy cập tại địa chỉ: **`http://localhost:8508`**

---

## ☁️ Triển Khai Lên Streamlit Community Cloud

1. Đẩy mã nguồn thư mục `KHTN8-TuHoc` lên repository GitHub cá nhân (chế độ **Public**).
2. Truy cập [share.streamlit.io](https://share.streamlit.io) và đăng nhập bằng tài khoản GitHub.
3. Bấm **"New app"** $\rightarrow$ Chọn Repository $\rightarrow$ Branch `main` $\rightarrow$ Main file path: `app.py`.
4. *(Tùy chọn kết nối Gia sư AI toàn cầu)*: Vào **Advanced settings** $\rightarrow$ Thẻ **Secrets**, cấu hình:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   ```
5. Bấm **Deploy!** và chia sẻ đường link cho học sinh trải nghiệm.
