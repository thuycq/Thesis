# ==============================================================================
# IMPORTS_AND_CONFIG
# ==============================================================================

import streamlit as st
import sqlite3
import pandas as pd


DB_PATH = "data/kltn.db"


# ==============================================================================
# DATABASE_AND_SCHEMA
# ==============================================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_bctt_rubric_columns():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        "nktt_1",
        "nktt_2",
        "nktt_3",
        "nktt_4",
        "nktt_5",
        "bctt_1",
        "bctt_2",
        "bctt_3",
        "bctt_4",
        "bctt_5"
    ]

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} REAL")

    conn.commit()
    conn.close()


def ensure_kltn_gvhd_rubric_columns():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        "gvhd_tc1",
        "gvhd_tc2",
        "gvhd_tc3",
        "gvhd_tc4"
    ]

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} REAL")

    conn.commit()
    conn.close()


def ensure_kltn_gvpb_rubric_columns():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        "gvpb_tc1",
        "gvpb_tc2",
        "gvpb_tc3",
        "gvpb_tc4",
        "gvpb_tc5"
    ]

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} REAL")

    conn.commit()
    conn.close()


def ensure_kltn_cthd_rubric_columns():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        "cthd_tc1",
        "cthd_tc2",
        "cthd_tc3",
        "cthd_tc4",
        "cthd_tc5",
        "cthd_tc6",
        "cthd_bonus"
    ]

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} REAL")

    conn.commit()
    conn.close()


def ensure_kltn_tvhd_rubric_columns():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        "tvhd_tc1",
        "tvhd_tc2",
        "tvhd_tc3",
        "tvhd_tc4",
        "tvhd_tc5",
        "tvhd_tc6",
        "tvhd_bonus"
    ]

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} REAL")

    conn.commit()
    conn.close()


def ensure_kltn_tkhd_rubric_columns():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_columns = [
        "tkhd_tc1",
        "tkhd_tc2",
        "tkhd_tc3",
        "tkhd_tc4",
        "tkhd_tc5",
        "tkhd_tc6",
        "tkhd_bonus",
        "council_comment"
    ]

    for col in new_columns:
        if col not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col} REAL" if col != "council_comment" else f"ALTER TABLE students ADD COLUMN {col} TEXT")

    conn.commit()
    conn.close()


# ==============================================================================
# GENERAL_UTILITIES
# ==============================================================================

def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def is_english_language(value):
    text = normalize_text(value)

    english_keywords = [
        "TIẾNG ANH",
        "TIENG ANH",
        "ENGLISH",
        "ANH",
        "EN"
    ]

    return any(keyword in text for keyword in english_keywords)


def detect_base_class_group(class_name):
    cls = normalize_text(class_name)

    if "404" in cls:
        return "404"
    if "412" in cls:
        return "412"
    if "414" in cls:
        return "414"

    return None


def get_workload_bucket(class_name, language_value):
    cls = normalize_text(class_name)
    base_group = detect_base_class_group(cls)

    if "CA" in cls:
        return "CA"

    if base_group is None:
        return None

    if cls.endswith("E"):
        return f"{base_group}E" if base_group in ["404", "414"] else None

    if cls.endswith("C"):
        return f"{base_group}C_EN" if is_english_language(language_value) else f"{base_group}C_VI"

    if cls.endswith("H"):
        return f"{base_group}H_EN" if is_english_language(language_value) else f"{base_group}H_VI"

    return base_group


WORKLOAD_BUCKETS = [
    ("404", "404"),
    ("412", "412"),
    ("414", "414"),
    ("404C_VI", "404C-VI"),
    ("404C_EN", "404C-EN"),
    ("414C_VI", "414C-VI"),
    ("414C_EN", "414C-EN"),
    ("404H_VI", "404H-VI"),
    ("404H_EN", "404H-EN"),
    ("414H_VI", "414H-VI"),
    ("414H_EN", "414H-EN"),
    ("404E", "404E"),
    ("414E", "414E"),
    ("CA", "CA")
]


# ==============================================================================
# AUTH_AND_USER_MANAGEMENT
# ==============================================================================

def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, role, lecturer_id FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    return user


def get_lecturer_by_id(lecturer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, lecturer_code, full_name, email, department
        FROM lecturers
        WHERE id = ?
    """, (lecturer_id,))

    lecturer = cursor.fetchone()
    conn.close()

    return lecturer


def add_lecturer(lecturer_code, full_name, email, department):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lecturers (lecturer_code, full_name, email, department)
        VALUES (?, ?, ?, ?)
    """, (lecturer_code, full_name, email, department))

    conn.commit()
    conn.close()


def get_all_lecturers():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM lecturers ORDER BY id DESC", conn)
    conn.close()
    return df


def create_lecturer_account(username, password, lecturer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password, role, lecturer_id)
        VALUES (?, ?, 'lecturer', ?)
    """, (username, password, lecturer_id))

    conn.commit()
    conn.close()


# ==============================================================================
# IMPORT_AND_ADMIN_DATA_ACCESS
# ==============================================================================

def import_students(df):

    conn = get_connection()
    cursor = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for _, row in df.iterrows():

        mssv = str(row["MSSV"]).strip()
        full_name = str(row["Họ tên SV"]).strip()
        class_name = str(row["Lớp"]).strip()
        gvhd_name = str(row["GVHD"]).strip()
        project_type = str(row["Loại"]).strip().upper()

        if project_type not in ["BCTT", "KLTN", "BC-KL"]:
            skipped_count = skipped_count + 1
            continue

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (gvhd_name,)
        )

        lecturer = cursor.fetchone()

        if lecturer:

            gvhd_id = lecturer[0]

            cursor.execute(
                """
                INSERT OR REPLACE INTO students (
                    mssv,
                    full_name,
                    class_name,
                    gvhd_id,
                    project_type
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    mssv,
                    full_name,
                    class_name,
                    gvhd_id,
                    project_type
                )
            )

            inserted_count = inserted_count + 1

        else:
            skipped_count = skipped_count + 1

    conn.commit()
    conn.close()

    return inserted_count, skipped_count


def import_bctt_submission_data(df):

    required_columns = ["MSSV", "Ngôn ngữ BCTT"]

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"Thiếu cột bắt buộc: {', '.join(missing_cols)}"

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0
    not_found_mssv = []

    for _, row in df.iterrows():
        mssv = str(row["MSSV"]).strip() if pd.notna(row["MSSV"]) else ""
        bctt_language = str(row["Ngôn ngữ BCTT"]).strip() if pd.notna(row["Ngôn ngữ BCTT"]) else None

        if not mssv:
            continue

        cursor.execute(
            """
            UPDATE students
            SET bctt_language = ?
            WHERE mssv = ?
            """,
            (bctt_language, mssv)
        )

        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found_mssv.append(mssv)

    conn.commit()
    conn.close()

    message = f"Đã cập nhật ngôn ngữ BCTT cho {updated_count} sinh viên."

    if not_found_mssv:
        message += f" Không tìm thấy {len(not_found_mssv)} MSSV: {', '.join(not_found_mssv[:10])}"
        if len(not_found_mssv) > 10:
            message += " ..."

    return True, message


def import_kltn_submission_data(df):

    required_columns = ["MSSV", "Tên đề tài", "Link bài", "Link Turnitin", "Ngôn ngữ KLTN"]

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"Thiếu cột bắt buộc: {', '.join(missing_cols)}"

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0
    not_found_mssv = []

    for _, row in df.iterrows():
        mssv = str(row["MSSV"]).strip() if pd.notna(row["MSSV"]) else ""

        topic_title = str(row["Tên đề tài"]).strip() if pd.notna(row["Tên đề tài"]) else None
        report_link = str(row["Link bài"]).strip() if pd.notna(row["Link bài"]) else None
        turnitin_link = str(row["Link Turnitin"]).strip() if pd.notna(row["Link Turnitin"]) else None
        kltn_language = str(row["Ngôn ngữ KLTN"]).strip() if pd.notna(row["Ngôn ngữ KLTN"]) else None

        if not mssv:
            continue

        cursor.execute(
            """
            UPDATE students
            SET topic_title = ?,
                report_link = ?,
                turnitin_link = ?,
                kltn_language = ?
            WHERE mssv = ?
              AND project_type IN ('KLTN', 'BC-KL')
            """,
            (topic_title, report_link, turnitin_link, kltn_language, mssv)
        )

        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found_mssv.append(mssv)

    conn.commit()
    conn.close()

    message = f"Đã cập nhật thông tin KLTN cho {updated_count} sinh viên."

    if not_found_mssv:
        message += f" Không tìm thấy {len(not_found_mssv)} MSSV: {', '.join(not_found_mssv[:10])}"
        if len(not_found_mssv) > 10:
            message += " ..."

    return True, message


def import_kltn_details(df):

    conn = get_connection()
    cursor = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for _, row in df.iterrows():

        mssv = str(row["MSSV"]).strip()

        gvpb_name = str(row["GVPB"]).strip()
        cthd_name = str(row["CTHĐ"]).strip()
        tvhd_name = str(row["TVHĐ"]).strip()
        tkhd_name = str(row["TKHĐ"]).strip()

        defense_time = str(row["Thời gian"]).strip()
        room = str(row["Phòng"]).strip()
        council = str(row["Hội đồng"]).strip()

        cursor.execute(
            "SELECT id FROM students WHERE mssv = ?",
            (mssv,)
        )

        student = cursor.fetchone()

        if not student:
            skipped_count = skipped_count + 1
            continue

        student_id = student[0]

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (gvpb_name,)
        )
        gvpb = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (cthd_name,)
        )
        cthd = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (tvhd_name,)
        )
        tvhd = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (tkhd_name,)
        )
        tkhd = cursor.fetchone()

        if gvpb and cthd and tvhd and tkhd:

            gvpb_id = gvpb[0]
            cthd_id = cthd[0]
            tvhd_id = tvhd[0]
            tkhd_id = tkhd[0]

            cursor.execute(
                """
                INSERT OR REPLACE INTO kltn_details (
                    student_id,
                    gvpb_id,
                    cthd_id,
                    tvhd_id,
                    tkhd_id,
                    defense_time,
                    room,
                    council
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    gvpb_id,
                    cthd_id,
                    tvhd_id,
                    tkhd_id,
                    defense_time,
                    room,
                    council
                )
            )

            inserted_count = inserted_count + 1

        else:
            skipped_count = skipped_count + 1

    conn.commit()
    conn.close()

    return inserted_count, skipped_count


def get_admin_overview_data():

    conn = get_connection()

    query = """
        SELECT
            s.mssv AS "MSSV",
            s.full_name AS "Họ tên SV",
            s.class_name AS "Lớp",
            s.project_type AS "Loại môn đăng ký học",
            gvhd.full_name AS "GVHD",
            gvpb.full_name AS "PB",
            cthd.full_name AS "CT",
            tvhd.full_name AS "UV",
            tkhd.full_name AS "TK",
            s.topic_title AS "Tên đề tài",
            s.report_link AS "Link bài",
            s.turnitin_link AS "Link Turnitin",
            s.bctt_language AS "Ngôn ngữ BCTT",
            s.kltn_language AS "Ngôn ngữ KLTN",
            kd.council AS "Hội đồng",
            kd.defense_time AS "Thời gian",
            kd.room AS "Phòng",
            s.score_bctt AS "Điểm BCTT",
            s.score_gvhd AS "Điểm GVHD",
            s.score_gvpb AS "Điểm GVPB",
            s.score_cthd AS "Điểm CTHĐ",
            s.score_tvhd AS "Điểm UVHĐ",
            s.score_tkhd AS "Điểm TKHĐ",            
            CASE
                WHEN s.score_gvhd IS NOT NULL
                 AND s.score_gvpb IS NOT NULL
                 AND s.score_cthd IS NOT NULL
                 AND s.score_tvhd IS NOT NULL
                 AND s.score_tkhd IS NOT NULL
                THEN ROUND(
                    (s.score_gvhd + s.score_gvpb + s.score_cthd + s.score_tvhd + s.score_tkhd) / 5.0,
                    2
                )
                ELSE NULL
            END AS "Điểm KLTN",
            s.council_comment AS "Nhận xét hội đồng"
        FROM students s
        LEFT JOIN lecturers gvhd
            ON s.gvhd_id = gvhd.id
        LEFT JOIN kltn_details kd
            ON s.id = kd.student_id
        LEFT JOIN lecturers gvpb
            ON kd.gvpb_id = gvpb.id
        LEFT JOIN lecturers cthd
            ON kd.cthd_id = cthd.id
        LEFT JOIN lecturers tvhd
            ON kd.tvhd_id = tvhd.id
        LEFT JOIN lecturers tkhd
            ON kd.tkhd_id = tkhd.id
        ORDER BY s.mssv
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_admin_bcct_data():

    conn = get_connection()

    query = """
        SELECT
            s.mssv AS "MSSV",
            s.full_name AS "Họ tên SV",
            s.class_name AS "Lớp",
            gvhd.full_name AS "GVHD",
            s.bctt_language AS "Ngôn ngữ BCTT",
            s.score_bctt AS "Điểm BCTT"
        FROM students s
        LEFT JOIN lecturers gvhd
            ON s.gvhd_id = gvhd.id
        WHERE s.project_type IN ('BCTT','BC-KL')
        ORDER BY s.mssv
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_admin_kltn_data():

    conn = get_connection()

    query = """
        SELECT
            s.mssv AS "MSSV",
            s.full_name AS "Họ tên SV",
            s.class_name AS "Lớp",
            gvhd.full_name AS "GVHD",
            gvpb.full_name AS "PB",
            cthd.full_name AS "CT",
            tvhd.full_name AS "UV",
            tkhd.full_name AS "TK",
            s.topic_title AS "Tên đề tài",
            s.report_link AS "Link bài",
            s.turnitin_link AS "Link Turnitin",
            s.kltn_language AS "Ngôn ngữ KLTN",
            kd.council AS "Hội đồng",
            kd.defense_time AS "Thời gian",
            kd.room AS "Phòng",
            s.score_gvhd AS "Điểm GVHD",
            s.score_gvpb AS "Điểm GVPB",
            s.score_cthd AS "Điểm CTHĐ",
            s.score_tvhd AS "Điểm UVHĐ",
            s.score_tkhd AS "Điểm TKHĐ",
            CASE
                WHEN s.score_gvhd IS NOT NULL
                 AND s.score_gvpb IS NOT NULL
                 AND s.score_cthd IS NOT NULL
                 AND s.score_tvhd IS NOT NULL
                 AND s.score_tkhd IS NOT NULL
                THEN ROUND(
                    (s.score_gvhd + s.score_gvpb + s.score_cthd + s.score_tvhd + s.score_tkhd) / 5.0,
                    2
                )
                ELSE NULL
            END AS "Điểm KLTN"
        FROM students s
        LEFT JOIN lecturers gvhd
            ON s.gvhd_id = gvhd.id
        LEFT JOIN kltn_details kd
            ON s.id = kd.student_id
        LEFT JOIN lecturers gvpb
            ON kd.gvpb_id = gvpb.id
        LEFT JOIN lecturers cthd
            ON kd.cthd_id = cthd.id
        LEFT JOIN lecturers tvhd
            ON kd.tvhd_id = tvhd.id
        LEFT JOIN lecturers tkhd
            ON kd.tkhd_id = tkhd.id
        WHERE s.project_type IN ('KLTN','BC-KL')
        ORDER BY s.mssv
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_admin_council_data():

    conn = get_connection()

    query = """
        SELECT DISTINCT
            kd.council AS "Hội đồng",
            cthd.full_name AS "CTHĐ",
            tvhd.full_name AS "TVHĐ",
            tkhd.full_name AS "TKHĐ",
            kd.defense_time AS "Thời gian",
            kd.room AS "Phòng"
        FROM kltn_details kd
        LEFT JOIN lecturers cthd
            ON kd.cthd_id = cthd.id
        LEFT JOIN lecturers tvhd
            ON kd.tvhd_id = tvhd.id
        LEFT JOIN lecturers tkhd
            ON kd.tkhd_id = tkhd.id
        WHERE kd.council IS NOT NULL
        ORDER BY kd.council, kd.defense_time, kd.room
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_admin_workload_source_data():

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv,
            s.full_name,
            s.class_name,
            s.project_type,
            s.bctt_language,
            s.kltn_language,
            gvhd.full_name AS gvhd_name,
            gvpb.full_name AS gvpb_name,
            cthd.full_name AS cthd_name,
            tvhd.full_name AS tvhd_name,
            tkhd.full_name AS tkhd_name
        FROM students s
        LEFT JOIN lecturers gvhd
            ON s.gvhd_id = gvhd.id
        LEFT JOIN kltn_details kd
            ON s.id = kd.student_id
        LEFT JOIN lecturers gvpb
            ON kd.gvpb_id = gvpb.id
        LEFT JOIN lecturers cthd
            ON kd.cthd_id = cthd.id
        LEFT JOIN lecturers tvhd
            ON kd.tvhd_id = tvhd.id
        LEFT JOIN lecturers tkhd
            ON kd.tkhd_id = tkhd.id
        ORDER BY s.mssv
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        df = df.drop_duplicates(subset=["id"])

    return df


def get_admin_assignment_stats_data():

    df = get_admin_workload_source_data()

    if df.empty:
        return pd.DataFrame()

    lecturer_names = set()

    for col in [
        "gvhd_name",
        "gvpb_name",
        "cthd_name",
        "tvhd_name",
        "tkhd_name"
    ]:
        if col in df.columns:
            lecturer_names.update(
                [
                    str(name).strip()
                    for name in df[col].dropna().tolist()
                    if str(name).strip() != ""
                ]
            )

    lecturer_names = sorted(lecturer_names)

    if not lecturer_names:
        return pd.DataFrame()

    task_groups = [
        "Hướng dẫn BCTT",
        "Hướng dẫn KLTN",
        "Phản biện",
        "Chủ tịch HĐ",
        "Ủy viên HĐ",
        "Thư ký HĐ"
    ]

    bucket_display_map = {code: label for code, label in WORKLOAD_BUCKETS}

    columns = []
    for task in task_groups:
        for bucket_code, bucket_label in WORKLOAD_BUCKETS:
            columns.append((task, bucket_label))

    result = pd.DataFrame(
        0,
        index=lecturer_names,
        columns=pd.MultiIndex.from_tuples(columns),
        dtype=int
    )

    for _, row in df.iterrows():
        project_type = normalize_text(row.get("project_type", ""))
        class_name = row.get("class_name", "")

        gvhd_name = str(row.get("gvhd_name", "")).strip()
        gvpb_name = str(row.get("gvpb_name", "")).strip()
        cthd_name = str(row.get("cthd_name", "")).strip()
        tvhd_name = str(row.get("tvhd_name", "")).strip()
        tkhd_name = str(row.get("tkhd_name", "")).strip()

        bctt_language = row.get("bctt_language", "")
        kltn_language = row.get("kltn_language", "")

        if project_type in ["BCTT", "BC-KL"] and gvhd_name:
            bucket = get_workload_bucket(class_name, bctt_language)
            if bucket in bucket_display_map:
                result.loc[gvhd_name, ("Hướng dẫn BCTT", bucket_display_map[bucket])] += 1

        if project_type in ["KLTN", "BC-KL"] and gvhd_name:
            bucket = get_workload_bucket(class_name, kltn_language)
            if bucket in bucket_display_map:
                result.loc[gvhd_name, ("Hướng dẫn KLTN", bucket_display_map[bucket])] += 1

        if project_type in ["KLTN", "BC-KL"] and gvpb_name:
            bucket = get_workload_bucket(class_name, kltn_language)
            if bucket in bucket_display_map:
                result.loc[gvpb_name, ("Phản biện", bucket_display_map[bucket])] += 1

        if project_type in ["KLTN", "BC-KL"] and cthd_name:
            bucket = get_workload_bucket(class_name, kltn_language)
            if bucket in bucket_display_map:
                result.loc[cthd_name, ("Chủ tịch HĐ", bucket_display_map[bucket])] += 1

        if project_type in ["KLTN", "BC-KL"] and tvhd_name:
            bucket = get_workload_bucket(class_name, kltn_language)
            if bucket in bucket_display_map:
                result.loc[tvhd_name, ("Ủy viên HĐ", bucket_display_map[bucket])] += 1

        if project_type in ["KLTN", "BC-KL"] and tkhd_name:
            bucket = get_workload_bucket(class_name, kltn_language)
            if bucket in bucket_display_map:
                result.loc[tkhd_name, ("Thư ký HĐ", bucket_display_map[bucket])] += 1

    result = result.reset_index()
    result = result.rename(columns={"index": "Họ và tên GV"})

    new_columns = [("", "Họ và tên GV")]
    for col in result.columns[1:]:
        new_columns.append(col)

    result.columns = pd.MultiIndex.from_tuples(new_columns)

    return result


def get_admin_assignment_stats_debug_data():

    df = get_admin_workload_source_data()

    if df.empty:
        return pd.DataFrame()

    debug_rows = []

    for _, row in df.iterrows():
        project_type = normalize_text(row.get("project_type", ""))
        class_name = row.get("class_name", "")

        debug_rows.append({
            "MSSV": row.get("mssv", ""),
            "Họ tên SV": row.get("full_name", ""),
            "Lớp": class_name,
            "Loại đăng ký": project_type,
            "Ngôn ngữ BCTT": row.get("bctt_language", ""),
            "Bucket BCTT": get_workload_bucket(class_name, row.get("bctt_language", "")),
            "Ngôn ngữ KLTN": row.get("kltn_language", ""),
            "Bucket KLTN": get_workload_bucket(class_name, row.get("kltn_language", ""))
        })

    return pd.DataFrame(debug_rows)


def import_bctt_students(df):

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        mssv = str(row["MSSV"])
        full_name = row["Họ tên SV"]
        class_name = row["Lớp"]
        gvhd_name = row["GVHD"]

        cursor.execute(
            "SELECT id FROM lecturers WHERE full_name=?",
            (gvhd_name,)
        )

        lecturer = cursor.fetchone()

        if lecturer:

            gvhd_id = lecturer[0]

            cursor.execute(
                """
                INSERT INTO bctt_students (mssv, full_name, class_name, gvhd_id)
                VALUES (?, ?, ?, ?)
                """,
                (mssv, full_name, class_name, gvhd_id)
            )

    conn.commit()
    conn.close()


def import_kltn_students(df):

    conn = get_connection()
    cursor = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for _, row in df.iterrows():

        mssv = str(row["MSSV"]).strip()
        full_name = str(row["Họ tên SV"]).strip()
        class_name = str(row["Lớp"]).strip()

        gvhd_name = str(row["GVHD"]).strip()
        gvpb_name = str(row["GVPB"]).strip()
        cthd_name = str(row["CTHĐ"]).strip()
        tvhd_name = str(row["TVHĐ"]).strip()
        tkhd_name = str(row["TKHĐ"]).strip()

        defense_time = str(row["Thời gian"]).strip()
        room = str(row["Phòng"]).strip()
        council = str(row["Hội đồng"]).strip()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (gvhd_name,)
        )
        gvhd = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (gvpb_name,)
        )
        gvpb = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (cthd_name,)
        )
        cthd = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (tvhd_name,)
        )
        tvhd = cursor.fetchone()

        cursor.execute(
            "SELECT id FROM lecturers WHERE TRIM(full_name) = ?",
            (tkhd_name,)
        )
        tkhd = cursor.fetchone()

        if gvhd and gvpb and cthd and tvhd and tkhd:

            gvhd_id = gvhd[0]
            gvpb_id = gvpb[0]
            cthd_id = cthd[0]
            tvhd_id = tvhd[0]
            tkhd_id = tkhd[0]

            cursor.execute(
                """
                INSERT INTO kltn_students (
                    mssv,
                    full_name,
                    class_name,
                    gvhd_id,
                    gvpb_id,
                    cthd_id,
                    tvhd_id,
                    tkhd_id,
                    defense_time,
                    room,
                    council
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mssv,
                    full_name,
                    class_name,
                    gvhd_id,
                    gvpb_id,
                    cthd_id,
                    tvhd_id,
                    tkhd_id,
                    defense_time,
                    room,
                    council
                )
            )

            inserted_count = inserted_count + 1

        else:
            skipped_count = skipped_count + 1

    conn.commit()
    conn.close()

    return inserted_count, skipped_count


# ==============================================================================
# LECTURER_DATA_ACCESS
# ==============================================================================

def get_teacher_bctt_students_data(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv AS "MSSV",
            s.full_name AS "Họ tên SV",
            s.class_name AS "Lớp",
            s.nktt_1,
            s.nktt_2,
            s.nktt_3,
            s.nktt_4,
            s.nktt_5,
            s.bctt_1,
            s.bctt_2,
            s.bctt_3,
            s.bctt_4,
            s.bctt_5
        FROM students s
        WHERE s.gvhd_id = ?
          AND s.project_type IN ('BCTT', 'BC-KL')
        ORDER BY s.mssv
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))
    conn.close()

    if df.empty:
        return df

    rubric_cols = [
        "nktt_1", "nktt_2", "nktt_3", "nktt_4", "nktt_5",
        "bctt_1", "bctt_2", "bctt_3", "bctt_4", "bctt_5"
    ]

    for col in rubric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Điểm NKTT"] = df[["nktt_1", "nktt_2", "nktt_3", "nktt_4", "nktt_5"]].sum(axis=1, min_count=1)
    df["Điểm BCTT"] = df[["bctt_1", "bctt_2", "bctt_3", "bctt_4", "bctt_5"]].sum(axis=1, min_count=1)

    df["Điểm tổng BCTT"] = (
        df["Điểm NKTT"] / 3.0 + df["Điểm BCTT"] * 2.0 / 3.0
    ).round(2)

    return df


def get_teacher_kltn_students_data(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv AS "MSSV",
            s.full_name AS "Họ tên SV",
            s.class_name AS "Lớp",
            s.report_link AS "Link bài",
            s.turnitin_link AS "Link Turnitin",
            s.gvhd_tc1,
            s.gvhd_tc2,
            s.gvhd_tc3,
            s.gvhd_tc4
        FROM students s
        WHERE s.gvhd_id = ?
          AND s.project_type IN ('KLTN','BC-KL')
        ORDER BY s.mssv
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))
    conn.close()

    if df.empty:
        return df

    rubric_cols = ["gvhd_tc1","gvhd_tc2","gvhd_tc3","gvhd_tc4"]

    for col in rubric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    total_raw = df[rubric_cols].sum(axis=1, min_count=1)

    df["Điểm GVHD"] = total_raw.clip(upper=10)

    return df


def get_reviewer_students_by_council(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv,
            s.full_name,
            s.class_name,
            s.topic_title,
            s.report_link,
            s.turnitin_link,
            kd.council,
            kd.defense_time,
            kd.room,
            s.gvpb_tc1,
            s.gvpb_tc2,
            s.gvpb_tc3,
            s.gvpb_tc4,
            s.gvpb_tc5
        FROM kltn_details kd
        JOIN students s ON kd.student_id = s.id
        WHERE kd.gvpb_id = ?
        ORDER BY kd.council, s.mssv
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))
    conn.close()

    if df.empty:
        return df

    rubric_cols = ["gvpb_tc1","gvpb_tc2","gvpb_tc3","gvpb_tc4","gvpb_tc5"]

    for col in rubric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    total_raw = df[rubric_cols].sum(axis=1, min_count=1)

    df["Điểm tổng"] = total_raw.clip(upper=10)

    return df


def get_chair_students_by_council(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv,
            s.full_name,
            s.class_name,
            s.topic_title,
            s.report_link,
            s.turnitin_link,
            kd.council,
            kd.defense_time,
            kd.room,
            s.cthd_tc1,
            s.cthd_tc2,
            s.cthd_tc3,
            s.cthd_tc4,
            s.cthd_tc5,
            s.cthd_tc6,
            s.cthd_bonus
        FROM kltn_details kd
        JOIN students s ON kd.student_id = s.id
        WHERE kd.cthd_id = ?
        ORDER BY kd.council, s.mssv
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))
    conn.close()

    if df.empty:
        return df

    rubric_cols = [
        "cthd_tc1",
        "cthd_tc2",
        "cthd_tc3",
        "cthd_tc4",
        "cthd_tc5",
        "cthd_tc6",
        "cthd_bonus"
    ]

    for col in rubric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    main_total = df[
        ["cthd_tc1", "cthd_tc2", "cthd_tc3", "cthd_tc4", "cthd_tc5", "cthd_tc6"]
    ].sum(axis=1, min_count=1)

    bonus_total = df[["cthd_bonus"]].sum(axis=1, min_count=1)

    total_raw = main_total.fillna(0) + bonus_total.fillna(0)
    total_raw = total_raw.where(~(main_total.isna() & bonus_total.isna()), None)

    df["Điểm tổng"] = total_raw.clip(upper=10)

    return df


def get_member_students_by_council(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv,
            s.full_name,
            s.class_name,
            s.topic_title,
            s.report_link,
            s.turnitin_link,
            kd.council,
            kd.defense_time,
            kd.room,
            s.tvhd_tc1,
            s.tvhd_tc2,
            s.tvhd_tc3,
            s.tvhd_tc4,
            s.tvhd_tc5,
            s.tvhd_tc6,
            s.tvhd_bonus
        FROM kltn_details kd
        JOIN students s ON kd.student_id = s.id
        WHERE kd.tvhd_id = ?
        ORDER BY kd.council, s.mssv
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))
    conn.close()

    if df.empty:
        return df

    rubric_cols = [
        "tvhd_tc1",
        "tvhd_tc2",
        "tvhd_tc3",
        "tvhd_tc4",
        "tvhd_tc5",
        "tvhd_tc6",
        "tvhd_bonus"
    ]

    for col in rubric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    main_total = df[
        ["tvhd_tc1", "tvhd_tc2", "tvhd_tc3", "tvhd_tc4", "tvhd_tc5", "tvhd_tc6"]
    ].sum(axis=1, min_count=1)

    bonus_total = df[["tvhd_bonus"]].sum(axis=1, min_count=1)

    total_raw = main_total.fillna(0) + bonus_total.fillna(0)
    total_raw = total_raw.where(~(main_total.isna() & bonus_total.isna()), None)

    df["Điểm tổng"] = total_raw.clip(upper=10)

    return df


def get_secretary_students_by_council(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            s.id,
            s.mssv,
            s.full_name,
            s.class_name,
            s.topic_title,
            s.report_link,
            s.turnitin_link,
            kd.council,
            kd.defense_time,
            kd.room,
            s.tkhd_tc1,
            s.tkhd_tc2,
            s.tkhd_tc3,
            s.tkhd_tc4,
            s.tkhd_tc5,
            s.tkhd_tc6,
            s.tkhd_bonus,
            s.council_comment
        FROM kltn_details kd
        JOIN students s ON kd.student_id = s.id
        WHERE kd.tkhd_id = ?
        ORDER BY kd.council, s.mssv
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))
    conn.close()

    if df.empty:
        return df

    rubric_cols = [
        "tkhd_tc1",
        "tkhd_tc2",
        "tkhd_tc3",
        "tkhd_tc4",
        "tkhd_tc5",
        "tkhd_tc6",
        "tkhd_bonus"
    ]

    for col in rubric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    main_total = df[
        ["tkhd_tc1","tkhd_tc2","tkhd_tc3","tkhd_tc4","tkhd_tc5","tkhd_tc6"]
    ].sum(axis=1, min_count=1)

    bonus_total = df[["tkhd_bonus"]].sum(axis=1, min_count=1)

    total_raw = main_total.fillna(0) + bonus_total.fillna(0)
    total_raw = total_raw.where(~(main_total.isna() & bonus_total.isna()), None)

    df["Điểm tổng"] = total_raw.clip(upper=10)

    return df


def get_bctt_by_lecturer(lecturer_id):

    conn = get_connection()

    query = """
        SELECT
            mssv,
            full_name,
            class_name
        FROM bctt_students
        WHERE gvhd_id = ?
        ORDER BY class_name
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))

    conn.close()

    return df


def get_students_by_lecturer_and_types(lecturer_id, project_types):

    conn = get_connection()

    placeholders = ",".join(["?"] * len(project_types))

    query = f"""
        SELECT
            mssv,
            full_name,
            class_name,
            project_type
        FROM students
        WHERE gvhd_id = ? AND project_type IN ({placeholders})
        ORDER BY class_name, full_name
    """

    params = [lecturer_id] + project_types

    df = pd.read_sql_query(query, conn, params=params)

    conn.close()

    return df


def get_bctt_students_by_lecturer(lecturer_id):

    return get_students_by_lecturer_and_types(lecturer_id, ["BCTT", "BC-KL"])


def get_kltn_students_by_lecturer(lecturer_id):

    return get_students_by_lecturer_and_types(lecturer_id, ["KLTN", "BC-KL"])


def get_council_assignments_by_role(lecturer_id, role_type):

    conn = get_connection()

    if role_type == "Phản biện":
        role_column = "kd.gvpb_id"
    elif role_type == "Chủ tịch HĐ":
        role_column = "kd.cthd_id"
    elif role_type == "Ủy viên HĐ":
        role_column = "kd.tvhd_id"
    elif role_type == "Thư ký HĐ":
        role_column = "kd.tkhd_id"
    else:
        conn.close()
        return pd.DataFrame()

    query = f"""
        SELECT
            kd.council,
            kd.defense_time,
            kd.room,
            s.mssv,
            s.full_name,
            s.class_name
        FROM kltn_details kd
        INNER JOIN students s
            ON kd.student_id = s.id
        WHERE {role_column} = ?
        ORDER BY kd.council, s.full_name
    """

    df = pd.read_sql_query(query, conn, params=(lecturer_id,))

    conn.close()

    return df


def get_grouped_council_assignments(lecturer_id, role_type):

    df = get_council_assignments_by_role(lecturer_id, role_type)

    if df.empty:
        return {}

    grouped_data = {}

    for council_name, group_df in df.groupby("council"):

        defense_time = group_df["defense_time"].iloc[0]
        room = group_df["room"].iloc[0]

        display_df = group_df[["mssv", "full_name", "class_name"]].reset_index(drop=True)

        grouped_data[council_name] = {
            "defense_time": defense_time,
            "room": room,
            "data": display_df
        }

    return grouped_data


# ==============================================================================
# SCORE_PROCESSING_AND_DISPLAY_HELPERS
# ==============================================================================

def prepare_bctt_editor_df(df):

    if df.empty:
        return df

    editor_df = df.copy()

    rubric_cols = [
        "nktt_1", "nktt_2", "nktt_3", "nktt_4", "nktt_5",
        "bctt_1", "bctt_2", "bctt_3", "bctt_4", "bctt_5"
    ]

    for col in rubric_cols:
        editor_df[col] = pd.to_numeric(editor_df[col], errors="coerce")

    nktt_total = editor_df[["nktt_1","nktt_2","nktt_3","nktt_4","nktt_5"]].sum(axis=1, min_count=1)
    bctt_total = editor_df[["bctt_1","bctt_2","bctt_3","bctt_4","bctt_5"]].sum(axis=1, min_count=1)

    editor_df["Điểm NKTT"] = nktt_total.clip(upper=10)
    editor_df["Điểm BCTT"] = bctt_total.clip(upper=10)

    editor_df["Điểm tổng BCTT"] = (
        editor_df["Điểm NKTT"] / 3.0 + editor_df["Điểm BCTT"] * 2.0 / 3.0
    ).round(2)

    return editor_df


def save_teacher_bctt_scores(edited_df):

    if edited_df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0

    score_columns = [
        "nktt_1", "nktt_2", "nktt_3", "nktt_4", "nktt_5",
        "bctt_1", "bctt_2", "bctt_3", "bctt_4", "bctt_5"
    ]

    for _, row in edited_df.iterrows():
        student_id = row["id"]

        values = []
        rubric_values = {}

        for col in score_columns:
            value = row[col]

            if pd.isna(value) or value == "":
                rubric_values[col] = None
                values.append(None)
            else:
                rubric_values[col] = float(value)
                values.append(float(value))

        nktt_parts = [
            rubric_values["nktt_1"],
            rubric_values["nktt_2"],
            rubric_values["nktt_3"],
            rubric_values["nktt_4"],
            rubric_values["nktt_5"]
        ]

        bctt_parts = [
            rubric_values["bctt_1"],
            rubric_values["bctt_2"],
            rubric_values["bctt_3"],
            rubric_values["bctt_4"],
            rubric_values["bctt_5"]
        ]

        nktt_sum_raw = sum(v for v in nktt_parts if v is not None) if any(v is not None for v in nktt_parts) else None
        bctt_sum_raw = sum(v for v in bctt_parts if v is not None) if any(v is not None for v in bctt_parts) else None

        nktt_final = min(nktt_sum_raw, 10) if nktt_sum_raw is not None else None
        bctt_final = min(bctt_sum_raw, 10) if bctt_sum_raw is not None else None

        if nktt_final is not None and bctt_final is not None:
            final_bctt_score = round(nktt_final / 3.0 + bctt_final * 2.0 / 3.0, 2)
        else:
            final_bctt_score = None

        cursor.execute(
            """
            UPDATE students
            SET
                nktt_1 = ?,
                nktt_2 = ?,
                nktt_3 = ?,
                nktt_4 = ?,
                nktt_5 = ?,
                bctt_1 = ?,
                bctt_2 = ?,
                bctt_3 = ?,
                bctt_4 = ?,
                bctt_5 = ?,
                score_bctt = ?
            WHERE id = ?
            """,
            (*values, final_bctt_score, student_id)
        )

        updated_count += 1

    conn.commit()
    conn.close()

    return updated_count


def prepare_kltn_editor_df(df):

    if df.empty:
        return df

    editor_df = df.copy()

    rubric_cols = ["gvhd_tc1","gvhd_tc2","gvhd_tc3","gvhd_tc4"]

    for col in rubric_cols:
        editor_df[col] = pd.to_numeric(editor_df[col], errors="coerce")

    total_raw = editor_df[rubric_cols].sum(axis=1, min_count=1)

    editor_df["Điểm GVHD"] = total_raw.clip(upper=10)

    return editor_df


def save_teacher_kltn_gvhd_scores(edited_df):

    if edited_df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0

    for _, row in edited_df.iterrows():

        student_id = row["id"]

        tc1 = row["gvhd_tc1"]
        tc2 = row["gvhd_tc2"]
        tc3 = row["gvhd_tc3"]
        tc4 = row["gvhd_tc4"]

        values = []

        for v in [tc1, tc2, tc3, tc4]:
            if pd.isna(v) or v == "":
                values.append(None)
            else:
                values.append(float(v))

        tc_sum_raw = sum(v for v in values if v is not None) if any(v is not None for v in values) else None

        score_gvhd = min(tc_sum_raw, 10) if tc_sum_raw is not None else None

        cursor.execute(
            """
            UPDATE students
            SET
                gvhd_tc1 = ?,
                gvhd_tc2 = ?,
                gvhd_tc3 = ?,
                gvhd_tc4 = ?,
                score_gvhd = ?
            WHERE id = ?
            """,
            (*values, score_gvhd, student_id)
        )

        updated_count += 1

    conn.commit()
    conn.close()

    return updated_count


def prepare_reviewer_editor_df(df):

    if df.empty:
        return df

    editor_df = df.copy()

    rubric_cols = ["gvpb_tc1", "gvpb_tc2", "gvpb_tc3", "gvpb_tc4", "gvpb_tc5"]

    for col in rubric_cols:
        editor_df[col] = pd.to_numeric(editor_df[col], errors="coerce")

    total_raw = editor_df[rubric_cols].sum(axis=1, min_count=1)

    editor_df["Điểm tổng"] = total_raw.clip(upper=10)

    return editor_df


def save_reviewer_scores(edited_df):

    if edited_df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0

    for _, row in edited_df.iterrows():

        student_id = row["id"]

        tc1 = row["gvpb_tc1"]
        tc2 = row["gvpb_tc2"]
        tc3 = row["gvpb_tc3"]
        tc4 = row["gvpb_tc4"]
        tc5 = row["gvpb_tc5"]

        values = []

        for v in [tc1, tc2, tc3, tc4, tc5]:
            if pd.isna(v) or v == "":
                values.append(None)
            else:
                values.append(float(v))

        tc_sum_raw = sum(v for v in values if v is not None) if any(v is not None for v in values) else None

        score_gvpb = min(tc_sum_raw, 10) if tc_sum_raw is not None else None

        cursor.execute(
            """
            UPDATE students
            SET
                gvpb_tc1 = ?,
                gvpb_tc2 = ?,
                gvpb_tc3 = ?,
                gvpb_tc4 = ?,
                gvpb_tc5 = ?,
                score_gvpb = ?
            WHERE id = ?
            """,
            (*values, score_gvpb, student_id)
        )

        updated_count += 1

    conn.commit()
    conn.close()

    return updated_count


def prepare_chair_editor_df(df):

    if df.empty:
        return df

    editor_df = df.copy()

    rubric_cols = [
        "cthd_tc1",
        "cthd_tc2",
        "cthd_tc3",
        "cthd_tc4",
        "cthd_tc5",
        "cthd_tc6",
        "cthd_bonus"
    ]

    for col in rubric_cols:
        editor_df[col] = pd.to_numeric(editor_df[col], errors="coerce")

    main_total = editor_df[
        ["cthd_tc1", "cthd_tc2", "cthd_tc3", "cthd_tc4", "cthd_tc5", "cthd_tc6"]
    ].sum(axis=1, min_count=1)

    bonus_total = editor_df[["cthd_bonus"]].sum(axis=1, min_count=1)

    total_raw = main_total.fillna(0) + bonus_total.fillna(0)
    total_raw = total_raw.where(~(main_total.isna() & bonus_total.isna()), None)

    editor_df["Điểm tổng"] = total_raw.clip(upper=10)

    return editor_df


def save_chair_scores(edited_df):

    if edited_df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0

    for _, row in edited_df.iterrows():

        student_id = row["id"]

        tc1 = row["cthd_tc1"]
        tc2 = row["cthd_tc2"]
        tc3 = row["cthd_tc3"]
        tc4 = row["cthd_tc4"]
        tc5 = row["cthd_tc5"]
        tc6 = row["cthd_tc6"]
        bonus = row["cthd_bonus"]

        values = []

        for v in [tc1, tc2, tc3, tc4, tc5, tc6, bonus]:
            if pd.isna(v) or v == "":
                values.append(None)
            else:
                values.append(float(v))

        main_values = values[:6]
        bonus_value = values[6]

        main_sum_raw = sum(v for v in main_values if v is not None) if any(v is not None for v in main_values) else None

        if main_sum_raw is None and bonus_value is None:
            score_cthd = None
        else:
            total_raw = (main_sum_raw or 0) + (bonus_value or 0)
            score_cthd = min(total_raw, 10)

        cursor.execute(
            """
            UPDATE students
            SET
                cthd_tc1 = ?,
                cthd_tc2 = ?,
                cthd_tc3 = ?,
                cthd_tc4 = ?,
                cthd_tc5 = ?,
                cthd_tc6 = ?,
                cthd_bonus = ?,
                score_cthd = ?
            WHERE id = ?
            """,
            (*values, score_cthd, student_id)
        )

        updated_count += 1

    conn.commit()
    conn.close()

    return updated_count


def prepare_member_editor_df(df):

    if df.empty:
        return df

    editor_df = df.copy()

    rubric_cols = [
        "tvhd_tc1",
        "tvhd_tc2",
        "tvhd_tc3",
        "tvhd_tc4",
        "tvhd_tc5",
        "tvhd_tc6",
        "tvhd_bonus"
    ]

    for col in rubric_cols:
        editor_df[col] = pd.to_numeric(editor_df[col], errors="coerce")

    main_total = editor_df[
        ["tvhd_tc1", "tvhd_tc2", "tvhd_tc3", "tvhd_tc4", "tvhd_tc5", "tvhd_tc6"]
    ].sum(axis=1, min_count=1)

    bonus_total = editor_df[["tvhd_bonus"]].sum(axis=1, min_count=1)

    total_raw = main_total.fillna(0) + bonus_total.fillna(0)
    total_raw = total_raw.where(~(main_total.isna() & bonus_total.isna()), None)

    editor_df["Điểm tổng"] = total_raw.clip(upper=10)

    return editor_df


def save_member_scores(edited_df):

    if edited_df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0

    for _, row in edited_df.iterrows():

        student_id = row["id"]

        tc1 = row["tvhd_tc1"]
        tc2 = row["tvhd_tc2"]
        tc3 = row["tvhd_tc3"]
        tc4 = row["tvhd_tc4"]
        tc5 = row["tvhd_tc5"]
        tc6 = row["tvhd_tc6"]
        bonus = row["tvhd_bonus"]

        values = []

        for v in [tc1, tc2, tc3, tc4, tc5, tc6, bonus]:
            if pd.isna(v) or v == "":
                values.append(None)
            else:
                values.append(float(v))

        main_values = values[:6]
        bonus_value = values[6]

        main_sum_raw = sum(v for v in main_values if v is not None) if any(v is not None for v in main_values) else None

        if main_sum_raw is None and bonus_value is None:
            score_tvhd = None
        else:
            total_raw = (main_sum_raw or 0) + (bonus_value or 0)
            score_tvhd = min(total_raw, 10)

        cursor.execute(
            """
            UPDATE students
            SET
                tvhd_tc1 = ?,
                tvhd_tc2 = ?,
                tvhd_tc3 = ?,
                tvhd_tc4 = ?,
                tvhd_tc5 = ?,
                tvhd_tc6 = ?,
                tvhd_bonus = ?,
                score_tvhd = ?
            WHERE id = ?
            """,
            (*values, score_tvhd, student_id)
        )

        updated_count += 1

    conn.commit()
    conn.close()

    return updated_count


def prepare_secretary_editor_df(df):

    if df.empty:
        return df

    editor_df = df.copy()

    rubric_cols = [
        "tkhd_tc1","tkhd_tc2","tkhd_tc3",
        "tkhd_tc4","tkhd_tc5","tkhd_tc6",
        "tkhd_bonus"
    ]

    for col in rubric_cols:
        editor_df[col] = pd.to_numeric(editor_df[col], errors="coerce")

    main_total = editor_df[
        ["tkhd_tc1","tkhd_tc2","tkhd_tc3","tkhd_tc4","tkhd_tc5","tkhd_tc6"]
    ].sum(axis=1, min_count=1)

    bonus_total = editor_df[["tkhd_bonus"]].sum(axis=1, min_count=1)

    total_raw = main_total.fillna(0) + bonus_total.fillna(0)
    total_raw = total_raw.where(~(main_total.isna() & bonus_total.isna()), None)

    editor_df["Điểm tổng"] = total_raw.clip(upper=10)

    return editor_df


def save_secretary_scores(edited_df):

    if edited_df.empty:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0

    for _, row in edited_df.iterrows():

        student_id = row["id"]

        tc_values = [
            row["tkhd_tc1"],
            row["tkhd_tc2"],
            row["tkhd_tc3"],
            row["tkhd_tc4"],
            row["tkhd_tc5"],
            row["tkhd_tc6"],
            row["tkhd_bonus"]
        ]

        values = []

        for v in tc_values:
            if pd.isna(v) or v == "":
                values.append(None)
            else:
                values.append(float(v))

        comment = row["council_comment"]

        main_values = values[:6]
        bonus_value = values[6]

        main_sum_raw = sum(v for v in main_values if v is not None) if any(v is not None for v in main_values) else None

        if main_sum_raw is None and bonus_value is None:
            score_tkhd = None
        else:
            total_raw = (main_sum_raw or 0) + (bonus_value or 0)
            score_tkhd = min(total_raw, 10)

        cursor.execute(
            """
            UPDATE students
            SET
                tkhd_tc1 = ?,
                tkhd_tc2 = ?,
                tkhd_tc3 = ?,
                tkhd_tc4 = ?,
                tkhd_tc5 = ?,
                tkhd_tc6 = ?,
                tkhd_bonus = ?,
                council_comment = ?,
                score_tkhd = ?
            WHERE id = ?
            """,
            (*values, comment, score_tkhd, student_id)
        )

        updated_count += 1

    conn.commit()
    conn.close()

    return updated_count


def format_teacher_kltn_display_df(df):

    if df.empty:
        return df

    display_df = df.rename(columns={
        "gvhd_tc1":"Tiêu chí 1",
        "gvhd_tc2":"Tiêu chí 2",
        "gvhd_tc3":"Tiêu chí 3",
        "gvhd_tc4":"Tiêu chí 4"
    })

    columns = [
        "MSSV",
        "Họ tên SV",
        "Lớp",
        "Link bài",
        "Link Turnitin",
        "Tiêu chí 1",
        "Tiêu chí 2",
        "Tiêu chí 3",
        "Tiêu chí 4",
        "Điểm GVHD"
    ]

    return display_df[columns]


def format_teacher_bctt_display_df(df):

    if df.empty:
        return df

    display_df = df.copy()

    display_df = display_df.rename(columns={
        "nktt_1": "NKTT 1",
        "nktt_2": "NKTT 2",
        "nktt_3": "NKTT 3",
        "nktt_4": "NKTT 4",
        "nktt_5": "NKTT 5",
        "bctt_1": "BCTT 1",
        "bctt_2": "BCTT 2",
        "bctt_3": "BCTT 3",
        "bctt_4": "BCTT 4",
        "bctt_5": "BCTT 5"
    })

    display_columns = [
        "MSSV",
        "Họ tên SV",
        "Lớp",
        "NKTT 1",
        "NKTT 2",
        "NKTT 3",
        "NKTT 4",
        "NKTT 5",
        "Điểm NKTT",
        "BCTT 1",
        "BCTT 2",
        "BCTT 3",
        "BCTT 4",
        "BCTT 5",
        "Điểm BCTT",
        "Điểm tổng BCTT"
    ]

    return display_df[display_columns]


# ==============================================================================
# UI_PAGES
# ==============================================================================

def login_page():
    st.title("Hệ thống quản lý KLTN/BCTT")

    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập"):
        user = check_login(username, password)

        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user[1]
            st.session_state["role"] = user[2]
            st.session_state["lecturer_id"] = user[3]
            st.rerun()
        else:
            st.error("Sai tên đăng nhập hoặc mật khẩu")


def admin_dashboard():
    st.title("Admin Dashboard")
    st.write(f"Xin chào: {st.session_state['username']}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Quản lý giảng viên",
        "Tạo tài khoản",
        "Import Excel",
        "Tổng hợp phân công"
    ])

    with tab1:
        st.subheader("Thêm giảng viên")

        lecturer_code = st.text_input("Mã giảng viên")
        full_name = st.text_input("Họ tên giảng viên")
        email = st.text_input("Email")
        department = st.text_input("Bộ môn")

        if st.button("Lưu giảng viên"):
            if lecturer_code and full_name:
                add_lecturer(lecturer_code, full_name, email, department)
                st.success("Đã lưu giảng viên")
                st.rerun()
            else:
                st.error("Cần nhập ít nhất Mã giảng viên và Họ tên giảng viên")

        st.subheader("Danh sách giảng viên")
        df_lecturers = get_all_lecturers()
        st.dataframe(df_lecturers, use_container_width=True)
    with tab2:

        st.subheader("Tạo tài khoản đăng nhập cho giảng viên")

        df = get_all_lecturers()

        if not df.empty:

            lecturer_options = {
                f"{row['full_name']} ({row['lecturer_code']})": row["id"]
                for _, row in df.iterrows()
            }

            selected_lecturer = st.selectbox(
                "Chọn giảng viên",
                list(lecturer_options.keys())
            )
    
            username = st.text_input("Username")
            password = st.text_input("Password")

            if st.button("Tạo tài khoản"):

                lecturer_id = lecturer_options[selected_lecturer]

                create_lecturer_account(username, password, lecturer_id)

                st.success("Đã tạo tài khoản giảng viên")

        else:
            st.warning("Chưa có giảng viên trong hệ thống")
    with tab3:

        st.subheader("Import dữ liệu từ Excel")

        import_type = st.selectbox(
            "Chọn loại dữ liệu import",
            [
                "Phân công hướng dẫn",
                "Thông tin BCTT",
                "Thông tin KLTN",
                "Chi tiết hội đồng KLTN"
            ]
        )

        uploaded_file = st.file_uploader(
            "Chọn file Excel",
            type=["xlsx", "xls"]
        )

        if uploaded_file is not None:
            try:
                df_preview = pd.read_excel(uploaded_file)

                st.success("Đọc file Excel thành công")
                st.write("Xem trước dữ liệu:")
                st.dataframe(df_preview, use_container_width=True)

                st.info(f"Loại dữ liệu chuẩn bị import: {import_type}")

                if import_type == "Phân công hướng dẫn":

                    if st.button("Import phân công hướng dẫn"):

                        inserted_count, skipped_count = import_students(df_preview)

                        st.success(f"Đã import {inserted_count} dòng vào bảng students")
                        st.warning(f"Bỏ qua {skipped_count} dòng do sai loại hoặc không khớp GVHD")

                elif import_type == "Thông tin BCTT":

                    st.caption("File cần có các cột: MSSV, Ngôn ngữ BCTT")

                    if st.button("Import thông tin BCTT"):

                        success, message = import_bctt_submission_data(df_preview)

                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                elif import_type == "Thông tin KLTN":

                    st.caption("File cần có các cột: MSSV, Tên đề tài, Link bài, Link Turnitin, Ngôn ngữ KLTN")

                    if st.button("Import thông tin KLTN"):

                        success, message = import_kltn_submission_data(df_preview)

                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                elif import_type == "Chi tiết hội đồng KLTN":

                    if st.button("Import chi tiết hội đồng KLTN"):

                        inserted_count, skipped_count = import_kltn_details(df_preview)

                        st.success(f"Đã import {inserted_count} dòng hội đồng KLTN")
                        st.warning(f"Bỏ qua {skipped_count} dòng do MSSV hoặc giảng viên không khớp")

            except Exception as e:
                st.error(f"Lỗi khi đọc file Excel: {e}")                
    with tab4:

        st.subheader("Tổng hợp phân công")

        sub1, sub2, sub3, sub4, sub5 = st.tabs([
            "Thông tin tổng thể",
            "Học phần BCTT",
            "Học phần KLTN",
            "Thông tin phân công hội đồng",
            "Thống kê phân công chi tiết"
        ])

        with sub1:

            st.write("Danh sách tổng hợp toàn bộ thông tin theo MSSV")

            df_overview = get_admin_overview_data()

            if df_overview.empty:
                st.info("Chưa có dữ liệu")
            else:
                st.dataframe(df_overview, use_container_width=True)

        with sub2:

            st.write("Danh sách sinh viên học phần BCTT")

            df_bcct = get_admin_bcct_data()

            if df_bcct.empty:
                st.info("Chưa có dữ liệu BCTT")
            else:
                st.dataframe(df_bcct, use_container_width=True)

        with sub3:

            st.write("Danh sách sinh viên học phần KLTN")

            df_kltn = get_admin_kltn_data()

            if df_kltn.empty:
                st.info("Chưa có dữ liệu")
            else:
                st.dataframe(df_kltn, use_container_width=True)

        with sub4:

            st.write("Danh sách thông tin hội đồng")

            df_council = get_admin_council_data()

            if df_council.empty:
                st.info("Chưa có dữ liệu hội đồng")
            else:
                st.dataframe(df_council, use_container_width=True)

        with sub5:

            st.write("Thống kê phân công chi tiết theo giảng viên, nhiệm vụ và lớp")

            df_stats = get_admin_assignment_stats_data()

            if df_stats.empty:
                st.info("Chưa có dữ liệu thống kê")
            else:
                st.dataframe(df_stats, use_container_width=True)

            with st.expander("Xem bảng debug phân loại lớp/ngôn ngữ", expanded=False):
                df_debug = get_admin_assignment_stats_debug_data()

                if df_debug.empty:
                    st.info("Không có dữ liệu debug")
                else:
                    st.dataframe(df_debug, use_container_width=True)

    if st.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()


def lecturer_dashboard():

    #st.title("Lecturer Dashboard")
    #st.write(f"Xin chào: {st.session_state['username']}")

    lecturer_id = st.session_state.get("lecturer_id")

    if lecturer_id:

        lecturer = get_lecturer_by_id(lecturer_id)

        if lecturer:

            st.subheader("Thông tin giảng viên")
            #st.write(f"Mã giảng viên: {lecturer[1]}")
            st.write(f"Họ tên: {lecturer[2]}")
            #st.write(f"Email: {lecturer[3]}")
            #st.write(f"Bộ môn: {lecturer[4]}")

            tab1, tab2, tab3 = st.tabs(["Hướng dẫn BCTT", "Hướng dẫn KLTN", "Chi tiết phân công hội đồng"])

            with tab1:

                st.subheader("Hướng dẫn BCTT")

                df_bctt = get_teacher_bctt_students_data(lecturer_id)

                if df_bctt.empty:
                    st.info("Chưa có sinh viên được phân công")
                else:

                    editor_df = prepare_bctt_editor_df(df_bctt)

                    edited_df = st.data_editor(
                        editor_df,
                        use_container_width=True,
                        hide_index=True,
                        disabled=[
                            "id",
                            "MSSV",
                            "Họ tên SV",
                            "Lớp",
                            "Điểm NKTT",
                            "Điểm BCTT",
                            "Điểm tổng BCTT"
                        ],
                        column_config={
                            "id": None,
                            "nktt_1": st.column_config.NumberColumn("NKTT 1", min_value=0.0, max_value=2.0, step=0.1),
                            "nktt_2": st.column_config.NumberColumn("NKTT 2", min_value=0.0, max_value=5.0, step=0.1),
                            "nktt_3": st.column_config.NumberColumn("NKTT 3", min_value=0.0, max_value=1.5, step=0.1),
                            "nktt_4": st.column_config.NumberColumn("NKTT 4", min_value=0.0, max_value=1.5, step=0.1),
                            "nktt_5": st.column_config.NumberColumn("NKTT 5", min_value=0.0, max_value=1.0, step=0.1),
                            "bctt_1": st.column_config.NumberColumn("BCTT 1", min_value=0.0, max_value=2.0, step=0.1),
                            "bctt_2": st.column_config.NumberColumn("BCTT 2", min_value=0.0, max_value=5.0, step=0.1),
                            "bctt_3": st.column_config.NumberColumn("BCTT 3", min_value=0.0, max_value=1.5, step=0.1),
                            "bctt_4": st.column_config.NumberColumn("BCTT 4", min_value=0.0, max_value=1.5, step=0.1),
                            "bctt_5": st.column_config.NumberColumn("BCTT 5", min_value=0.0, max_value=1.0, step=0.1),
                            "Điểm NKTT": st.column_config.NumberColumn("Điểm NKTT", disabled=True),
                            "Điểm BCTT": st.column_config.NumberColumn("Điểm BCTT", disabled=True),
                            "Điểm tổng BCTT": st.column_config.NumberColumn("Điểm tổng BCTT", disabled=True)
                        },
                        key="teacher_bctt_editor"
                    )

                    edited_df = prepare_bctt_editor_df(edited_df)

                    st.dataframe(
                        edited_df[
                            [
                                "MSSV",
                                "Họ tên SV",
                                "Lớp",
                                "Điểm NKTT",
                                "Điểm BCTT",
                                "Điểm tổng BCTT"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    if st.button("Lưu điểm BCTT", key="save_bctt_scores"):
                        updated_count = save_teacher_bctt_scores(edited_df)
                        st.success(f"Đã lưu điểm cho {updated_count} sinh viên")
                        st.rerun()
            with tab2:

                st.subheader("Hướng dẫn KLTN")

                df_kltn = get_teacher_kltn_students_data(lecturer_id)

                if df_kltn.empty:
                    st.info("Chưa có sinh viên KLTN được phân công")
                else:

                    editor_df = prepare_kltn_editor_df(df_kltn)

                    edited_df = st.data_editor(
                        editor_df,
                        use_container_width=True,
                        hide_index=True,
                        disabled=[
                            "id",
                            "MSSV",
                            "Họ tên SV",
                            "Lớp",
                            "Link bài",
                            "Link Turnitin",
                            "Điểm GVHD"
                        ],
                        column_config={
                            "id": None,
                            "gvhd_tc1": st.column_config.NumberColumn("Tiêu chí 1", min_value=0.0, max_value=3.0, step=0.1),
                            "gvhd_tc2": st.column_config.NumberColumn("Tiêu chí 2", min_value=0.0, max_value=5.0, step=0.1),
                            "gvhd_tc3": st.column_config.NumberColumn("Tiêu chí 3", min_value=0.0, max_value=2.0, step=0.1),
                            "gvhd_tc4": st.column_config.NumberColumn("Tiêu chí 4", min_value=0.0, max_value=1.0, step=0.1),
                            "Điểm GVHD": st.column_config.NumberColumn("Điểm GVHD", disabled=True)
                        },
                        key="teacher_kltn_editor"
                    )

                    edited_df = prepare_kltn_editor_df(edited_df)

                    st.dataframe(
                        edited_df[
                            [
                                "MSSV",
                                "Họ tên SV",
                                "Lớp",
                                "Điểm GVHD"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    if st.button("Lưu điểm GVHD", key="save_kltn_scores"):
                        updated_count = save_teacher_kltn_gvhd_scores(edited_df)
                        st.success(f"Đã lưu điểm cho {updated_count} sinh viên")
                        st.rerun()

            with tab3:

                st.subheader("Chi tiết phân công hội đồng")

                sub1, sub2, sub3, sub4 = st.tabs(
                    ["Phản biện", "Chủ tịch HĐ", "Ủy viên HĐ", "Thư ký HĐ"]
                )

                with sub1:

                    st.subheader("Chấm điểm phản biện")

                    df_pb = get_reviewer_students_by_council(lecturer_id)

                    if df_pb.empty:
                        st.info("Không có nhiệm vụ được phân công")
                    else:
                        councils = df_pb["council"].dropna().unique()

                        for council_name in councils:
                            df_council = df_pb[df_pb["council"] == council_name].copy()

                            defense_time = df_council["defense_time"].iloc[0]
                            room = df_council["room"].iloc[0]

                            st.markdown(f"### {council_name}")
                            st.write(f"Thời gian tổ chức: {defense_time}")
                            st.write(f"Phòng: {room}")

                            editor_df = prepare_reviewer_editor_df(df_council)

                            editor_df = editor_df[
                                [
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "gvpb_tc1",
                                    "gvpb_tc2",
                                    "gvpb_tc3",
                                    "gvpb_tc4",
                                    "gvpb_tc5",
                                    "Điểm tổng"
                                ]
                            ]

                            edited_df = st.data_editor(
                                editor_df,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "Điểm tổng"
                                ],
                                column_config={
                                    "id": None,
                                    "mssv": "MSSV",
                                    "full_name": "Họ tên SV",
                                    "class_name": "Lớp",
                                    "topic_title": "Tên đề tài",
                                    "report_link": "Link bài",
                                    "turnitin_link": "Link Turnitin",
                                    "gvpb_tc1": st.column_config.NumberColumn("Tiêu chí 1", min_value=0.0, max_value=2.0, step=0.1),
                                    "gvpb_tc2": st.column_config.NumberColumn("Tiêu chí 2", min_value=0.0, max_value=1.0, step=0.1),
                                    "gvpb_tc3": st.column_config.NumberColumn("Tiêu chí 3", min_value=0.0, max_value=2.0, step=0.1),
                                    "gvpb_tc4": st.column_config.NumberColumn("Tiêu chí 4", min_value=0.0, max_value=5.0, step=0.1),
                                    "gvpb_tc5": st.column_config.NumberColumn("Tiêu chí 5", min_value=0.0, max_value=1.0, step=0.1),
                                    "Điểm tổng": st.column_config.NumberColumn("Điểm tổng", disabled=True)
                                },
                                key=f"review_editor_{council_name}"
                            )

                            edited_df = prepare_reviewer_editor_df(edited_df)

                            if st.button("Lưu điểm", key=f"save_review_scores_{council_name}"):
                                updated_count = save_reviewer_scores(edited_df)
                                st.success(f"Đã lưu điểm cho {updated_count} sinh viên của {council_name}")
                                st.rerun()

                with sub2:

                    st.subheader("Chấm điểm Chủ tịch HĐ")

                    df_ct = get_chair_students_by_council(lecturer_id)

                    if df_ct.empty:
                        st.info("Không có nhiệm vụ được phân công")
                    else:
                        councils = df_ct["council"].dropna().unique()

                        for council_name in councils:
                            df_council = df_ct[df_ct["council"] == council_name].copy()

                            defense_time = df_council["defense_time"].iloc[0]
                            room = df_council["room"].iloc[0]

                            st.markdown(f"### {council_name}")
                            st.write(f"Thời gian tổ chức: {defense_time}")
                            st.write(f"Phòng: {room}")

                            editor_df = prepare_chair_editor_df(df_council)

                            editor_df = editor_df[
                                [
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "cthd_tc1",
                                    "cthd_tc2",
                                    "cthd_tc3",
                                    "cthd_tc4",
                                    "cthd_tc5",
                                    "cthd_tc6",
                                    "cthd_bonus",
                                    "Điểm tổng"
                                ]
                            ]

                            edited_df = st.data_editor(
                                editor_df,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "Điểm tổng"
                                ],
                                column_config={
                                    "id": None,
                                    "mssv": "MSSV",
                                    "full_name": "Họ tên SV",
                                    "class_name": "Lớp",
                                    "topic_title": "Tên đề tài",
                                    "report_link": "Link bài",
                                    "turnitin_link": "Link Turnitin",
                                    "cthd_tc1": st.column_config.NumberColumn("Tiêu chí 1", min_value=0.0, max_value=1.0, step=0.1),
                                    "cthd_tc2": st.column_config.NumberColumn("Tiêu chí 2", min_value=0.0, max_value=2.0, step=0.1),
                                    "cthd_tc3": st.column_config.NumberColumn("Tiêu chí 3", min_value=0.0, max_value=3.0, step=0.1),
                                    "cthd_tc4": st.column_config.NumberColumn("Tiêu chí 4", min_value=0.0, max_value=1.0, step=0.1),
                                    "cthd_tc5": st.column_config.NumberColumn("Tiêu chí 5", min_value=0.0, max_value=1.0, step=0.1),
                                    "cthd_tc6": st.column_config.NumberColumn("Tiêu chí 6", min_value=0.0, max_value=2.0, step=0.1),
                                    "cthd_bonus": st.column_config.NumberColumn("Điểm thưởng", min_value=0.0, max_value=1.0, step=0.1),
                                    "Điểm tổng": st.column_config.NumberColumn("Điểm tổng", disabled=True)
                                },
                                key=f"chair_editor_{council_name}"
                            )

                            edited_df = prepare_chair_editor_df(edited_df)

                            if st.button("Lưu điểm", key=f"save_chair_scores_{council_name}"):
                                updated_count = save_chair_scores(edited_df)
                                st.success(f"Đã lưu điểm cho {updated_count} sinh viên của {council_name}")
                                st.rerun()
                                
                with sub3:

                    st.subheader("Chấm điểm Ủy viên HĐ")

                    df_tv = get_member_students_by_council(lecturer_id)

                    if df_tv.empty:
                        st.info("Không có nhiệm vụ được phân công")
                    else:
                        councils = df_tv["council"].dropna().unique()

                        for council_name in councils:
                            df_council = df_tv[df_tv["council"] == council_name].copy()

                            defense_time = df_council["defense_time"].iloc[0]
                            room = df_council["room"].iloc[0]

                            st.markdown(f"### {council_name}")
                            st.write(f"Thời gian tổ chức: {defense_time}")
                            st.write(f"Phòng: {room}")

                            editor_df = prepare_member_editor_df(df_council)

                            editor_df = editor_df[
                                [
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "tvhd_tc1",
                                    "tvhd_tc2",
                                    "tvhd_tc3",
                                    "tvhd_tc4",
                                    "tvhd_tc5",
                                    "tvhd_tc6",
                                    "tvhd_bonus",
                                    "Điểm tổng"
                                ]
                            ]

                            edited_df = st.data_editor(
                                editor_df,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "Điểm tổng"
                                ],
                                column_config={
                                    "id": None,
                                    "mssv": "MSSV",
                                    "full_name": "Họ tên SV",
                                    "class_name": "Lớp",
                                    "topic_title": "Tên đề tài",
                                    "report_link": "Link bài",
                                    "turnitin_link": "Link Turnitin",
                                    "tvhd_tc1": st.column_config.NumberColumn("Tiêu chí 1", min_value=0.0, max_value=1.0, step=0.1),
                                    "tvhd_tc2": st.column_config.NumberColumn("Tiêu chí 2", min_value=0.0, max_value=2.0, step=0.1),
                                    "tvhd_tc3": st.column_config.NumberColumn("Tiêu chí 3", min_value=0.0, max_value=3.0, step=0.1),
                                    "tvhd_tc4": st.column_config.NumberColumn("Tiêu chí 4", min_value=0.0, max_value=1.0, step=0.1),
                                    "tvhd_tc5": st.column_config.NumberColumn("Tiêu chí 5", min_value=0.0, max_value=1.0, step=0.1),
                                    "tvhd_tc6": st.column_config.NumberColumn("Tiêu chí 6", min_value=0.0, max_value=2.0, step=0.1),
                                    "tvhd_bonus": st.column_config.NumberColumn("Điểm thưởng", min_value=0.0, max_value=1.0, step=0.1),
                                    "Điểm tổng": st.column_config.NumberColumn("Điểm tổng", disabled=True)
                                },
                                key=f"member_editor_{council_name}"
                            )

                            edited_df = prepare_member_editor_df(edited_df)

                            if st.button("Lưu điểm", key=f"save_member_scores_{council_name}"):
                                updated_count = save_member_scores(edited_df)
                                st.success(f"Đã lưu điểm cho {updated_count} sinh viên của {council_name}")
                                st.rerun()

                with sub4:

                    st.subheader("Chấm điểm Thư ký HĐ")

                    df_tk = get_secretary_students_by_council(lecturer_id)

                    if df_tk.empty:
                        st.info("Không có nhiệm vụ được phân công")
                    else:
                        councils = df_tk["council"].dropna().unique()

                        for council_name in councils:

                            df_council = df_tk[df_tk["council"] == council_name].copy()

                            defense_time = df_council["defense_time"].iloc[0]
                            room = df_council["room"].iloc[0]

                            st.markdown(f"### {council_name}")
                            st.write(f"Thời gian tổ chức: {defense_time}")
                            st.write(f"Phòng: {room}")

                            editor_df = prepare_secretary_editor_df(df_council)

                            editor_df = editor_df[
                                [
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "tkhd_tc1",
                                    "tkhd_tc2",
                                    "tkhd_tc3",
                                    "tkhd_tc4",
                                    "tkhd_tc5",
                                    "tkhd_tc6",
                                    "tkhd_bonus",
                                    "council_comment",
                                    "Điểm tổng"
                                ]
                            ]

                            edited_df = st.data_editor(
                                editor_df,
                                use_container_width=True,
                                hide_index=True,
                                disabled=[
                                    "id",
                                    "mssv",
                                    "full_name",
                                    "class_name",
                                    "topic_title",
                                    "report_link",
                                    "turnitin_link",
                                    "Điểm tổng"
                                ],
                                column_config={
                                    "id": None,
                                    "mssv": "MSSV",
                                    "full_name": "Họ tên SV",
                                    "class_name": "Lớp",
                                    "topic_title": "Tên đề tài",
                                    "report_link": "Link bài",
                                    "turnitin_link": "Link Turnitin",
                                    "tkhd_tc1": st.column_config.NumberColumn("Tiêu chí 1", min_value=0.0, max_value=1.0, step=0.1),
                                    "tkhd_tc2": st.column_config.NumberColumn("Tiêu chí 2", min_value=0.0, max_value=2.0, step=0.1),
                                    "tkhd_tc3": st.column_config.NumberColumn("Tiêu chí 3", min_value=0.0, max_value=3.0, step=0.1),
                                    "tkhd_tc4": st.column_config.NumberColumn("Tiêu chí 4", min_value=0.0, max_value=1.0, step=0.1),
                                    "tkhd_tc5": st.column_config.NumberColumn("Tiêu chí 5", min_value=0.0, max_value=1.0, step=0.1),
                                    "tkhd_tc6": st.column_config.NumberColumn("Tiêu chí 6", min_value=0.0, max_value=2.0, step=0.1),
                                    "tkhd_bonus": st.column_config.NumberColumn("Điểm thưởng", min_value=0.0, max_value=1.0, step=0.1),
                                    "council_comment": st.column_config.TextColumn("Nhận xét hội đồng"),
                                    "Điểm tổng": st.column_config.NumberColumn("Điểm tổng", disabled=True)
                                },
                                key=f"secretary_editor_{council_name}"
                            )

                            edited_df = prepare_secretary_editor_df(edited_df)

                            if st.button("Lưu điểm", key=f"save_secretary_scores_{council_name}"):

                                updated_count = save_secretary_scores(edited_df)

                                st.success(f"Đã lưu điểm cho {updated_count} sinh viên của {council_name}")

                                st.rerun()

        else:
            st.warning("Không tìm thấy thông tin giảng viên")

    else:
        st.warning("Tài khoản này chưa được gắn với giảng viên")

    if st.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()


# ==============================================================================
# APP_ENTRYPOINT
# ==============================================================================

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"] is False:
        login_page()
    else:
        if st.session_state["role"] == "admin":
            admin_dashboard()
        elif st.session_state["role"] == "lecturer":
            lecturer_dashboard()


if __name__ == "__main__":
    ensure_bctt_rubric_columns()
    ensure_kltn_gvhd_rubric_columns()
    ensure_kltn_gvpb_rubric_columns()
    ensure_kltn_cthd_rubric_columns()
    ensure_kltn_tvhd_rubric_columns()
    ensure_kltn_tkhd_rubric_columns()
    main()
