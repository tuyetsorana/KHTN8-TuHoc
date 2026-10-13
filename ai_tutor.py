import os
import time
from typing import List, Dict, Generator, Union

SYSTEM_PROMPT = """Bạn là "Bác học Newton & Marie Curie" — Cặp đôi Danh nhân Khoa học kiệt xuất, đồng hành làm Gia sư thông minh cho học sinh Khoa học Tự nhiên lớp 8 (Bộ sách "Kết nối tri thức với cuộc sống").

PHÂN VAI ĐẶC THÙ:
- Khi học sinh hỏi về HÓA HỌC (Phản ứng, Mol, Nồng độ dung dịch, Cân bằng PTHH, Tính theo PTHH, Axit, Bazơ...): Marie Curie sẽ ân cần, tỉ mỉ dẫn dắt. Xưng hô: "Cô Marie Curie" và "em".
- Khi học sinh hỏi về VẬT LÝ & HIỆN TƯỢNG TỰ NHIÊN (Khối lượng riêng, Áp suất, Lực đẩy Archimedes, Đòn bẩy, Nhiệt...): Isaac Newton uyên bác, sắc sảo dẫn dắt. Xưng hô: "Thầy Isaac Newton" và "em".
- Khi học sinh hỏi về SINH HỌC (Cơ thể người, các hệ cơ quan, phản ứng sinh lý...): Cả hai cùng kết hợp phân tích góc nhìn Hóa - Sinh - Lý.

PHƯƠNG PHÁP SƯ PHẠM SOCRATIC (GỢI MỞ TƯ DUY KHOA HỌC):
1. Tuyệt đối KHÔNG giải tuột đáp án hay toàn bộ kết quả ngay lập tức.
2. Dẫn dắt từng bước:
   - Khi học sinh trả lời câu hỏi trước đó: Hãy KHEN NGỢI nếu đúng, hoặc sửa chữa nhẹ nhàng nếu chưa chính xác, rồi lập tức hướng dẫn bước tiếp theo.
   - Luôn đặt 1 - 2 câu hỏi gợi mở cụ thể, dễ trả lời ở cuối mỗi tin nhắn để học sinh phản hồi tiếp.
3. QUY TẮC TRÌNH BÀY CÔNG THỨC & PTHH:
   - Dùng KaTeX chuẩn.
   - Phương trình Hóa học KHÔNG được in nghiêng tên nguyên tố: Dùng \\mathrm{...} hoặc \\text{...}.
   - Ví dụ: $$\\mathrm{Fe} + 2\\mathrm{HCl} \\rightarrow \\mathrm{FeCl}_2 + \\mathrm{H}_2 \\uparrow$$
   - Khi có điều kiện: $$\\mathrm{CaCO}_3 \\xrightarrow{t^\\circ} \\mathrm{CaO} + \\mathrm{CO}_2 \\uparrow$$
   - Công thức Vật lý: $$D = \\frac{m}{V}, \\quad p = d \\cdot h, \\quad F_A = d \\cdot V, \\quad F_1 \\cdot d_1 = F_2 \\cdot d_2$$
4. Giọng điệu ấm áp, hào hứng, khen ngợi sự tò mò của học sinh, khích lệ các em tự tay tìm ra đáp án.
"""

# Các mô hình ổn định và phản hồi siêu tốc nhất của Google Gemini
FAST_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro"]

def generate_tutor_stream(
    api_key: str,
    lesson_title: str,
    lesson_summary: str,
    chat_history: List[Dict[str, str]],
    user_message: str,
    model_name: str = "gemini-2.5-flash",
    character: str = "all"
) -> Generator[str, None, None]:
    """
    Generator phát trực tiếp (streaming) từng token giúp học sinh nhận phản hồi NGAY LẬP TỨC (< 0.5s).
    """
    api_key = (api_key or "").strip()
    
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            
            # Tùy biến prompt theo nhân vật được chọn
            char_instruction = ""
            if character == "curie":
                char_instruction = "\nEm đang đối thoại trực tiếp với CÔ MARIE CURIE. Bạn hãy đóng vai Cô Marie Curie (xưng 'Cô Curie' và gọi 'em'), chuyên sâu về Hóa học, phản ứng, cân bằng PTHH và bài toán mol với giọng điệu ân cần, khích lệ."
            elif character == "newton":
                char_instruction = "\nEm đang đối thoại trực tiếp với THẦY ISAAC NEWTON. Bạn hãy đóng vai Thầy Newton (xưng 'Thầy Newton' và gọi 'em'), chuyên sâu về Vật lý, lực, áp suất, cơ học và tư duy logic với giọng điệu uyên bác, truyền cảm hứng."
                
            prompt_context = f"=== BÀI HỌC KHTN 8 HIỆN TẠI: {lesson_title} ===\n"
            if lesson_summary:
                prompt_context += f"Tóm tắt kiến thức bài học:\n{lesson_summary[:1000]}\n\n"
                
            prompt_context += "Lịch sử cuộc đối thoại gần nhất giữa Thầy/Cô và Học sinh:\n"
            for msg in chat_history[-6:]:
                sender = "Học sinh" if msg["role"] == "user" else "Bác học"
                prompt_context += f"{sender}: {msg['content']}\n"
                
            prompt_context += f"\nHọc sinh vừa trả lời/hỏi: {user_message}\n\nHãy phản hồi theo đúng phong cách Socratic (nhận xét câu trả lời của học sinh, dẫn dắt bước tiếp theo và đặt câu hỏi gợi mở):"
            
            # Ưu tiên các model siêu tốc, loại bỏ model lỗi
            models_to_try = []
            if model_name and not any(err in model_name for err in ["3.8", "3.7"]):
                models_to_try.append(model_name)
            for m in FAST_MODELS:
                if m not in models_to_try:
                    models_to_try.append(m)
                    
            for m in models_to_try:
                try:
                    response_stream = client.models.generate_content_stream(
                        model=m,
                        contents=prompt_context,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT + char_instruction,
                            temperature=0.7,
                        )
                    )
                    got_chunk = False
                    for chunk in response_stream:
                        if chunk and chunk.text:
                            got_chunk = True
                            yield chunk.text
                    if got_chunk:
                        return
                except Exception:
                    continue
        except Exception:
            pass

    # Nếu không có API key hoặc kết nối lỗi: Dùng Smart Offline Engine chạy streaming giả lập cực mượt
    offline_text = get_offline_response(lesson_title, user_message, character=character)
    words = offline_text.split(" ")
    for idx, w in enumerate(words):
        yield w + (" " if idx < len(words) - 1 else "")
        time.sleep(0.015)


def generate_tutor_response(
    api_key: str,
    lesson_title: str,
    lesson_summary: str,
    chat_history: List[Dict[str, str]],
    user_message: str,
    model_name: str = "gemini-2.5-flash",
    character: str = "all"
) -> str:
    """Trả về toàn bộ văn bản (dành cho chế độ không streaming)."""
    chunks = list(generate_tutor_stream(
        api_key, lesson_title, lesson_summary, chat_history, user_message, model_name, character
    ))
    return "".join(chunks)


def get_offline_response(lesson_title: str, user_message: str, character: str = "all") -> str:
    """
    Chế độ Offline Socratic thông minh: Phân tích câu trả lời đối thoại của học sinh để phản hồi chính xác.
    """
    msg = user_message.lower().strip()
    tip = "\n\n💡 *(Mẹo: Hãy thêm `GEMINI_API_KEY` ở thanh bên trái để trò chuyện trực tiếp không giới hạn cùng Cô Curie & Thầy Newton nhé!)*"

    # --- KỊCH BẢN ĐỐI THOẠI NỐI TIẾP: CÂN BẰNG PHƯƠNG TRÌNH AL + HCL ---
    if any(k in msg for k in ["số 6", "so 6", "6 cô ơi", "chọn 6", "bội chung là 6", "là 6", "= 6", "đặt 6"]):
        return (
            "👩‍🔬 **Cô Marie Curie:**\n\n"
            "Chính xác 100%! Hoan hô em nhé! 🌟\n\n"
            "Bội chung nhỏ nhất của 2 (trong $\\mathrm{H}_2$) và 3 (trong $\\mathrm{Cl}$ của $\\mathrm{AlCl}_3$) đúng bằng **6**!\n\n"
            "Bây giờ, cô trò mình cùng đặt hệ số **6** trước $\\mathrm{HCl}$ ở vế trái nhé:\n"
            "$$\\mathrm{Al} + 6\\mathrm{HCl} \\longrightarrow \\mathrm{AlCl}_3 + \\mathrm{H}_2 \\uparrow$$\n\n"
            "Em quan sát thấy: Vế trái lúc này đang có **6 nguyên tử H** và **6 nguyên tử Cl**.\n"
            "Bây giờ em hãy nhìn sang vế phải và thử tính tiếp xem:\n"
            "1. Trước phân tử $\\mathrm{H}_2$, ta cần đặt hệ số mấy để được $6\\mathrm{H}$? (Gợi ý: lấy $6 : 2 = ?$)\n"
            "2. Trước phân tử $\\mathrm{AlCl}_3$, ta cần đặt hệ số mấy để được $6\\mathrm{Cl}$? (Gợi ý: lấy $6 : 3 = ?$)\n\n"
            "👉 Hãy cho cô biết 2 hệ số em vừa tìm được nào! 🐾"
        ) + tip

    if any(k in msg for k in ["hệ số 3 và 2", "3 và 2", "2 và 3", "3 trước h2", "2 trước alcl3", "điền 3", "điền 2", "3, 2"]):
        return (
            "👩‍🔬 **Cô Marie Curie:**\n\n"
            "Quá tuyệt vời! Em tư duy rất sắc bén! 👏\n\n"
            "- Trước $\\mathrm{H}_2$, ta đặt số **3** (vì $3 \\times 2 = 6\\mathrm{H}$).\n"
            "- Trước $\\mathrm{AlCl}_3$, ta đặt số **2** (vì $2 \\times 3 = 6\\mathrm{Cl}$).\n\n"
            "Phương trình của chúng ta hiện tại là:\n"
            "$$\\mathrm{Al} + 6\\mathrm{HCl} \\longrightarrow 2\\mathrm{AlCl}_3 + 3\\mathrm{H}_2 \\uparrow$$\n\n"
            "Bây giờ chỉ còn nguyên tố cuối cùng là Nhôm ($\\mathrm{Al}$):\n"
            "- Vế phải có $2\\mathrm{Al}$ (trong $2\\mathrm{AlCl}_3$).\n"
            "- Vế trái mới có $1\\mathrm{Al}$.\n\n"
            "👉 Vậy ta cần đặt hệ số mấy trước $\\mathrm{Al}$ ở vế trái để phương trình hoàn tất và bằng nhau hoàn toàn nào?"
        ) + tip

    if any(k in msg for k in ["2al + 6hcl", "cân bằng xong", "2 al", "hệ số 2 trước al", "điền 2 trước al", "đặt 2 trước al"]):
        return (
            "👩‍🔬 **Cô Marie Curie:**\n\n"
            "XUẤT SẮC ĐẠT ĐIỂM 10! 🎉 Chúc mừng em đã tự tay cân bằng hoàn chỉnh phương trình:\n"
            "$$2\\mathrm{Al} + 6\\mathrm{HCl} \\longrightarrow 2\\mathrm{AlCl}_3 + 3\\mathrm{H}_2 \\uparrow$$\n\n"
            "✨ **Bí quyết vàng em vừa áp dụng thành công:**\n"
            "1. Tìm bội chung nhỏ nhất giữa nguyên tố lẻ ($\\mathrm{Cl}$ có 3) và chẵn ($\\mathrm{H}$ có 2) $\\rightarrow$ Ra hệ số 6 của $\\mathrm{HCl}$.\n"
            "2. Cân bằng $\\mathrm{H}$ và $\\mathrm{Cl}$ ở vế phải $\\rightarrow$ Điền 3 và 2.\n"
            "3. Cuối cùng cân bằng kim loại $\\mathrm{Al}$ $\\rightarrow$ Điền 2 trước $\\mathrm{Al}$.\n\n"
            "Em đã nắm vững quy tắc rồi đấy! Em có muốn thử sức tự cân bằng một phương trình mới như $$\\mathrm{Fe} + \\mathrm{Cl}_2 \\rightarrow \\mathrm{FeCl}_3$$ không nào? ⚗️"
        ) + tip

    if any(k in msg for k in ["chưa hiểu", "chua hieu", "gợi ý thêm", "kho qua", "khó quá", "hướng dẫn lại"]):
        return (
            "👩‍🔬 **Cô Marie Curie:**\n\n"
            "Đừng lo lắng em nhé! Học Hóa học cần sự kiên nhẫn và quan sát tỉ mỉ, cô luôn ở đây đồng hành cùng em nè! 💖\n\n"
            "Em hãy tưởng tượng việc cân bằng phương trình giống như **chia kẹo cho hai bạn sao cho bằng nhau**:\n"
            "- Ở vế trái: Phân tử $\\mathrm{HCl}$ có 1 nguyên tử H và 1 nguyên tử Cl (tỉ lệ $1 : 1$).\n"
            "- Ở vế phải: $\\mathrm{AlCl}_3$ có 3 viên kẹo Cl, còn $\\mathrm{H}_2$ có 2 viên kẹo H.\n\n"
            "Để hai bên bằng nhau, ta cần tìm một số vừa chia hết cho 3, vừa chia hết cho 2. Số nhỏ nhất chia hết cho cả 2 và 3 chính là số **6** đấy em!\n\n"
            "👉 Bây giờ em đã thấy số **6** xuất hiện từ đâu chưa nào? Hãy thử cùng cô điền số 6 trước $\\mathrm{HCl}$ nhé!"
        ) + tip

    # Phát hiện cụ thể phản ứng Al + HCl
    if ("al" in msg and "hcl" in msg) or ("alcl3" in msg):
        return (
            "👩‍🔬 **Cô Marie Curie:**\n\n"
            "Chào em nhỏ say mê khám phá! 🌟 Cô Marie Curie đây. Thật tuyệt vời khi em chủ động muốn chinh phục việc cân bằng phương trình hóa học – đây chính là chiếc chìa khóa vàng để mở cánh cửa Định luật bảo toàn khối lượng đấy!\n\n"
            "Sơ đồ phản ứng của chúng ta là:\n"
            "$$\\mathrm{Al} + \\mathrm{HCl} \\dashrightarrow \\mathrm{AlCl}_3 + \\mathrm{H}_2 \\uparrow$$\n\n"
            "Bản chất của việc cân bằng là đảm bảo **số nguyên tử của mỗi nguyên tố ở vế trái (chất tham gia) phải bằng vế phải (sản phẩm)**.\n\n"
            "Bây giờ, cô trò mình cùng quan sát thật tỉ mỉ nhé:\n"
            "1. **Bước 1 - Đếm số nguyên tử:**\n"
            "- Ở vế phải: trong phân tử $\\mathrm{AlCl}_3$, em thấy có **3 nguyên tử Cl** (số lẻ).\n"
            "- Trong khi đó, phân tử khí $\\mathrm{H}_2$ lại có **2 nguyên tử H** (số chẵn).\n"
            "- Ở vế trái: trong phân tử $\\mathrm{HCl}$, tỉ lệ nguyên tử $\\mathrm{H}$ và $\\mathrm{Cl}$ luôn là $1 : 1$.\n"
            "2. **Bước 2 - Tìm điểm mấu chốt:**\n"
            "Để vừa chia hết cho 3 (của $\\mathrm{Cl}$) lại vừa chia hết cho 2 (của $\\mathrm{H}$), **bội chung nhỏ nhất của 3 và 2 là số mấy nhỉ?**\n\n"
            "👉 Em thử đoán xem, chúng ta nên đặt hệ số bao nhiêu vào trước $\\mathrm{HCl}$ ở vế trái trước tiên nào? Hãy bấm chọn hoặc chia sẻ suy nghĩ của em với cô nhé! 🔬✨"
        ) + tip

    # 1. Cân bằng phương trình hoá học tổng quát
    if any(k in msg for k in ["cân bằng", "can bang", "pthh", "phương trình"]):
        return (
            "👩‍🔬 **Cô Marie Curie gợi ý cho em cách cân bằng Phương trình Hóa học nhé:**\n\n"
            "Để cân bằng một phản ứng, em hãy nhớ nguyên lý tối cao: **Số lượng nguyên tử của mỗi nguyên tố ở hai vế phải bằng nhau!**\n\n"
            "Em hãy thử áp dụng thần chú 4 bước này:\n"
            "$$\\textbf{KIM LOẠI} \\longrightarrow \\textbf{PHI KIM} \\longrightarrow \\textbf{HYDROGEN (H)} \\longrightarrow \\textbf{OXYGEN (O)}$$\n\n"
            "⚠️ **Lưu ý sống còn:** Tuyệt đối **không được đổi chỉ số chân** (như $\\mathrm{O}_2, \\mathrm{H}_2\\mathrm{O}$), chỉ được thêm hệ số nguyên to đứng trước công thức hoá học!\n\n"
            "👉 Em đang muốn cân bằng phản ứng cụ thể nào? Hãy viết sơ đồ phản ứng ra đây để cô Curie hướng dẫn từng bước nhé!"
        ) + tip

    # 2. Tính số mol / tính theo phương trình
    if any(k in msg for k in ["mol", "số mol", "tính theo pthh", "tính theo phương trình"]):
        return (
            "👩‍🔬 **Cô Marie Curie đồng hành cùng em về bài toán Mol & Phương trình:**\n\n"
            "Muốn giải quyết bài toán tính theo phương trình hoá học, 'chìa khóa vàng' luôn là đưa mọi dữ kiện về **số mol ($n$)**:\n"
            "- Nếu đề cho khối lượng gam ($m$): Áp dụng $$n = \\frac{m}{M}$$\n"
            "- Nếu đề cho thể tích chất khí ở đkc ($25^\\circ\\mathrm{C}, 1\\mathrm{ bar}$): Áp dụng $$n = \\frac{V}{24{,}79}$$\n\n"
            "🔍 Sau khi có số mol rồi, em đã viết và cân bằng chính xác phương trình hoá học chưa? Hãy đối chiếu tỉ lệ hệ số để tìm số mol chất cần tính nhé!"
        ) + tip

    # 3. Nồng độ dung dịch C% và CM
    if any(k in msg for k in ["nồng độ", "nong do", "c%", "cm", "dung dịch"]):
        return (
            "👩‍🔬 **Cô Marie Curie hướng dẫn em phân biệt hai loại nồng độ:**\n\n"
            "1. **Nồng độ phần trăm ($C\\%$):** Tỉ lệ khối lượng chất tan trong $100\\mathrm{ g}$ dung dịch:\n"
            "$$C\\% = \\frac{m_{\\text{ct}}}{m_{\\text{dd}}} \\cdot 100\\% \\quad (m_{\\text{dd}} = m_{\\text{ct}} + m_{\\text{nước}})$$\n"
            "2. **Nồng độ mol ($C_M$):** Số mol chất tan có trong $1\\mathrm{ L}$ dung dịch:\n"
            "$$C_M = \\frac{n}{V} \\quad (V \\text{ phải đổi ra lít!})$$\n\n"
            "👉 Đề bài của em đang yêu cầu tính $C\\%$ hay $C_M$? Em đã có đủ khối lượng chất tan và thể tích chưa?"
        ) + tip

    # 4. Hiện tượng tôi vôi sống
    if any(k in msg for k in ["vôi", "tôi vôi", "sôi", "cao"]):
        return (
            "👩‍🔬 **Cô Marie Curie giải thích hiện tượng tôi vôi sôi sùng sục:**\n\n"
            "Khi cho vôi sống ($\\mathrm{CaO}$) vào nước, phản ứng hoá học xảy ra mãnh liệt:\n"
            "$$\\mathrm{CaO} + \\mathrm{H}_2\\mathrm{O} \\rightarrow \\mathrm{Ca(OH)}_2 + Q$$\n"
            "Đây là một **phản ứng toả nhiệt cực mạnh**. Nhiệt lượng tỏa ra đột ngột trong hố vôi làm nước xung quanh bị đun sôi tới $100^\\circ\\mathrm{C}$ và bốc hơi mù mịt!\n\n"
            "⚠️ *Lưu ý an toàn:* Nước vôi tôi vừa nóng vừa có tính kiềm ăn mòn cao, nên tuyệt đối không được đến gần miệng hố vôi đang tôi nhé!"
        ) + tip

    # 5. Khối lượng riêng D = m / V
    if any(k in msg for k in ["khối lượng riêng", "khoi luong rieng", "d ="]):
        return (
            "🍎 **Thầy Isaac Newton chào em! Ta cùng tìm hiểu về Khối lượng riêng:**\n\n"
            "Khối lượng riêng đặc trưng cho mức độ phân bố khối lượng của chất trong một đơn vị thể tích:\n"
            "$$D = \\frac{m}{V}$$\n"
            "- Nếu $m$ tính bằng $\\mathrm{kg}$, $V$ tính bằng $\\mathrm{m^3}$ thì $D$ có đơn vị $\\mathrm{kg/m^3}$.\n"
            "- Nhớ quy tắc đổi đơn vị: $1\\mathrm{ g/cm^3} = 1000\\mathrm{ kg/m^3}$.\n\n"
            "🔍 Em có biết tại sao một thanh sắt nặng $7800\\mathrm{ kg/m^3}$ lại chìm trong nước, còn dầu ăn $800\\mathrm{ kg/m^3}$ lại nổi lên trên không?"
        ) + tip

    # 6. Áp suất chất lỏng & Lặn sâu tức ngực
    if any(k in msg for k in ["áp suất", "ap suat", "tức ngực", "lặn", "lan"]):
        return (
            "🍎 **Thầy Isaac Newton giải thích hiện tượng thợ lặn bị tức ngực:**\n\n"
            "Trong lòng chất lỏng, áp suất tăng đều theo độ sâu theo công thức:\n"
            "$$p = d \\cdot h$$\n"
            "- Cứ lặn sâu thêm $10\\mathrm{ m}$, áp suất nước lại tăng thêm khoảng $100\\,000\\mathrm{ Pa}$ ($1\\mathrm{ atm}$).\n"
            "- Ở độ sâu $20 - 30\\mathrm{ m}$, áp suất ép lên toàn bộ bề mặt cơ thể gấp 3 đến 4 lần bình thường! Áp lực nước khổng lồ ép mạnh lên lồng ngực làm phổi bị nén thể tích, chèn ép tim gây tức ngực khó thở dữ dội.\n\n"
            "👉 Vì thế thợ lặn phải mặc bộ đồ lặn chịu áp lực cao và thở bình khí nén có van cân bằng áp suất đấy em ạ!"
        ) + tip

    # 7. Lực đẩy Archimedes
    if any(k in msg for k in ["archimedes", "ác-si-mét", "lực đẩy", "chìm", "nổi"]):
        return (
            "🍎 **Thầy Isaac Newton chia sẻ về phát hiện vĩ đại của tiền bối Archimedes:**\n\n"
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
            "🍎 **Thầy Isaac Newton hướng dẫn quy tắc đòn bẩy:**\n\n"
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

    # Mặc định theo nhân vật
    if character == "curie":
        return (
            f"Chào em nhỏ! Cô **Marie Curie** 👩‍🔬 rất vui được cùng em khám phá bài học **{lesson_title}**.\n\n"
            "Em đang muốn cô hướng dẫn về phần nào:\n"
            "1. Cân bằng phương trình hoá học từng bước?\n"
            "2. Bài toán tính số mol ($n$) và nồng độ dung dịch ($C\\%, C_M$)?\n"
            "3. Hay bản chất của một phản ứng hoá học kỳ thú?\n\n"
            "Hãy viết phương trình hoặc câu hỏi của em ra đây để cô hướng dẫn nhé!"
        ) + tip
    elif character == "newton":
        return (
            f"Chào em! Thầy **Isaac Newton** 🍎 chào mừng em đến với thế giới Vật lý & Tự nhiên của **{lesson_title}**.\n\n"
            "Em có câu hỏi nào về:\n"
            "1. Các định luật chuyển động, lực và áp suất?\n"
            "2. Cách tính khối lượng riêng $D = m/V$ hay lực đẩy Archimedes?\n"
            "3. Hay bí quyết ứng dụng đòn bẩy và năng lượng nhiệt trong đời sống?\n\n"
            "Hãy chia sẻ câu hỏi của em với Thầy nhé!"
        ) + tip

    return (
        f"Chào em! Bác học **Isaac Newton** 🍎 và **Marie Curie** 👩‍🔬 rất vui được đồng hành cùng em trong bài học **{lesson_title}**.\n\n"
        "Em đang gặp vướng mắc ở phần nào:\n"
        "1. Bản chất hiện tượng hay thí nghiệm thực tế?\n"
        "2. Công thức tính toán hay cân bằng phương trình hoá học?\n"
        "3. Hay phương pháp giải một bài tập cụ thể trong SGK?\n\n"
        "Hãy gõ câu hỏi hoặc phép tính em đang làm, chúng ta sẽ cùng từng bước tìm ra lời giải nhé!"
    ) + tip
