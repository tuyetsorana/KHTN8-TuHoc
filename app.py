import streamlit as st
import os
import re
import base64
import json
import random
import time
import database as db
import ai_tutor
import streamlit.components.v1 as components

# ================= CẤU HÌNH TRANG STREAMLIT =================
st.set_page_config(
    page_title="KHTN 8 Tự Học Thông Minh - Kết Nối Tri Thức",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chống lỗi React removeChild do Google Translate / trình duyệt dịch tự động làm biến đổi DOM
st.markdown("""
<meta name="google" content="notranslate">
<div class="notranslate" translate="no" style="display:none;"></div>
""", unsafe_allow_html=True)

# Custom CSS giao diện Khoa học Tự nhiên Dễ thương (Cute & Lively Science)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@600;700&family=Nunito:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"], .main, [data-testid="stAppViewContainer"] {
        font-family: 'Nunito', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    h1, h2, h3, .app-header h1 {
        font-family: 'Comfortaa', 'Nunito', cursive, sans-serif !important;
    }
    
    /* Header chủ đạo phong cách Cute Galaxy */
    .app-header {
        background: linear-gradient(135deg, #0284c7 0%, #0d9488 40%, #10b981 75%, #f59e0b 100%);
        color: white;
        padding: 1.8rem 2.2rem;
        border-radius: 24px;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.28);
        border: 2px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    .app-header::after {
        content: "✨🫧🔭🍎";
        position: absolute;
        right: 20px;
        bottom: 10px;
        font-size: 2.2rem;
        opacity: 0.35;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        color: white !important;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .app-header p {
        margin: 0.6rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Callout blocks bo tròn cực cute */
    .callout-note {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        border: 2px solid #a7f3d0;
        border-left: 8px solid #10b981;
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        margin: 1.3rem 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
    }
    .callout-tip {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #fde68a;
        border-left: 8px solid #f59e0b;
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        margin: 1.3rem 0;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);
    }
    
    /* Card hiện tượng thực tế xinh xắn */
    .phenomenon-card {
        background: #ffffff;
        border: 2px solid #bae6fd;
        border-radius: 20px;
        padding: 1.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.07);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .phenomenon-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(14, 165, 233, 0.12);
    }
    
    /* Badge môn học xinh xắn */
    .badge-chem {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        color: #0284c7;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1px solid #7dd3fc;
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.1);
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .badge-phy {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #b45309;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1px solid #fcd34d;
        box-shadow: 0 2px 6px rgba(180, 83, 9, 0.1);
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .badge-bio {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #15803d;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1px solid #86efac;
        box-shadow: 0 2px 6px rgba(21, 128, 61, 0.1);
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    
    /* Stat box dễ thương trong sidebar */
    .cute-stat-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 0.9rem;
        text-align: center;
        margin-bottom: 0.6rem;
        box-shadow: 0 3px 8px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo cơ sở dữ liệu
db.init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Danh mục bài học KHTN 8 chuẩn 100% SGK Kết nối tri thức (47 Bài)
LESSONS = [
    {
        "id": "Bai_01_Su_dung_hoa_chat_va_thiet_bi",
        "title": "Bài 1: Sử dụng hoá chất & thiết bị cơ bản",
        "chapter": "Mở đầu: Kỹ năng phòng thí nghiệm",
        "subject": "Kỹ năng thực hành",
        "file": "Bai_01_Su_dung_hoa_chat_va_thiet_bi.md",
        "dir": "Chuong_00_Mo_dau"
    },
    {
        "id": "Bai_02_Phan_ung_hoa_hoc",
        "title": "Bài 2: Phản ứng hoá học",
        "chapter": "Chương I: Phản ứng hoá học",
        "subject": "Hóa học",
        "file": "Bai_02_Phan_ung_hoa_hoc.md",
        "dir": "Chuong_01_Phan_ung_hoa_hoc"
    },
    {
        "id": "Bai_03_Mol_va_ti_khoi_chat_khi",
        "title": "Bài 3: Mol và tỉ khối chất khí",
        "chapter": "Chương I: Phản ứng hoá học",
        "subject": "Hóa học",
        "file": "Bai_03_Mol_va_ti_khoi_chat_khi.md",
        "dir": "Chuong_01_Phan_ung_hoa_hoc"
    },
    {
        "id": "Bai_04_Dung_dich_va_nong_do",
        "title": "Bài 4: Dung dịch và nồng độ",
        "chapter": "Chương I: Phản ứng hoá học",
        "subject": "Hóa học",
        "file": "Bai_04_Dung_dich_va_nong_do.md",
        "dir": "Chuong_01_Phan_ung_hoa_hoc"
    },
    {
        "id": "Bai_05_Dinh_luat_bao_toan_khoi_luong_va_PTHH",
        "title": "Bài 5: Định luật bảo toàn khối lượng & PTHH",
        "chapter": "Chương I: Phản ứng hoá học",
        "subject": "Hóa học",
        "file": "Bai_05_Dinh_luat_bao_toan_khoi_luong_va_PTHH.md",
        "dir": "Chuong_01_Phan_ung_hoa_hoc"
    },
    {
        "id": "Bai_06_Tinh_theo_phuong_trinh_hoa_hoc",
        "title": "Bài 6: Tính theo phương trình hoá học",
        "chapter": "Chương I: Phản ứng hoá học",
        "subject": "Hóa học",
        "file": "Bai_06_Tinh_theo_phuong_trinh_hoa_hoc.md",
        "dir": "Chuong_01_Phan_ung_hoa_hoc"
    },
    {
        "id": "Bai_07_Toc_do_phan_ung_va_chat_xuc_tac",
        "title": "Bài 7: Tốc độ phản ứng và chất xúc tác",
        "chapter": "Chương I: Phản ứng hoá học",
        "subject": "Hóa học",
        "file": "Bai_07_Toc_do_phan_ung_va_chat_xuc_tac.md",
        "dir": "Chuong_01_Phan_ung_hoa_hoc"
    },
    {
        "id": "Bai_08_Acid",
        "title": "Bài 8: Acid",
        "chapter": "Chương II: Một số hợp chất thông dụng",
        "subject": "Hóa học",
        "file": "Bai_08_Acid.md",
        "dir": "Chuong_02_Mot_so_hop_chat_thong_dung"
    },
    {
        "id": "Bai_09_Base_Thang_pH",
        "title": "Bài 9: Base. Thang pH",
        "chapter": "Chương II: Một số hợp chất thông dụng",
        "subject": "Hóa học",
        "file": "Bai_09_Base_Thang_pH.md",
        "dir": "Chuong_02_Mot_so_hop_chat_thong_dung"
    },
    {
        "id": "Bai_10_Oxide",
        "title": "Bài 10: Oxide",
        "chapter": "Chương II: Một số hợp chất thông dụng",
        "subject": "Hóa học",
        "file": "Bai_10_Oxide.md",
        "dir": "Chuong_02_Mot_so_hop_chat_thong_dung"
    },
    {
        "id": "Bai_11_Muoi",
        "title": "Bài 11: Muối",
        "chapter": "Chương II: Một số hợp chất thông dụng",
        "subject": "Hóa học",
        "file": "Bai_11_Muoi.md",
        "dir": "Chuong_02_Mot_so_hop_chat_thong_dung"
    },
    {
        "id": "Bai_12_Phan_bon_hoa_hoc",
        "title": "Bài 12: Phân bón hoá học",
        "chapter": "Chương II: Một số hợp chất thông dụng",
        "subject": "Hóa học",
        "file": "Bai_12_Phan_bon_hoa_hoc.md",
        "dir": "Chuong_02_Mot_so_hop_chat_thong_dung"
    },
    {
        "id": "Bai_13_Khoi_luong_rieng",
        "title": "Bài 13: Khối lượng riêng",
        "chapter": "Chương III: Khối lượng riêng và Áp suất",
        "subject": "Vật lý",
        "file": "Bai_13_Khoi_luong_rieng.md",
        "dir": "Chuong_03_Khoi_luong_rieng_va_Ap_suat"
    },
    {
        "id": "Bai_14_Thuc_hanh_xac_dinh_khoi_luong_rieng",
        "title": "Bài 14: Thực hành xác định khối lượng riêng",
        "chapter": "Chương III: Khối lượng riêng và Áp suất",
        "subject": "Vật lý",
        "file": "Bai_14_Thuc_hanh_xac_dinh_khoi_luong_rieng.md",
        "dir": "Chuong_03_Khoi_luong_rieng_va_Ap_suat"
    },
    {
        "id": "Bai_15_Ap_suat_tren_mot_be_mat",
        "title": "Bài 15: Áp suất trên một bề mặt",
        "chapter": "Chương III: Khối lượng riêng và Áp suất",
        "subject": "Vật lý",
        "file": "Bai_15_Ap_suat_tren_mot_be_mat.md",
        "dir": "Chuong_03_Khoi_luong_rieng_va_Ap_suat"
    },
    {
        "id": "Bai_16_Ap_suat_chat_long_Ap_suat_khi_quyen",
        "title": "Bài 16: Áp suất chất lỏng & Áp suất khí quyển",
        "chapter": "Chương III: Khối lượng riêng và Áp suất",
        "subject": "Vật lý",
        "file": "Bai_16_Ap_suat_chat_long_Ap_suat_khi_quyen.md",
        "dir": "Chuong_03_Khoi_luong_rieng_va_Ap_suat"
    },
    {
        "id": "Bai_17_Luc_day_Archimedes",
        "title": "Bài 17: Lực đẩy Archimedes",
        "chapter": "Chương III: Khối lượng riêng và Áp suất",
        "subject": "Vật lý",
        "file": "Bai_17_Luc_day_Archimedes.md",
        "dir": "Chuong_03_Khoi_luong_rieng_va_Ap_suat"
    },
    {
        "id": "Bai_18_Tac_dung_lam_quay_cua_luc_Moment_luc",
        "title": "Bài 18: Tác dụng làm quay. Moment lực",
        "chapter": "Chương IV: Tác dụng làm quay của lực",
        "subject": "Vật lý",
        "file": "Bai_18_Tac_dung_lam_quay_cua_luc_Moment_luc.md",
        "dir": "Chuong_04_Tac_dung_lam_quay_cua_luc"
    },
    {
        "id": "Bai_19_Don_bay_va_ung_dung",
        "title": "Bài 19: Đòn bẩy và ứng dụng",
        "chapter": "Chương IV: Tác dụng làm quay của lực",
        "subject": "Vật lý",
        "file": "Bai_19_Don_bay_va_ung_dung.md",
        "dir": "Chuong_03_Khoi_luong_rieng_va_Ap_suat"
    },
    {
        "id": "Bai_20_Hien_tuong_nhiem_dien_do_co_xat",
        "title": "Bài 20: Hiện tượng nhiễm điện do cọ xát",
        "chapter": "Chương V: Điện",
        "subject": "Vật lý",
        "file": "Bai_20_Hien_tuong_nhiem_dien_do_co_xat.md",
        "dir": "Chuong_05_Dien"
    },
    {
        "id": "Bai_21_Dong_dien_nguon_dien",
        "title": "Bài 21: Dòng điện, nguồn điện",
        "chapter": "Chương V: Điện",
        "subject": "Vật lý",
        "file": "Bai_21_Dong_dien_nguon_dien.md",
        "dir": "Chuong_05_Dien"
    },
    {
        "id": "Bai_22_Mach_dien_don_gian",
        "title": "Bài 22: Mạch điện đơn giản",
        "chapter": "Chương V: Điện",
        "subject": "Vật lý",
        "file": "Bai_22_Mach_dien_don_gian.md",
        "dir": "Chuong_05_Dien"
    },
    {
        "id": "Bai_23_Tac_dung_cua_dong_dien",
        "title": "Bài 23: Tác dụng của dòng điện",
        "chapter": "Chương V: Điện",
        "subject": "Vật lý",
        "file": "Bai_23_Tac_dung_cua_dong_dien.md",
        "dir": "Chuong_05_Dien"
    },
    {
        "id": "Bai_24_Cuong_do_dong_dien_va_hieu_dien_the",
        "title": "Bài 24: Cường độ dòng điện và hiệu điện thế",
        "chapter": "Chương V: Điện",
        "subject": "Vật lý",
        "file": "Bai_24_Cuong_do_dong_dien_va_hieu_dien_the.md",
        "dir": "Chuong_05_Dien"
    },
    {
        "id": "Bai_25_Thuc_hanh_do_cuong_do_dong_dien_va_hieu_dien_the",
        "title": "Bài 25: Thực hành đo I và U",
        "chapter": "Chương V: Điện",
        "subject": "Vật lý",
        "file": "Bai_25_Thuc_hanh_do_cuong_do_dong_dien_va_hieu_dien_the.md",
        "dir": "Chuong_05_Dien"
    },
    {
        "id": "Bai_26_Nang_luong_nhiet_va_noi_nang",
        "title": "Bài 26: Năng lượng nhiệt và nội năng",
        "chapter": "Chương VI: Nhiệt",
        "subject": "Vật lý",
        "file": "Bai_26_Nang_luong_nhiet_va_noi_nang.md",
        "dir": "Chuong_06_Nhiet"
    },
    {
        "id": "Bai_27_Thuc_hanh_do_nang_luong_nhiet_bang_joulemeter",
        "title": "Bài 27: Thực hành đo nhiệt bằng Joulemeter",
        "chapter": "Chương VI: Nhiệt",
        "subject": "Vật lý",
        "file": "Bai_27_Thuc_hanh_do_nang_luong_nhiet_bang_joulemeter.md",
        "dir": "Chuong_06_Nhiet"
    },
    {
        "id": "Bai_28_Su_truyen_nhiet",
        "title": "Bài 28: Sự truyền nhiệt",
        "chapter": "Chương VI: Nhiệt",
        "subject": "Vật lý",
        "file": "Bai_28_Su_truyen_nhiet.md",
        "dir": "Chuong_06_Nhiet"
    },
    {
        "id": "Bai_29_Su_no_vi_nhiet",
        "title": "Bài 29: Sự nở vì nhiệt",
        "chapter": "Chương VI: Nhiệt",
        "subject": "Vật lý",
        "file": "Bai_29_Su_no_vi_nhiet.md",
        "dir": "Chuong_06_Nhiet"
    },
    {
        "id": "Bai_30_Khai_quat_ve_co_the_nguoi",
        "title": "Bài 30: Khái quát về cơ thể người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_30_Khai_quat_ve_co_the_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_31_He_van_dong_o_nguoi",
        "title": "Bài 31: Hệ vận động ở người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_31_He_van_dong_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_32_Dinh_duong_va_tieu_hoa_o_nguoi",
        "title": "Bài 32: Dinh dưỡng và tiêu hoá ở người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_32_Dinh_duong_va_tieu_hoa_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_33_Mau_va_he_tuan_hoan_cua_co_the_nguoi",
        "title": "Bài 33: Máu và hệ tuần hoàn",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_33_Mau_va_he_tuan_hoan_cua_co_the_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_34_He_ho_hap_o_nguoi",
        "title": "Bài 34: Hệ hô hấp ở người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_34_He_ho_hap_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_35_He_bai_tiet_o_nguoi",
        "title": "Bài 35: Hệ bài tiết ở người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_35_He_bai_tiet_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_36_Dieu_hoa_moi_truong_trong_cua_co_the_nguoi",
        "title": "Bài 36: Điều hoà môi trường trong",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_36_Dieu_hoa_moi_truong_trong_cua_co_the_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_37_He_than_kinh_va_cac_giac_quan_o_nguoi",
        "title": "Bài 37: Hệ thần kinh & giác quan",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_37_He_than_kinh_va_cac_giac_quan_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_38_He_noi_tiet_o_nguoi",
        "title": "Bài 38: Hệ nội tiết ở người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_38_He_noi_tiet_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_39_Da_va_dieu_hoa_than_nhiet_o_nguoi",
        "title": "Bài 39: Da và điều hoà thân nhiệt",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_39_Da_va_dieu_hoa_than_nhiet_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_40_Sinh_san_o_nguoi",
        "title": "Bài 40: Sinh sản ở người",
        "chapter": "Chương VII: Sinh học cơ thể người",
        "subject": "Sinh học",
        "file": "Bai_40_Sinh_san_o_nguoi.md",
        "dir": "Chuong_07_Sinh_hoc_co_the_nguoi"
    },
    {
        "id": "Bai_41_Moi_truong_va_cac_nhan_to_sinh_thai",
        "title": "Bài 41: Môi trường & các nhân tố sinh thái",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_41_Moi_truong_va_cac_nhan_to_sinh_thai.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    },
    {
        "id": "Bai_42_Quan_the_sinh_vat",
        "title": "Bài 42: Quần thể sinh vật",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_42_Quan_the_sinh_vat.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    },
    {
        "id": "Bai_43_Quan_xa_sinh_vat",
        "title": "Bài 43: Quần xã sinh vật",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_43_Quan_xa_sinh_vat.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    },
    {
        "id": "Bai_44_He_sinh_thai",
        "title": "Bài 44: Hệ sinh thái",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_44_He_sinh_thai.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    },
    {
        "id": "Bai_45_Sinh_quyen",
        "title": "Bài 45: Sinh quyển",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_45_Sinh_quyen.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    },
    {
        "id": "Bai_46_Can_bang_tu_nhien",
        "title": "Bài 46: Cân bằng tự nhiên",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_46_Can_bang_tu_nhien.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    },
    {
        "id": "Bai_47_Bao_ve_moi_truong",
        "title": "Bài 47: Bảo vệ môi trường",
        "chapter": "Chương VIII: Sinh vật và môi trường",
        "subject": "Sinh học",
        "file": "Bai_47_Bao_ve_moi_truong.md",
        "dir": "Chuong_08_Sinh_vat_va_moi_truong"
    }
]

# Nạp dữ liệu các phân hệ
@st.cache_data
def load_json_data(file_name: str):
    p = os.path.join(BASE_DIR, "data", file_name)
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

LESSON_VIDEOS = load_json_data("lesson_videos.json")
PHET_SIMS = load_json_data("phet_simulations.json")
REAL_PHENOMENA = load_json_data("real_phenomena.json")
SGK_SOLUTIONS = load_json_data("sgk_solutions.json")
EXTRA_EXERCISES = load_json_data("extra_exercises.json")
EXTRA_PRACTICE_PROBLEMS = load_json_data("extra_practice_problems.json")
LESSON_THEORY_HUB = load_json_data("lesson_theory_hub.json")

def load_markdown_content(lesson_dict: dict) -> str:
    """Nạp bài học Markdown và chuyển đổi ảnh sang Base64 data URI"""
    file_path = os.path.join(BASE_DIR, lesson_dict["dir"], "content", lesson_dict["file"])
    if not os.path.exists(file_path):
        return f"⚠️ Không tìm thấy file nội dung: {lesson_dict['file']}"
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Nhúng ảnh Base64
    def replace_img(match):
        alt = match.group(1)
        src = match.group(2)
        norm_path = os.path.normpath(os.path.join(BASE_DIR, lesson_dict["dir"], "content", src))
        if not os.path.exists(norm_path):
            candidate = os.path.join(ASSETS_DIR, "images", os.path.basename(src))
            if os.path.exists(candidate):
                norm_path = candidate
                
        if os.path.exists(norm_path):
            ext = os.path.splitext(norm_path)[1].lower().replace(".", "")
            mime = "image/png" if ext == "png" else "image/jpeg"
            try:
                with open(norm_path, "rb") as img_f:
                    b64 = base64.b64encode(img_f.read()).decode("utf-8")
                return f'<div style="text-align: center; margin: 1.2rem 0;"><img src="data:{mime};base64,{b64}" alt="{alt}" style="max-width: 88%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);"><br><em style="font-size: 0.9rem; color: #64748b;">{alt}</em></div>'
            except Exception:
                return f"*(Không tải được hình: {alt})*"
        return match.group(0)

    content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img, content)
    
    # Định dạng Callouts dễ thương
    content = re.sub(r'> \[!NOTE\]\s*\n((?:> .*\n?)*)', r'<div class="callout-note"><strong>🌱 Bí Kíp Trọng Tâm Của Bé:</strong>\n\1</div>\n', content)
    content = re.sub(r'> \[!TIP\]\s*\n((?:> .*\n?)*)', r'<div class="callout-tip"><strong>💡 Mẹo Vàng Newton & Curie:</strong>\n\1</div>\n', content)
    
    content = re.sub(r'<div class="(?:callout-note|callout-tip)">([\s\S]*?)</div>', 
                     lambda m: '<div class="' + ('callout-note' if 'callout-note' in m.group(0) else 'callout-tip') + '">' + m.group(1).replace('> ', '').replace('>', '') + '</div>', 
                     content)

    return content

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ✨🔬 KHOA HỌC TỰ NHIÊN 8 🎒✨")
    st.caption("🌈 Cùng học vui mỗi ngày • Nắm trọn điểm 10 🌟")
    
    # Thống kê học tập dễ thương
    stats = db.get_student_stats(len(LESSONS))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="cute-stat-card">
            <div style="font-size: 1.5rem; font-weight: 800; color: #f97316;">🔥 {stats['streak']}</div>
            <div style="font-size: 0.8rem; color: #64748b; font-weight: 700;">Ngày chăm chỉ 🐾</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="cute-stat-card">
            <div style="font-size: 1.5rem; font-weight: 800; color: #eab308;">⭐ {int(stats['total_points'])}</div>
            <div style="font-size: 0.8rem; color: #64748b; font-weight: 700;">Sao tích lũy 🌟</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"**🌱 Mầm non ➡️ 🌿 Lớn lên ➡️ 🍎 Thu hoạch ({stats['completed_count']}/{len(LESSONS)} bài • {stats['completion_rate']}%)**")
    st.progress(stats['completion_rate'] / 100.0)
    
    st.markdown("---")
    
    # Bộ lọc phân môn tích hợp
    selected_subj = st.selectbox(
        "📚 Khám phá phân môn:",
        [
            "🌈 Tất cả phân môn kỳ thú",
            "🧪 Kỹ năng thực hành & Mở đầu 🔬",
            "⚗️ Hóa Học Diệu Kỳ (Chất & Phản ứng) 🫧",
            "⚡ Vật Lý Vui Nhộn (Lực, Năng lượng, Điện) 🧲",
            "🧬 Sinh Học Kỳ Thú (Cơ thể người & Môi trường) 🌿"
        ]
    )
    
    filtered_lessons = LESSONS
    if "Kỹ năng" in selected_subj:
        filtered_lessons = [l for l in LESSONS if "Kỹ năng" in l["subject"] or "Chuong_00" in l["dir"]]
    elif "Hóa Học" in selected_subj:
        filtered_lessons = [l for l in LESSONS if l["subject"] == "Hóa học"]
    elif "Vật Lý" in selected_subj:
        filtered_lessons = [l for l in LESSONS if l["subject"] == "Vật lý"]
    elif "Sinh Học" in selected_subj:
        filtered_lessons = [l for l in LESSONS if l["subject"] == "Sinh học"]

    progress_map = db.get_all_progress()
    lesson_labels = []
    for l in filtered_lessons:
        st_p = progress_map.get(l["id"], {}).get("status", "not_started")
        badge = "🌟" if st_p == "completed" else ("🚀" if st_p == "in_progress" else "🌱")
        subj_icon = "🧪" if "Kỹ năng" in l["subject"] else ("⚗️" if l["subject"] == "Hóa học" else ("⚡" if l["subject"] == "Vật lý" else "🧬"))
        lesson_labels.append(f"{badge} {subj_icon} {l['title']}")

    sel_idx = st.radio(
        "Danh sách bài học:",
        range(len(filtered_lessons)),
        format_func=lambda i: lesson_labels[i],
        label_visibility="collapsed"
    )
    current_lesson = filtered_lessons[sel_idx]
    
    st.markdown("---")
    st.markdown("#### 🤖 Gia Sư AI Khoa Học")
    st.caption("Bác học Newton & Marie Curie đồng hành Socratic")
    
    selected_model = st.selectbox(
        "⚡ Mô hình Gemini AI:",
        ["gemini-2.5-flash (Siêu tốc & Thông minh ⭐)", "gemini-2.0-flash (Phản hồi tức thì ⚡)", "gemini-1.5-flash (Ổn định)", "gemini-2.5-pro (Tư duy chuyên sâu)"],
        index=0,
        help="Mô hình Gemini 2.5 Flash và 2.0 Flash thế hệ mới với tốc độ phản hồi cực nhanh dưới 0.5 giây."
    )
    model_code = selected_model.split(" ")[0]
    
    cloud_key = ""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            cloud_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not cloud_key:
        cloud_key = os.getenv("GEMINI_API_KEY", "")

    if cloud_key:
        api_key_input = cloud_key
        st.success(f"🟢 Online ({model_code} qua Secrets)")
    else:
        api_key_input = st.text_input(
            "GEMINI_API_KEY (Tuỳ chọn):",
            type="password",
            help="Nhập Gemini API Key để trò chuyện trực tiếp. Nếu để trống, app sẽ chạy Chế độ Offline Socratic cực kỳ thông minh."
        )
        if api_key_input:
            st.success(f"🟢 Online ({model_code})")
        else:
            st.info("🟡 Chế độ Offline Socratic (Sẵn sàng)")

# Đánh dấu bài học bắt đầu học
db.mark_lesson_in_progress(current_lesson["id"], current_lesson["title"])

# ================= KHU VỰC CHÍNH =================
subj_icon = "⚗️" if current_lesson["subject"] == "Hóa học" else ("⚡" if current_lesson["subject"] == "Vật lý" else "🧬")
subj_class = "badge-chem" if current_lesson["subject"] == "Hóa học" else ("badge-phy" if current_lesson["subject"] == "Vật lý" else "badge-bio")
st.markdown(f"""
<div class="app-header">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
        <span class="{subj_class}">{subj_icon} {current_lesson['subject'].upper()}</span>
        <span style="opacity: 0.95; font-size: 1rem; font-weight: 700;">✨ {current_lesson['chapter']}</span>
    </div>
    <h1>{current_lesson['title']} 🌟</h1>
    <p>🌈 Khám phá thế giới diệu kỳ • Thí nghiệm trực quan • Cùng Bác học Newton & Marie Curie 👩‍🔬🍎</p>
</div>
""", unsafe_allow_html=True)

# 4 Tab chức năng Sư phạm phong cách Cute & Sinh động
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Khám Phá Bài Học 🌈",
    "🫧 Thí Nghiệm & Hiện Tượng Kỳ Thú 🔬",
    "🎮 Đấu Trường & Bài Tập SGK 🏆",
    "🪄 Góc Bác Học Newton & Curie 👩‍🔬🍎"
])

# ================= TAB 1: BÀI HỌC & LÝ THUYẾT TINH GỌN =================
with tab1:
    theory = LESSON_THEORY_HUB.get(current_lesson["file"])
    content_md = load_markdown_content(current_lesson)
    
    # Chia phần lý thuyết của mỗi bài thành 3 thẻ chuyên biệt
    subtab1, subtab2, subtab3 = st.tabs([
        "💡 Ghi nhớ nhanh",
        "🔬 Thí nghiệm & Ví dụ mẫu",
        "📖 Đọc thêm SGK"
    ])
    
    # ----- THẺ 1: GHI NHỚ NHANH (TRỌNG TÂM CỐT LÕI) -----
    with subtab1:
        st.markdown("#### 💡 Trọng Tâm Cốt Lõi Cần Nhớ")
        if theory and "quick_summary" in theory:
            qs = theory["quick_summary"]
            
            # 1. Khái niệm then chốt
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border-left: 5px solid #10b981; padding: 1.2rem; border-radius: 14px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);">
                <div style="font-weight: 800; color: #047857; font-size: 1.15rem; margin-bottom: 0.4rem;">📌 Khái Niệm Then Chốt</div>
                <div style="font-size: 1.05rem; color: #1e293b; line-height: 1.6;">{qs.get('key_concept', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Công thức & Phương trình phản ứng (chuẩn KaTeX)
            st.markdown("""
            <div style="background: #ffffff; border: 2px solid #e0e7ff; border-radius: 14px; padding: 1.2rem; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.06);">
                <div style="font-weight: 800; color: #4338ca; font-size: 1.15rem; margin-bottom: 0.5rem;">⚗️ Công Thức & Phương Trình Phản Ứng (Chuẩn KaTeX)</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(qs.get('formulas_reactions', ''))
            
            # 3. Bản chất hiện tượng & Ứng dụng thực tế
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-left: 5px solid #f59e0b; padding: 1.2rem; border-radius: 14px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);">
                <div style="font-weight: 800; color: #b45309; font-size: 1.15rem; margin-bottom: 0.4rem;">🌍 Bản Chất Hiện Tượng & Ứng Dụng Thực Tế</div>
                <div style="font-size: 1rem; color: #334155; line-height: 1.6;">{qs.get('real_world', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 4. Bẫy & Nhầm lẫn thường gặp
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%); border-left: 5px solid #f43f5e; padding: 1.2rem; border-radius: 14px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.08);">
                <div style="font-weight: 800; color: #be123c; font-size: 1.15rem; margin-bottom: 0.4rem;">⚠️ Bẫy & Nhầm Lẫn Thường Gặp Của Học Sinh</div>
                <div style="font-size: 1rem; color: #475569; line-height: 1.6;">{qs.get('common_pitfalls', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 Mời bạn xem toàn bộ nội dung bài học chi tiết ở thẻ **'📖 Đọc thêm SGK'** hoặc trò chuyện với Gia sư AI ở Tab 4!")
            
    # ----- THẺ 2: THÍ NGHIỆM & VÍ DỤ MẪU -----
    with subtab2:
        if theory and "experiment_or_example" in theory:
            ee = theory["experiment_or_example"]
            cat = ee.get("category", "Thí nghiệm & Ví dụ mẫu")
            st.markdown(f"#### 🔬 {cat}: {ee.get('title', '')}")
            
            st.markdown("""
            <div style="background: #ffffff; border: 2px solid #bae6fd; border-radius: 14px; padding: 1.2rem; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08);">
                <div style="font-weight: 800; color: #0284c7; font-size: 1.15rem; margin-bottom: 0.6rem;">📋 Hướng Dẫn Từng Bước Chi Tiết:</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(ee.get('steps', ''))
            
            if ee.get("takeaway"):
                st.success(f"✨ **Bác học đúc kết:** {ee.get('takeaway')}")
        else:
            st.info("🔬 Bài học này khuyến khích học sinh quan sát thực tế và cùng khám phá phòng thí nghiệm ảo ở Tab 2!")

        # Video bài giảng và thí nghiệm trực quan
        lesson_media = LESSON_VIDEOS.get(current_lesson["file"])
        if lesson_media:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🎬 Video Bài Giảng Giáo Viên & Clip Thí Nghiệm Cận Cảnh", expanded=True):
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    st.markdown("##### 👨‍🏫 Bài giảng chi tiết của Giáo viên")
                    lec = lesson_media.get("lecture", {})
                    st.markdown(f"**{lec.get('video_title')}**")
                    st.caption(f"Kênh: `{lec.get('teacher_channel')}`")
                    lec_url = lec.get("youtube_url")
                    if lec_url:
                        st.video(lec_url)
                        st.link_button("🌐 Mở xem trên YouTube", lec_url, use_container_width=True)
                    st.info(f"📌 {lec.get('description')}")
                    
                with col_v2:
                    st.markdown("##### 🔬 Clip quay thí nghiệm thực tế")
                    exp = lesson_media.get("experiment", {})
                    st.markdown(f"**{exp.get('title')}**")
                    st.caption("Thí nghiệm quay cận cảnh hiện tượng")
                    exp_url = exp.get("youtube_url")
                    if exp_url:
                        st.video(exp_url)
                        st.link_button("🌐 Mở xem trên YouTube", exp_url, use_container_width=True)
                    st.success(f"✨ {exp.get('description')}")

    # ----- THẺ 3: ĐỌC THÊM SGK -----
    with subtab3:
        st.markdown("#### 📖 Đọc Thêm Sách Giáo Khoa (Kết Nối Tri Thức)")
        st.caption("Toàn bộ nội dung văn bản bóc tách từ SGK kèm hình ảnh sơ đồ, bảng biểu minh họa đầy đủ.")
        with st.expander("📖 Xem toàn bộ nội dung sách giáo khoa KNTT", expanded=False):
            st.markdown(content_md, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Bước tiếp theo:** Hãy chuyển sang tab **'🫧 Thí Nghiệm & Hiện Tượng Kỳ Thú'** để khám phá các bí mật đời sống và thực hành phòng thí nghiệm ảo nhé! 🐾")

# ================= TAB 2: THÍ NGHIỆM & HIỆN TƯỢNG THỰC TẾ =================
with tab2:
    st.markdown("### 🫧 Thí Nghiệm Sống Động & Giải Mã Hiện Tượng Đời Sống 🔬✨")
    st.caption("Cùng lật mở những bí mật kỳ thú của tự nhiên quanh ta nào các bạn nhỏ ơi! 🐱🐾")
    
    # 1. Nhúng mô phỏng PhET nếu có
    sim_data = PHET_SIMS.get(current_lesson["file"])
    if sim_data:
        st.markdown(f"#### 🎮 Phòng Thí Nghiệm Ảo: {sim_data['title']} ✨")
        st.markdown(f"*{sim_data['description']}*")
        st.info(f"👉 **Hướng dẫn thao tác cho bé:** {sim_data['guide']}")
        
        # Nhúng an toàn iframe PhET (sửa triệt để lỗi unexpected keyword argument 'scrolling')
        try:
            if hasattr(st, "iframe"):
                st.iframe(sim_data["sim_url"], height=520)
            else:
                components.iframe(sim_data["sim_url"], height=520, scrolling=False)
        except Exception:
            try:
                components.iframe(sim_data["sim_url"], height=520)
            except Exception:
                st.warning("Trình duyệt không hỗ trợ nhúng trực tiếp, vui lòng mở liên kết dưới đây.")
        
        st.link_button("🌐 Mở toàn màn hình mô phỏng PhET", sim_data["sim_url"])
        st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 2px dashed #38bdf8;'>", unsafe_allow_html=True)
        
    # 2. Các hiện tượng thực tế chuyên sâu
    phenomena_list = REAL_PHENOMENA.get(current_lesson["file"], [])
    if phenomena_list:
        st.markdown("#### 🌍 Giải Mã Hiện Tượng Đời Thường Cùng Bác Học 🪄")
        for idx, p in enumerate(phenomena_list, 1):
            with st.container():
                st.markdown(f"""
                <div class="phenomenon-card">
                    <h3 style="color: #0284c7; margin-top: 0;">💡 {p['title']} ✨</h3>
                    <p style="font-size: 1.05rem; color: #334155;"><strong>❓ Câu hỏi tò mò:</strong> {p['question']}</p>
                    <p style="color: #475569;"><strong>👁️ Hiện tượng quan sát được:</strong> {p['observation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"🔍 Bấm để xem Bác học giải mã Cơ chế Khoa học của {p['title']} 🪄", expanded=(idx == 1)):
                    st.markdown(p["mechanism"])
                    st.markdown("---")
                    st.markdown(p["application_safety"])
    else:
        st.info("Hiện tượng thực tế của bài học này đang được tổng hợp và hiển thị trực tiếp trong Tab 1.")

# ================= TAB 3: LUYỆN TẬP & TỰ CHẤM ĐIỂM =================
with tab3:
    st.markdown("### 🎮 Đấu Trường Trắc Nghiệm & Luyện Tập SGK 🏆✨")
    st.caption("Cùng rèn luyện kỹ năng, săn sao may mắn ⭐ và trở thành Nhà Khoa Học Nhí tài ba nào các bạn nhỏ ơi! 🐱🐾")
    
    ex_mode = st.radio(
        "Lựa chọn thử thách:",
        [
            "📚 Bài Tập SGK Kết Nối Tri Thức ✏️",
            "🌟 5 Bài Tập Tự Luyện Mở Rộng Ngoài SGK 🚀",
            "🎯 Đấu Trường Trắc Nghiệm 5 Câu (Săn Sao ⭐)"
        ],
        horizontal=True,
        key=f"khtn_mode_{current_lesson['id']}"
    )
    st.markdown("---")
    
    # ---------------- CHẾ ĐỘ 1: BÀI TẬP SGK ----------------
    if "Bài Tập SGK" in ex_mode:
        st.markdown("#### 📚 Toàn Bộ Bài Tập SGK Kết Nối Tri Thức ✏️")
        st.info("💡 **Lời khuyên từ Bác học Newton & Marie Curie:** Bé hãy tự thử sức giải hoặc nháp vào cuốn sổ bên dưới trước khi bấm xem hướng dẫn để rèn luyện trí tuệ siêu việt nhé! 🌟")
        
        sgk_list = SGK_SOLUTIONS.get(current_lesson["file"], [])
        if sgk_list:
            st.caption(f"Bài học này có **{len(sgk_list)} bài tập SGK chuẩn mực** kèm lời giải chi tiết 4 bước.")
            for idx, ex in enumerate(sgk_list, 1):
                with st.container():
                    st.markdown(f"#### 📝 {ex.get('title', f'Bài tập {idx}')}")
                    st.markdown(f"**Đề bài:**\n\n{ex.get('problem', '')}")
                    
                    st.text_area(
                        "✏️ Cuốn Sổ Nháp Xinh Xắn Của Bé 📝:",
                        placeholder="Bé hãy viết công thức, đổi số mol hoặc ghi các bước tính toán tại đây nha...",
                        key=f"khtn_draft_{current_lesson['id']}_{ex.get('id', idx)}",
                        height=90
                    )
                    
                    with st.expander("💡 Xem hướng dẫn giải 4 bước chi tiết cùng Bác học 🪄", expanded=False):
                        if ex.get("method"):
                            st.markdown("**🔍 Phương pháp tư duy:**")
                            st.info(ex["method"])
                        
                        steps = ex.get("steps", [])
                        if steps:
                            st.markdown("**📝 Các bước giải chi tiết:**")
                            for step in steps:
                                st.markdown(step)
                            
                        if ex.get("conclusion"):
                            st.success(f"**🎯 Kết luận cuối cùng:** {ex['conclusion']}")
                    
                    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 2px dashed #bae6fd;'>", unsafe_allow_html=True)
        else:
            st.info("Hệ thống bài tập SGK của bài học này đang được chuẩn bị.")

    # ---------------- CHẾ ĐỘ 2: 5 BÀI TẬP TỰ LUYỆN MỞ RỘNG NGOÀI SGK ----------------
    elif "Tự Luyện Mở Rộng" in ex_mode:
        st.markdown("#### 🌟 5 Bài Tập Tự Luyện & Mở Rộng Ngoài SGK (Kèm Lời Giải 4 Bước) 🚀")
        st.caption("Bộ 5 bài tập phát triển tư duy khoa học, gắn liền đời sống và nâng cao điểm số được Bác học Newton & Marie Curie tuyển chọn riêng cho bài học này.")
        st.info("💡 **Bí kíp điểm 10:** Bé hãy tự giác suy nghĩ, viết tóm tắt dữ kiện và nháp lời giải vào cuốn sổ bên dưới trước khi mở xem hướng dẫn chi tiết 4 bước nhé! 🐾")

        practice_list = EXTRA_PRACTICE_PROBLEMS.get(current_lesson["file"], [])
        if practice_list:
            for idx, ex in enumerate(practice_list, 1):
                with st.container():
                    lvl = ex.get("level", "Cơ bản")
                    if "Cơ bản" in lvl:
                        b_color = "#10b981"
                        b_bg = "#ecfdf5"
                        icon = "🟢"
                    elif "Thông hiểu" in lvl:
                        b_color = "#0284c7"
                        b_bg = "#e0f2fe"
                        icon = "🟡"
                    elif "Vận dụng" in lvl:
                        b_color = "#d97706"
                        b_bg = "#fef3c7"
                        icon = "🟠"
                    else:
                        b_color = "#e11d48"
                        b_bg = "#ffe4e6"
                        icon = "🔴"

                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-top: 1.2rem; margin-bottom: 0.6rem;">
                        <span style="font-size: 1.18rem; font-weight: 800; color: #1e293b;">📝 {ex.get('title', f'Bài tập {idx}')}</span>
                        <span style="background: {b_bg}; color: {b_color}; padding: 4px 14px; border-radius: 9999px; font-weight: 800; font-size: 0.85rem; border: 1.5px solid {b_color}44;">{icon} {lvl}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"**Đề bài:**\n\n{ex.get('problem', '')}")

                    st.text_area(
                        "✏️ Cuốn Sổ Nháp Của Bé 📝:",
                        placeholder="Bé hãy viết công thức, tóm tắt bài toán hoặc nháp lời giải tại đây trước khi xem gợi ý nha...",
                        key=f"draft_extra_{current_lesson['id']}_{ex.get('id', idx)}",
                        height=85
                    )

                    with st.expander("💡 Xem hướng dẫn giải 4 bước chi tiết cùng Bác học 🪄", expanded=False):
                        if ex.get("method"):
                            st.markdown("**🔍 Phương pháp tư duy khoa học:**")
                            st.info(ex["method"])

                        steps = ex.get("steps", [])
                        if steps:
                            st.markdown("**📝 4 bước giải chi tiết chuẩn mực:**")
                            for step in steps:
                                st.markdown(step)

                        if ex.get("conclusion"):
                            st.success(f"**🎯 Kết luận cuối cùng:** {ex['conclusion']}")

                    done_key = f"done_prob_{current_lesson['id']}_{ex.get('id', idx)}"
                    if st.checkbox("✅ Em đã tự giải và hiểu rõ bài tập này! (+5 ⭐)", key=done_key):
                        st.caption("🎉 Hoan hô bé! Bé đã xuất sắc tích lũy thêm 5 sao vào sổ tay khoa học!")

                    st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 2px dashed #bae6fd;'>", unsafe_allow_html=True)
        else:
            st.info("Hệ thống 5 bài tập rèn luyện cho bài học này đang được chuẩn bị.")

    # ---------------- CHẾ ĐỘ 3: ĐẤU TRƯỜNG TRẮC NGHIỆM ----------------
    else:
        st.markdown("#### 🎯 Đấu Trường Trắc Nghiệm Phân Hạng (5 Câu Ngẫu Nhiên) 🌟")
        st.caption("Bộ đề rút cân bằng: 2 Dễ (Nhận biết) • 2 Vừa (Thông hiểu) • 1 Thử thách (Vận dụng) kèm đồng hồ tính giờ.")
        
        bank = EXTRA_EXERCISES.get(current_lesson["file"], [])
        if bank:
            q_set_key = f"khtn_qset_{current_lesson['id']}"
            q_time_key = f"khtn_qtime_{current_lesson['id']}"
            q_sub_key = f"khtn_qsub_{current_lesson['id']}"
            
            if q_set_key not in st.session_state:
                de_list = [q for q in bank if q.get("level") == "Dễ"]
                vua_list = [q for q in bank if q.get("level") == "Vừa"]
                kho_list = [q for q in bank if q.get("level") == "Thử thách"]
                
                selected_q = []
                if len(de_list) >= 2 and len(vua_list) >= 2 and len(kho_list) >= 1:
                    selected_q = random.sample(de_list, 2) + random.sample(vua_list, 2) + random.sample(kho_list, 1)
                else:
                    selected_q = random.sample(bank, min(5, len(bank)))
                    
                st.session_state[q_set_key] = selected_q
                st.session_state[q_time_key] = time.time()
                st.session_state[q_sub_key] = None

            current_questions = st.session_state[q_set_key]
            
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                sub_data = st.session_state.get(q_sub_key)
                if not sub_data:
                    elapsed = int(time.time() - st.session_state[q_time_key])
                    st.markdown(f"⏱️ **Thời gian tranh tài:** `{elapsed // 60:02d}:{elapsed % 60:02d}` ⏳")
                else:
                    st.markdown("🏁 **Đã hoàn thành xuất sắc lượt thi đấu!** ✨")
            with col_btn:
                if st.button("🔄 Tạo Đề Mới 🎲", key=f"btn_reset_{current_lesson['id']}", use_container_width=True):
                    del st.session_state[q_set_key]
                    if q_sub_key in st.session_state:
                        del st.session_state[q_sub_key]
                    st.rerun()

            st.markdown("---")
            user_choices = {}
            for i, q in enumerate(current_questions, 1):
                level_badge = "🟢 Dễ Như Ăn Kẹo 🍬" if q.get("level") == "Dễ" else ("🟡 Thử Thách Vừa Sức 🌟" if q.get("level") == "Vừa" else "🔴 Siêu Thử Thách 🚀")
                st.markdown(f"**Câu {i}** ({level_badge}): {q['question']}")
                
                choice = st.radio(
                    f"Chọn đáp án cho câu {i}:",
                    range(len(q["options"])),
                    format_func=lambda idx, opts=q["options"]: opts[idx],
                    key=f"khtn_choice_{current_lesson['id']}_{q['id']}",
                    index=None,
                    label_visibility="collapsed"
                )
                user_choices[q["id"]] = choice
                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

            if not st.session_state.get(q_sub_key):
                if st.button("🚀 Nộp Bài & Nhận Sao Thưởng ⭐", type="primary", key=f"btn_sub_{current_lesson['id']}", use_container_width=True):
                    duration = int(time.time() - st.session_state[q_time_key])
                    correct = sum(1 for q in current_questions if user_choices.get(q["id"]) == q["correct"])
                    total = len(current_questions)
                    score = round((correct / total) * 10.0, 1)
                    
                    db.save_quiz_result(current_lesson["id"], score, correct, total, duration)
                    if score >= 7.0:
                        db.mark_lesson_completed(current_lesson["id"], current_lesson["title"])
                        
                    st.session_state[q_sub_key] = {
                        "score_10": score,
                        "correct_count": correct,
                        "total_count": total,
                        "duration_sec": duration,
                        "choices": user_choices
                    }
                    st.rerun()

            sub_res = st.session_state.get(q_sub_key)
            if sub_res:
                sc = sub_res["score_10"]
                cor = sub_res["correct_count"]
                tot = sub_res["total_count"]
                dur = sub_res["duration_sec"]
                dur_m = dur // 60
                dur_s = dur % 60
                user_ans = sub_res["choices"]
                
                st.markdown("---")
                if sc >= 7.0:
                    st.balloons()
                    st.success(f"🎉 **OA XUẤT SẮC QUÁ BÉ ƠI!** 🌟 Bé đạt **{sc}/10 điểm** ({cor}/{tot} câu đúng) trong thời gian **{dur_m:02d} phút {dur_s:02d} giây**! Bé đã mở khóa danh hiệu Nhà Khoa Học Nhí 🏅 và hoàn thành bài học này rồi nha! ✅✨")
                else:
                    st.warning(f"💪 **CỐ GẮNG LÊN NÀO BẠN NHỎ ƠI!** 🐾 Bé đạt **{sc}/10 điểm** ({cor}/{tot} câu đúng) trong thời gian **{dur_m:02d} phút {dur_s:02d} giây**. Thầy Newton bảo: *'Mỗi lần thử sai là một lần ta tiến gần hơn tới chân lý!'*. Bé hãy đọc kỹ phần giải thích bên dưới rồi bấm '🔄 Tạo Đề Mới 🎲' để lấy điểm 10 nha! 🌈")

                st.markdown("#### 📖 Hướng Dẫn & Đáp Án Chi Tiết Cùng Bác Học:")
                for i, q in enumerate(current_questions, 1):
                    chosen = user_ans.get(q["id"])
                    is_cor = (chosen == q["correct"])
                    icon = "🌟" if is_cor else "❌"
                    lvl = q.get("level", "Vừa")
                    with st.expander(f"{icon} Câu {i} ({lvl}): {q['options'][q['correct']]}", expanded=not is_cor):
                        if not is_cor:
                            st.markdown(f"❌ **Lựa chọn của bé:** {q['options'][chosen] if chosen is not None else 'Chưa chọn'}")
                        st.markdown(f"✅ **Đáp án chính xác:** {q['options'][q['correct']]}")
                        st.markdown(f"**🔍 Lời giải thích khoa học:**\n\n{q['explanation']}")
        else:
            st.info("Ngân hàng câu hỏi trắc nghiệm của bài học này đang được chuẩn bị.")

# ================= TAB 4: GIA SƯ AI NEWTON & MARIE CURIE =================
with tab4:
    st.markdown("### 🪄 Góc Đối Thoại Socratic: Cô Marie Curie & Thầy Isaac Newton 👩‍🔬🍎")
    st.caption("Đối thoại hai chiều gợi mở tư duy khoa học: Em trả lời câu hỏi của Thầy/Cô để tự mình tìm ra kho báu tri thức nhé! 🌟")
    
    session_chat_key = f"khtn_chat_{current_lesson['id']}"
    if session_chat_key not in st.session_state:
        st.session_state[session_chat_key] = [
            {
                "role": "assistant",
                "content": f"Xin chào bạn nhỏ say mê khám phá! 🌟 Cô **Marie Curie** 👩‍🔬 và Thầy **Isaac Newton** 🍎 rất vui được đồng hành cùng em trong bài học **{current_lesson['title']}**.\n\nCó điều gì kỳ thú hay phương trình/bài tập nào làm em băn khoăn không? Cứ thủ thỉ cùng chúng ta nhé! 🐾🔬"
            }
        ]
        
    # Thanh công cụ đối thoại: Chọn người đồng hành & Nút làm mới
    col_tutor_role, col_tutor_reset = st.columns([3, 1])
    with col_tutor_role:
        tutor_partner = st.radio(
            "🌟 Chọn Bác học em muốn trò chuyện cùng:",
            ["👩‍🔬 Cô Marie Curie (Hóa học & PTHH)", "🍎 Thầy Isaac Newton (Vật lý & Tự nhiên)", "🪄 Cả hai Bác học cùng đồng hành"],
            horizontal=True,
            key=f"khtn_partner_{current_lesson['id']}"
        )
    with col_tutor_reset:
        if st.button("🔄 Cuộc đối thoại mới", key=f"khtn_reset_chat_{current_lesson['id']}", use_container_width=True):
            st.session_state[session_chat_key] = [
                {
                    "role": "assistant",
                    "content": f"Xin chào em! Cô **Marie Curie** 👩‍🔬 và Thầy **Isaac Newton** 🍎 đã sẵn sàng cho một bài tập/câu hỏi mới trong **{current_lesson['title']}**. Hãy chia sẻ cùng Thầy Cô nhé!"
                }
            ]
            st.rerun()

    partner_code = "curie" if "Curie" in tutor_partner else ("newton" if "Newton" in tutor_partner else "all")

    # Hiển thị toàn bộ lịch sử đối thoại dạng Chat Message
    for msg in st.session_state[session_chat_key]:
        if msg["role"] == "assistant":
            # Chọn avatar tương ứng
            if "Curie" in msg["content"] or partner_code == "curie":
                avatar_icon = "👩‍🔬"
            elif "Newton" in msg["content"] or partner_code == "newton":
                avatar_icon = "🍎"
            else:
                avatar_icon = "🪄"
            with st.chat_message("assistant", avatar=avatar_icon):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(msg["content"])

    # Phân tích tin nhắn gần nhất để hiển thị các nút trả lời nhanh (Quick Response Pills)
    last_assistant_msg = ""
    for m in reversed(st.session_state[session_chat_key]):
        if m["role"] == "assistant":
            last_assistant_msg = m["content"].lower()
            break

    st.markdown("<hr style='margin: 1.2rem 0 0.8rem 0; border: none; border-top: 1px dashed #bae6fd;'>", unsafe_allow_html=True)
    st.markdown("##### 💡 Em hãy chọn nhanh câu trả lời hoặc gõ trực tiếp bên dưới:")

    quick_action_clicked = None
    
    # Kịch bản 1: Hỏi về BCNN của 2 và 3 hoặc đặt hệ số trước HCl (như Al + HCl)
    if any(k in last_assistant_msg for k in ["bội chung nhỏ nhất", "bội chung", "chia hết cho 3", "chia hết cho 2", "bao nhiêu vào trước hcl"]):
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔢 Số 6 cô ơi (BCNN của 2 và 3)! 🌟", key=f"btn_bcnn_6_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Dạ là số 6 cô ơi (bội chung nhỏ nhất của 2 và 3 là 6)!"
        with c2:
            if st.button("🔢 Em đặt hệ số 6 trước HCl ạ!", key=f"btn_hcl_6_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Em đặt hệ số 6 trước HCl ở vế trái cô nhé!"
        with c3:
            if st.button("🤔 Em chưa hiểu, cô gợi ý thêm đi ạ!", key=f"btn_hint_bcnn_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Em chưa hiểu đoạn này, cô Marie Curie gợi ý thêm một chút nữa cho em với ạ!"
    
    # Kịch bản 2: Hỏi về hệ số trước H2 và AlCl3
    elif any(k in last_assistant_msg for k in ["hệ số mấy để được 6h", "hệ số mấy để được 6cl", "nhìn sang vế phải"]):
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔢 Đặt 3 trước H₂ và 2 trước AlCl₃ cô ơi! 🌟", key=f"btn_coeff_3_2_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Dạ đặt hệ số 3 trước H₂ và hệ số 2 trước AlCl₃ cô ạ!"
        with c2:
            if st.button("🔢 Em cân bằng xong: 2Al + 6HCl → 2AlCl₃ + 3H₂ 🎉", key=f"btn_full_eq_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Em cân bằng xong toàn bộ phương trình rồi: 2Al + 6HCl → 2AlCl₃ + 3H₂ ạ!"
        with c3:
            if st.button("🤔 Cô hướng dẫn em tính 6 : 2 và 6 : 3 với ạ!", key=f"btn_calc_help_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Cô hướng dẫn em cách chia hệ số 6 cho 2 và 3 với ạ!"

    # Kịch bản 3: Hỏi về hệ số Al cuối cùng
    elif any(k in last_assistant_msg for k in ["trước al ở vế trái", "nguyên tố cuối cùng là nhôm"]):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🎉 Đặt hệ số 2 trước Al cô ơi! (2Al + 6HCl → 2AlCl₃ + 3H₂)", key=f"btn_al_2_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Dạ ta đặt hệ số 2 trước Al để hoàn thành phương trình: 2Al + 6HCl → 2AlCl₃ + 3H₂ cô nhé!"
        with c2:
            if st.button("✨ Cho em thử một phương trình mới đi cô!", key=f"btn_new_eq_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Em hiểu rồi! Cô Curie cho em một phương trình mới để em tự cân bằng thử nhé!"

    # Kịch bản tổng quát / mở đầu
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⚗️ Cô Curie: Hướng dẫn em cân bằng PTHH! 🫧", key=f"khtn_q_chem_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Cô Marie Curie ơi, cô hướng dẫn em phương pháp cân bằng phương trình hoá học từng bước với ạ!"
        with c2:
            if st.button("🍎 Thầy Newton: Giải mã bí mật hiện tượng này! 🧲", key=f"khtn_q_phy_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Thầy Newton ơi, thầy giải thích bản chất hiện tượng thực tế của bài học này giúp em với ạ!"
        with c3:
            if st.button("📖 Thầy Cô gợi ý phương pháp giải bài tập SGK! ✏️", key=f"khtn_q_sgk_{current_lesson['id']}", use_container_width=True):
                quick_action_clicked = "Xin Thầy Cô gợi ý phương pháp tư duy để giải các bài tập trong bài học này cho em với ạ!"

    # Khung nhập câu trả lời trực tiếp NGAY BÊN DƯỚI BONG BÓNG TIN NHẮN
    with st.form(key=f"khtn_direct_dialogue_form_{current_lesson['id']}", clear_on_submit=True):
        col_inp, col_btn = st.columns([4, 1])
        with col_inp:
            direct_reply_text = st.text_input(
                "💬 Em trả lời câu hỏi của Cô Curie / Thầy Newton tại đây:",
                placeholder="💬 Gõ câu trả lời của em tại đây (ví dụ: số 6 cô ơi!, hoặc thắc mắc của em)...",
                label_visibility="collapsed"
            )
        with col_btn:
            send_clicked = st.form_submit_button("🚀 Gửi Trả Lời", use_container_width=True)

    bottom_chat_text = st.chat_input("Hoặc nhập câu hỏi tại đây... 💬")

    # Xác định nội dung học sinh phản hồi
    active_user_input = None
    if send_clicked and direct_reply_text and direct_reply_text.strip():
        active_user_input = direct_reply_text.strip()
    elif quick_action_clicked:
        active_user_input = quick_action_clicked
    elif bottom_chat_text and bottom_chat_text.strip():
        active_user_input = bottom_chat_text.strip()

    if active_user_input:
        st.session_state[session_chat_key].append({"role": "user", "content": active_user_input})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(active_user_input)

        resp_avatar = "👩‍🔬" if partner_code == "curie" else ("🍎" if partner_code == "newton" else "🪄")
        with st.chat_message("assistant", avatar=resp_avatar):
            stream_gen = ai_tutor.generate_tutor_stream(
                api_key=api_key_input,
                lesson_title=current_lesson["title"],
                lesson_summary=content_md[:800],
                chat_history=st.session_state[session_chat_key],
                user_message=active_user_input,
                model_name=model_code,
                character=partner_code
            )
            reply_text = st.write_stream(stream_gen)

        st.session_state[session_chat_key].append({"role": "assistant", "content": reply_text})
        st.rerun()
