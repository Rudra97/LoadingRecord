import sqlite3
from datetime import datetime, timedelta, date
from io import BytesIO

import pandas as pd
import streamlit as st

DB_FILE = "records.db"

LOADING_POINTS = [
    "WCTL-1",
    "WCTL-2",
    "NCTL-1",
    "Phase-1 Middle",
    "Phase-1 RM",
    "Phase-2 RM",
    "Phase-2 Middle",
]

SHIFT_OPTIONS = ["A", "B", "C"]


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS loading_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_no TEXT NOT NULL,
            record_date TEXT NOT NULL,
            loading_point TEXT NOT NULL,
            shift TEXT NOT NULL,
            loading_start_time TEXT NOT NULL,
            loading_end_time TEXT NOT NULL,
            remarks TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def delete_old_records():
    cutoff = datetime.now() - timedelta(days=2)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM loading_records WHERE created_at < ?",
        (cutoff.isoformat(),)
    )
    conn.commit()
    conn.close()


def insert_record(
    vehicle_no,
    record_date,
    loading_point,
    shift,
    loading_start_time,
    loading_end_time,
    remarks,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO loading_records (
            vehicle_no, record_date, loading_point, shift,
            loading_start_time, loading_end_time, remarks, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            vehicle_no,
            str(record_date),
            loading_point,
            shift,
            loading_start_time,
            loading_end_time,
            remarks,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_all_records():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            id,
            vehicle_no AS "Vehicle No",
            record_date AS "Date",
            loading_point AS "Loading Point",
            shift AS "Shift",
            loading_start_time AS "Loading Start Time",
            loading_end_time AS "Loading End Time",
            remarks AS "Remarks",
            created_at AS "Created At"
        FROM loading_records
        ORDER BY created_at DESC
        """,
        conn,
    )
    conn.close()
    return df


def to_excel(df):
    output = BytesIO()
    export_df = df.copy()
    if "id" in export_df.columns:
        export_df = export_df.drop(columns=["id"])
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Records")
    output.seek(0)
    return output


def check_records_access():
    if "records_auth" not in st.session_state:
        st.session_state.records_auth = False

    if st.session_state.records_auth:
        return True

    st.markdown(
        """
        <div class="card">
            <div class="card-title">Protected Records</div>
            <div class="card-text">Enter password to view and download saved records.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    password = st.text_input("Password", type="password", key="records_password_input")
    if st.button("Login", use_container_width=True):
        app_password = st.secrets.get("records_password", "12345")
        if password == app_password:
            st.session_state.records_auth = True
            st.success("Access granted.")
            st.rerun()
        else:
            st.error("Wrong password.")
    return False


def add_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 50%, #f6f8fc 100%);
        }

        .block-container {
            max-width: 1100px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .hero {
            background: linear-gradient(135deg, #1d4ed8 0%, #0f766e 100%);
            padding: 24px;
            border-radius: 22px;
            color: white;
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
            margin-bottom: 18px;
        }

        .hero h1 {
            margin: 0;
            font-size: 2rem;
            color: white;
        }

        .card {
            background: white;
            border-radius: 18px;
            padding: 18px;
            border: 1px solid #dbe4f0;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
            margin-bottom: 14px;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
        }

        .card-text {
            color: #475569;
            font-size: 0.95rem;
        }

        .metric-box {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 18px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }

        .metric-label {
            color: #64748b;
            font-size: 0.9rem;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 4px;
        }

        div[data-testid="stForm"] {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 20px;
            padding: 18px 18px 8px 18px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }

        div[data-baseweb="select"] > div {
            background: white !important;
            color: #0f172a !important;
            border-radius: 12px !important;
            border: 1px solid #cbd5e1 !important;
        }

        div[data-baseweb="select"] * {
            color: #0f172a !important;
        }

        ul[role="listbox"] {
            background: white !important;
            color: #0f172a !important;
            border-radius: 12px !important;
            border: 1px solid #cbd5e1 !important;
        }

        ul[role="listbox"] li {
            color: #0f172a !important;
            background: white !important;
        }

        ul[role="listbox"] li:hover {
            background: #e0f2fe !important;
            color: #0f172a !important;
        }

        input, textarea {
            color: #0f172a !important;
        }

        div[data-baseweb="tab-list"] {
            gap: 8px;
        }

        button[data-baseweb="tab"] {
            background: white !important;
            border-radius: 12px !important;
            border: 1px solid #dbe4f0 !important;
            color: #0f172a !important;
            font-weight: 600 !important;
            padding: 10px 18px !important;
        }

        button[kind="primary"] {
            border-radius: 12px !important;
        }

        div[data-testid="stDataFrame"] {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #dbe4f0;
        }

        .download-wrap {
            background: linear-gradient(135deg, #eff6ff 0%, #ecfeff 100%);
            border: 1px solid #cfe3ff;
            border-radius: 18px;
            padding: 16px;
            margin-top: 12px;
            margin-bottom: 10px;
        }

        .download-title {
            color: #0f172a;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .download-text {
            color: #475569;
            font-size: 0.95rem;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Loading Records App",
    page_icon="🚚",
    layout="wide"
)

create_table()
delete_old_records()
add_custom_css()

all_df = get_all_records()
active_count = len(all_df)

st.markdown(
    """
    <div class="hero">
        <h1>🚚 Loading Records App</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Active Records</div>
            <div class="metric-value">{active_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-label">Auto Delete</div>
            <div class="metric-value">2 Days</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-label">Records Access</div>
            <div class="metric-value">Protected</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

tab1, tab2 = st.tabs(["📝 Entry", "📁 Records"])

with tab1:
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Add Loading Record</div>
            <div class="card-text">Fill the details below and save the record.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            vehicle_no = st.text_input("Vehicle No", placeholder="Enter vehicle number")
        with c2:
            record_date = st.date_input("Date", value=date.today())

        c3, c4 = st.columns(2)
        with c3:
            loading_point = st.selectbox("Loading Point", LOADING_POINTS)
        with c4:
            shift = st.selectbox("Shift", SHIFT_OPTIONS)

        c5, c6 = st.columns(2)
        with c5:
            loading_start_time = st.text_input(
                "Loading Start Time",
                placeholder="Enter time like 08:15"
            )
        with c6:
            loading_end_time = st.text_input(
                "Loading End Time",
                placeholder="Enter time like 10:45"
            )

        remarks = st.text_area(
            "Remarks / Other Data",
            placeholder="Enter notes or additional details"
        )

        save_clicked = st.form_submit_button("Save Record", use_container_width=True)

        if save_clicked:
            vehicle_no = vehicle_no.strip()
            remarks = remarks.strip()
            loading_start_time = loading_start_time.strip()
            loading_end_time = loading_end_time.strip()

            if not vehicle_no:
                st.error("Vehicle No is required.")
            elif not loading_start_time:
                st.error("Loading Start Time is required.")
            elif not loading_end_time:
                st.error("Loading End Time is required.")
            else:
                try:
                    start_obj = datetime.strptime(loading_start_time, "%H:%M")
                    end_obj = datetime.strptime(loading_end_time, "%H:%M")

                    if end_obj < start_obj:
                        st.error("Loading End Time cannot be earlier than Loading Start Time.")
                    else:
                        insert_record(
                            vehicle_no=vehicle_no,
                            record_date=record_date,
                            loading_point=loading_point,
                            shift=shift,
                            loading_start_time=loading_start_time,
                            loading_end_time=loading_end_time,
                            remarks=remarks,
                        )
                        st.success("Record saved successfully.")
                        st.rerun()

                except ValueError:
                    st.error("Please enter time in HH:MM format, for example 08:15 or 17:30.")

with tab2:
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Saved Records</div>
            <div class="card-text">View, filter, and download records as Excel.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if check_records_access():
        delete_old_records()
        df = get_all_records()

        if df.empty:
            st.info("No active records found.")
        else:
            f1, f2, f3 = st.columns(3)
            with f1:
                search_vehicle = st.text_input("Search Vehicle No")
            with f2:
                filter_point = st.selectbox("Filter Loading Point", ["All"] + LOADING_POINTS)
            with f3:
                filter_shift = st.selectbox("Filter Shift", ["All"] + SHIFT_OPTIONS)

            filtered_df = df.copy()

            if search_vehicle.strip():
                q = search_vehicle.strip().lower()
                filtered_df = filtered_df[
                    filtered_df["Vehicle No"].astype(str).str.lower().str.contains(q)
                ]

            if filter_point != "All":
                filtered_df = filtered_df[
                    filtered_df["Loading Point"] == filter_point
                ]

            if filter_shift != "All":
                filtered_df = filtered_df[
                    filtered_df["Shift"] == filter_shift
                ]

            st.dataframe(
                filtered_df.drop(columns=["id"]),
                use_container_width=True,
                hide_index=True
            )

            st.markdown(
                """
                <div class="download-wrap">
                    <div class="download-title">Download Records</div>
                    <div class="download-text">Export the currently visible records to Excel.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            excel_data = to_excel(filtered_df)

            d1, d2 = st.columns([3, 1])
            with d1:
                st.download_button(
                    label="⬇ Download Excel File",
                    data=excel_data,
                    file_name="loading_records.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with d2:
                if st.button("Logout", use_container_width=True):
                    st.session_state.records_auth = False
                    st.rerun()
