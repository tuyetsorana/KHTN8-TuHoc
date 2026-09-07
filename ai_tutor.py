import os
from typing import List, Dict

SYSTEM_PROMPT = """Bạn là "Bác học Newton & Marie Curie" — Cặp đôi Danh nhân Khoa học kiệt xuất, đồng hành làm Gia sư thông minh cho học sinh Khoa học Tự nhiên lớp 8 (Bộ sách "Kết nối tri thức với cuộc sống").

PHÂN VAI ĐẶC THÙ:
- Khi học sinh hỏi về HÓA HỌC (Phản ứng, Mol, Nồng độ dung dịch, Cân bằng PTHH, Tính theo PTHH, Axit, Bazơ...): Marie Curie sẽ ân cần, tỉ mỉ dẫn dắt.
- Khi học sinh hỏi về VẬT LÝ & HIỆN TƯỢNG TỰ NHIÊN (Khối lượng riêng, Áp suất, Lực đẩy Archimedes, Đòn bẩy, Nhiệt...): Isaac Newton uyên bác, sắc sảo dẫn dắt.
- Khi học sinh hỏi về SINH HỌC (Cơ thể người, các hệ cơ quan, phản ứng sinh lý...): Cả hai cùng kết hợp phân tích góc nhìn Hóa - Sinh - Lý.

PHƯƠNG PHÁP SƯ PHẠM SOCRATIC (GỢI MỞ TƯ DUY KHOA HỌC):
1. Tuyệt đối KHÔNG giải tuột đáp án hay kết quả cuối cùng ngay lập tức.
2. Dẫn dắt từng bước:
   - Bước 1: Hỏi học sinh về hiện tượng quan sát được hoặc công thức/định luật cốt lõi cần dùng.
   - Bước 2: Hướng dẫn học sinh thực hiện bước tính trung gian đầu tiên (ví dụ: đổi đơn vị, tính số mol n = m/M, xác định cánh tay đòn...).
   - Bước 3: Đặt câu hỏi gợi mở để học sinh tự tính nốt bước còn lại và rút ra kết luận.
3. QUY TẮC TRÌNH BÀY CÔNG THỨC & PTHH:
   - Tuyệt đối dùng KaTeX chuẩn.
   - Phương trình Hóa học KHÔNG được in nghiêng tên nguyên tố: Dùng \\mathrm{...} hoặc \\text{...}.
   - Ví dụ: $$\\mathrm{Fe} + 2\\mathrm{HCl} \\rightarrow \\mathrm{FeCl}_2 + \\mathrm{H}_2 \\uparrow$$
   - Khi có điều kiện nhiệt độ hoặc xúc tác: $$\\mathrm{CaCO}_3 \\xrightarrow{t^\\circ} \\mathrm{CaO} + \\mathrm{CO}_2 \\uparrow$$ hoặc $$2\\mathrm{KClO}_3 \\xrightarrow[\\mathrm{MnO}_2]{t^\\circ} 2\\mathrm{KCl} + 3\\mathrm{O}_2 \\uparrow$$
   - Công thức Vật lý: $$D = \\frac{m}{V}, \\quad p = d \\cdot h, \\quad F_A = d \\cdot V, \\quad F_1 \\cdot d_1 = F_2 \\cdot d_2$$
4. Giọng điệu truyền cảm hứng khám phá, gần gũi, ấm áp, khích lệ học sinh say mê khoa học thực nghiệm.
"""

def generate_tutor_response(
    api_key: str,
    lesson_title: str,
    lesson_summary: str,
    chat_history: List[Dict[str, str]],
    user_message: str,
    model_name: str = "gemini-3.8-flash"
) -> str:
    """
    Gửi yêu cầu tới Gemini API qua SDK google-genai (hỗ trợ Gemini 3.8 Flash, 3.7 Flash, 2.5 Flash)
    hoặc chuyển tiếp sang Offline Engine thông minh.
    """
    api_key = (api_key or "").strip()
    
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            
            # Xây dựng ngữ cảnh bài học
            prompt_context = f"=== BÀI HỌC KHTN 8 HIỆN TẠI: {lesson_title} ===\n"
            if lesson_summary:
                prompt_context += f"Tóm tắt kiến thức bài học:\n{lesson_summary[:1200]}\n\n"
                
            prompt_context += "Lịch sử trao đổi gần nhất:\n"
            for msg in chat_history[-4:]:
                sender = "Học sinh" if msg["role"] == "user" else "Bác học Newton & Marie Curie"
                prompt_context += f"{sender}: {msg['content']}\n"
                
            prompt_context += f"\nHọc sinh hỏi: {user_message}\n\nHãy phản hồi theo đúng phong cách Socratic gợi mở khoa học:"
            
            # Danh sách model ưu tiên từ thế hệ mới nhất 3.8, 3.7 đến các bản tiền nhiệm
            candidates = [model_name, "gemini-3.8-flash", "gemini-3.7-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
            models_to_try = []
            for c in candidates:
                if c and c not in models_to_try:
                    models_to_try.append(c)
            last_err = None
            
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt_context,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.7,
                        )
                    )
                    if response and response.text:
                        return response.text
                except Exception as ex:
                    last_err = ex
                    continue
                    
            if last_err:
                return f"⚠️ *Chưa thể kết nối Gemini API ({str(last_err)}). Bác học Newton & Marie Curie đang phản hồi ở chế độ Offline Socratic:*\n\n" + get_offline_response(lesson_title, user_message)
        except Exception as e:
            return f"⚠️ *Lỗi khởi tạo API ({str(e)}). Đang kích hoạt Chế độ Offline Socratic:*\n\n" + get_offline_response(lesson_title, user_message)
            
    # Chế độ Offline thông minh
    return get_offline_response(lesson_title, user_message)


def get_offline_response(lesson_title: str, user_message: str) -> str:
    """
    Chế độ Offline Socratic: Phân tích từ khóa để Bác học Newton hoặc Marie Curie gợi mở chuẩn xác.
    """
    msg = user_message.lower()
    tip = "\n\n💡 *(Mẹo: Hãy thêm `GEMINI_API_KEY` ở thanh bên trái để trò chuyện trực tiếp không giới hạn cùng Bác học Newton & Marie Curie nhé!)*"
    
    # 1. Cân bằng phương trình hoá học
    if any(k in msg for k in ["cân bằng", "can bang", "pthh", "phương trình"]):
        return (
            "👩‍🔬 **Marie Curie gợi ý cho em cách cân bằng Phương trình Hóa học nhé:**\n\n"
            "Để cân bằng một phản ứng, em hãy nhớ nguyên lý tối cao: **Số lượng nguyên tử của mỗi nguyên tố ở hai vế phải bằng nhau!**\n\n"
            "Em hãy thử áp dụng quy tắc 'Bội chung nhỏ nhất' theo 2 câu hỏi gợi ý này:\n"
            "1. Nguyên tố nào xuất hiện ít lần nhất nhưng có số nguyên tử lệch nhau nhiều nhất giữa hai vế? (Thông thường ta cân bằng kim loại trước $\\rightarrow$ phi kim $\\rightarrow$ $\\mathrm{H}$ $\\rightarrow$ và cuối cùng đếm lại $\\mathrm{O}$).\n"
            "2. Tuyệt đối **không được đổi chỉ số chân** (như $\\mathrm{O}_2, \\mathrm{H}_2\\mathrm{O}$), chỉ được thêm hệ số nguyên đứng trước công thức hoá học.\n\n"
            "👉 Em đang muốn cân bằng phản ứng cụ thể nào? Hãy viết các chất phản ứng và sản phẩm ra đây để cô Curie hướng dẫn từng bước nhé!"
        ) + tip

    # 2. Tính số mol / tính theo phương trình
    if any(k in msg for k in ["mol", "số mol", "tính theo pthh", "tính theo phương trình"]):
        return (
            "👩‍🔬 **Marie Curie đồng hành cùng em về bài toán Mol & Phương trình:**\n\n"
            "Muốn giải quyết bài toán tính theo phương trình hoá học, 'chìa khóa vàng' luôn là đưa mọi dữ kiện về **số mol ($n$)**:\n"
            "- Nếu đề cho khối lượng gam ($m$): Áp dụng $$n = \\frac{m}{M}$$\n"
            "- Nếu đề cho thể tích chất khí ở đkc ($25^\\circ\\mathrm{C}, 1\\mathrm{ bar}$): Áp dụng $$n = \\frac{V}{24{,}79}$$\n\n"
            "🔍 Sau khi có số mol rồi, em đã viết và cân bằng chính xác phương trình hoá học chưa? Hãy đối chiếu tỉ lệ hệ số để tìm số mol chất cần tính nhé!"
        ) + tip

    # 3. Nồng độ dung dịch C% và CM
    if any(k in msg for k in ["nồng độ", "nong do", "c%", "cm", "dung dịch"]):
        return (
            "👩‍🔬 **Marie Curie hướng dẫn em phân biệt hai loại nồng độ:**\n\n"
            "1. **Nồng độ phần trăm ($C\\%$):** Tỉ lệ khối lượng chất tan trong $100\\mathrm{ g}$ dung dịch:\n"
            "$$C\\% = \\frac{m_{\\text{ct}}}{m_{\\text{dd}}} \\cdot 100\\% \\quad (m_{\\text{dd}} = m_{\\text{ct}} + m_{\\text{nước}})$$\n"
            "2. **Nồng độ mol ($C_M$):** Số mol chất tan có trong $1\\mathrm{ L}$ dung dịch:\n"
            "$$C_M = \\frac{n}{V} \\quad (V \\text{ phải đổi ra lít!})$$\n\n"
            "👉 Đề bài của em đang yêu cầu tính $C\\%$ hay $C_M$? Em đã có đủ khối lượng chất tan và thể tích chưa?"
        ) + tip

    # 4. Hiện tượng tôi vôi sống
    if any(k in msg for k in ["vôi", "tôi vôi", "sôi", "cao"]):
        return (
            "👩‍🔬 **Marie Curie giải thích hiện tượng tôi vôi sôi sùng sục:**\n\n"
            "Khi cho vôi sống ($\\mathrm{CaO}$) vào nước, phản ứng hoá học xảy ra mãnh liệt:\n"
            "$$\\mathrm{CaO} + \\mathrm{H}_2\\mathrm{O} \\rightarrow \\mathrm{Ca(OH)}_2 + Q$$\n"
            "Đây là một **phản ứng toả nhiệt cực mạnh**. Nhiệt lượng tỏa ra đột ngột trong hố vôi làm nước xung quanh bị đun sôi tới $100^\\circ\\mathrm{C}$ và bốc hơi mù mịt!\n\n"
            "⚠️ *Lưu ý an toàn:* Nước vôi tôi vừa nóng vừa có tính kiềm ăn mòn cao, nên tuyệt đối không được đến gần miệng hố vôi đang tôi nhé!"
        ) + tip

    # 5. Khối lượng riêng D = m / V
    if any(k in msg for k in ["khối lượng riêng", "khoi luong rieng", "d ="]):
        return (
            "🍎 **Bác học Isaac Newton chào em! Ta cùng tìm hiểu về Khối lượng riêng:**\n\n"
            "Khối lượng riêng đặc trưng cho mức độ phân bố khối lượng của chất trong một đơn vị thể tích:\n"
            "$$D = \\frac{m}{V}$$\n"
            "- Nếu $m$ tính bằng $\\mathrm{kg}$, $V$ tính bằng $\\mathrm{m^3}$ thì $D$ có đơn vị $\\mathrm{kg/m^3}$.\n"
            "- Nhớ quy tắc đổi đơn vị: $1\\mathrm{ g/cm^3} = 1000\\mathrm{ kg/m^3}$.\n\n"
            "🔍 Em có biết tại sao một thanh sắt nặng $7800\\mathrm{ kg/m^3}$ lại chìm trong nước, còn dầu ăn $800\\mathrm{ kg/m^3}$ lại nổi lên trên không?"
        ) + tip

    # 6. Áp suất chất lỏng & Lặn sâu tức ngực
    if any(k in msg for k in ["áp suất", "ap suat", "tức ngực", "lặn", "lan"]):
        return (
            "🍎 **Bác học Isaac Newton giải thích hiện tượng thợ lặn bị tức ngực:**\n\n"
            "Trong lòng chất lỏng, áp suất tăng đều theo độ sâu theo công thức:\n"
            "$$p = d \\cdot h$$\n"
            "- Cứ lặn sâu thêm $10\\mathrm{ m}$, áp suất nước lại tăng thêm khoảng $100\\,000\\mathrm{ Pa}$ ($1\\mathrm{ atm}$).\n"
            "- Ở độ sâu $20 - 30\\mathrm{ m}$, áp suất ép lên toàn bộ bề mặt cơ thể gấp 3 đến 4 lần bình thường! Áp lực nước khổng lồ ép mạnh lên lồng ngực làm phổi bị nén thể tích, chèn ép tim gây tức ngực khó thở dữ dội.\n\n"
            "👉 Vì thế thợ lặn phải mặc bộ đồ lặn chịu áp lực cao và thở bình khí nén có van cân bằng áp suất đấy em ạ!"
        ) + tip

    # 7. Lực đẩy Archimedes
    if any(k in msg for k in ["archimedes", "ác-si-mét", "lực đẩy", "chìm", "nổi"]):
        return (
            "🍎 **Bác học Newton chia sẻ về phát hiện vĩ đại của tiền bối Archimedes:**\n\n"
            "Mọi vật nhúng trong chất lỏng đều được nâng đỡ bởi lực đẩy hướng thẳng đứng từ dưới lên:\n"
            "$$F_A = d \\cdot V$$\n"
            "Trong đó $V$ là **thể tích phần chất lỏng bị vật chiếm chỗ**.\n"
            "- Khi $F_A > P$ (hay $D_{\\text{chất lỏng}} > D_{\\text{vật}}$): Vật sẽ nổi lên.\n"
            "- Khi $F_A < P$ (hay $D_{\\text{chất lỏng}} < D_{\\text{vật}}$): Vật sẽ chìm xuống đáy.\n\n"
            "Em thử suy nghĩ xem: Con tàu thép nặng hàng vạn tấn tại sao lại nổi được trên mặt biển?"
        ) + tip

    # 8. Đòn bẩy
    if any(k in msg for k in ["đòn bẩy", "don bay", "cánh tay đòn", "moment"]):
        return (
            "🍎 **Bác học Newton hướng dẫn quy tắc đòn bẩy:**\n\n"
            "Đòn bẩy thăng bằng khi tích của lực với cánh tay đòn ở hai vế bằng nhau:\n"
            "$$F_1 \\cdot d_1 = F_2 \\cdot d_2 \\implies \\frac{F_2}{F_1} = \\frac{d_1}{d_2}$$\n"
            "Muốn được lợi về lực ($F_2 < F_1$), ta phải làm cho cánh tay đòn của tay người dài hơn ($d_2 > d_1$).\n\n"
            "🔍 Em hãy quan sát chiếc kìm nhổ đinh hay kéo cắt sắt: Điểm tựa ở đâu và cánh tay đòn nào dài hơn?"
        ) + tip

    # 9. Sinh học / Cơ thể người / Chuột rút
    if any(k in msg for k in ["cơ thể", "xương", "khớp", "chuột rút", "mỏi cơ"]):
        return (
            "🔬 **Bác học Newton & Marie Curie cùng phân tích sinh lý cơ thể người:**\n\n"
            "Cơ thể người là sự kết hợp hoàn hảo giữa cơ học (bộ xương và các đòn bẩy khớp) và hóa sinh (dẫn truyền xung thần kinh và năng lượng ATP):\n"
            "- Khi cơ co liên tục thiếu Oxygen, quá trình lên men sinh ra **Lactic acid** gây đau mỏi cơ.\n"
            "- Mất cân bằng các ion $\\mathrm{Ca}^{2+}, \\mathrm{Mg}^{2+}, \\mathrm{K}^+$ do toát mồ hôi sẽ kích hoạt cơn **chuột rút** co cứng cơ dữ dội.\n\n"
            "👉 Hãy nhớ khởi động kỹ trước khi bơi và bổ sung đủ nước khoáng điện giải nhé!"
        ) + tip

    # Mặc định
    return (
        f"Chào em! Bác học **Isaac Newton** và **Marie Curie** rất vui được đồng hành cùng em trong bài học **{lesson_title}**.\n\n"
        "Em đang gặp vướng mắc ở phần nào:\n"
        "1. Bản chất hiện tượng hay thí nghiệm thực tế?\n"
        "2. Công thức tính toán hay cân bằng phương trình hoá học?\n"
        "3. Hay phương pháp giải một bài tập cụ thể trong SGK?\n\n"
        "Hãy gõ câu hỏi hoặc phép tính em đang làm, chúng ta sẽ cùng từng bước tìm ra lời giải nhé!"
    ) + tip
