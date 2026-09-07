import sqlite3
import os
import datetime
from typing import Dict, Any, List

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "khtn8_progress.db")

def get_connection():
    """Tạo kết nối SQLite đa luồng an toàn với timeout 20s cho Streamlit Cloud"""
    conn = sqlite3.connect(DB_NAME, timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Khởi tạo bảng quản lý tiến độ và kết quả học tập"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Bảng theo dõi tiến độ bài học
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                lesson_id TEXT PRIMARY KEY,
                lesson_title TEXT,
                status TEXT DEFAULT 'not_started',
                last_accessed TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Bảng lưu kết quả trắc nghiệm Đấu trường
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id TEXT,
                score_10 REAL,
                correct_count INTEGER,
                total_count INTEGER,
                duration_sec INTEGER,
                submitted_at TIMESTAMP
            )
        """)
        
        # Bảng theo dõi chuỗi ngày học liên tục (streak)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_date DATE UNIQUE,
                activities_count INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()

def record_activity():
    """Ghi nhận hoạt động học tập hôm nay để tính chuỗi ngày học liên tục (streak)"""
    today = datetime.date.today().isoformat()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_log (activity_date, activities_count)
                VALUES (?, 1)
                ON CONFLICT(activity_date) DO UPDATE SET activities_count = activities_count + 1
            """, (today,))
            conn.commit()
    except Exception:
        pass

def mark_lesson_in_progress(lesson_id: str, lesson_title: str):
    """Đánh dấu học sinh bắt đầu học bài này"""
    record_activity()
    now = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM lesson_progress WHERE lesson_id = ?", (lesson_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                INSERT INTO lesson_progress (lesson_id, lesson_title, status, last_accessed)
                VALUES (?, ?, 'in_progress', ?)
            """, (lesson_id, lesson_title, now))
        else:
            if row["status"] != "completed":
                cursor.execute("""
                    UPDATE lesson_progress 
                    SET status = 'in_progress', last_accessed = ?
                    WHERE lesson_id = ?
                """, (now, lesson_id))
            else:
                cursor.execute("""
                    UPDATE lesson_progress 
                    SET last_accessed = ?
                    WHERE lesson_id = ?
                """, (now, lesson_id))
        conn.commit()

def mark_lesson_completed(lesson_id: str, lesson_title: str):
    """Đánh dấu bài học đã hoàn thành khi đạt điểm >= 7.0 trên Đấu trường"""
    record_activity()
    now = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lesson_progress (lesson_id, lesson_title, status, last_accessed, completed_at)
            VALUES (?, ?, 'completed', ?, ?)
            ON CONFLICT(lesson_id) DO UPDATE SET
                status = 'completed',
                last_accessed = ?,
                completed_at = COALESCE(completed_at, ?)
        """, (lesson_id, lesson_title, now, now, now, now))
        conn.commit()

def save_quiz_result(lesson_id: str, score_10: float, correct_count: int, total_count: int, duration_sec: int):
    """Lưu kết quả làm bài trắc nghiệm vào cơ sở dữ liệu"""
    record_activity()
    now = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quiz_results (lesson_id, score_10, correct_count, total_count, duration_sec, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lesson_id, score_10, correct_count, total_count, duration_sec, now))
        conn.commit()

def get_all_progress() -> Dict[str, Dict[str, Any]]:
    """Lấy danh sách trạng thái học tập của tất cả các bài học"""
    progress = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lesson_progress")
        for row in cursor.fetchall():
            progress[row["lesson_id"]] = {
                "status": row["status"],
                "last_accessed": row["last_accessed"],
                "completed_at": row["completed_at"]
            }
    return progress

def get_student_stats(total_lessons: int) -> Dict[str, Any]:
    """Tính toán thống kê: chuỗi ngày học (streak), tổng điểm, số bài hoàn thành, tỉ lệ hoàn thành"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Đếm số bài đã hoàn thành
        cursor.execute("SELECT COUNT(*) as count FROM lesson_progress WHERE status = 'completed'")
        completed_count = cursor.fetchone()["count"]
        
        # Tính tổng điểm tích lũy từ kết quả bài test
        cursor.execute("SELECT SUM(score_10) as total_pts FROM quiz_results")
        row = cursor.fetchone()
        total_points = row["total_pts"] if row and row["total_pts"] else 0.0
        
        # Tính chuỗi streak (các ngày liên tiếp có học tính từ hôm nay trở về trước)
        cursor.execute("SELECT activity_date FROM activity_log ORDER BY activity_date DESC")
        dates = [r["activity_date"] for r in cursor.fetchall()]
        
        streak = 0
        today = datetime.date.today()
        current_check = today
        
        date_set = set(dates)
        # Nếu hôm nay chưa học thì kiểm tra từ hôm qua
        if today.isoformat() not in date_set:
            current_check = today - datetime.timedelta(days=1)
            
        while current_check.isoformat() in date_set:
            streak += 1
            current_check -= datetime.timedelta(days=1)
            
        rate = round((completed_count / total_lessons * 100), 1) if total_lessons > 0 else 0.0
        
        return {
            "completed_count": completed_count,
            "completion_rate": rate,
            "total_points": total_points,
            "streak": streak
        }
