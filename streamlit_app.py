import streamlit as st
import hashlib
import sqlite3


# ===== 사용자 관련 DB 함수 =====
def create_user_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user


# ===== 프로필 관련 DB 함수 =====
def create_profile_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def update_profile(username, description):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("REPLACE INTO profiles (username, description) VALUES (?, ?)", (username, description))
    conn.commit()
    conn.close()

def get_profiles():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM profiles")
    profiles = c.fetchall()
    conn.close()
    return profiles


# ===== 위키 페이지 관련 DB 함수 =====
def create_pages_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            content TEXT,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_page(title, content, author):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO pages (title, content, author) VALUES (?, ?, ?)", (title, content, author))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("해당 제목의 페이지가 이미 존재합니다. 다른 제목을 사용하거나 기존 페이지를 편집하세요.")
    conn.close()

def update_page(title, content, author):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE pages SET content = ?, updated_at = CURRENT_TIMESTAMP, author = ? WHERE title = ?",
              (content, author, title))
    conn.commit()
    conn.close()

def get_all_pages():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT title, author, updated_at FROM pages ORDER BY updated_at DESC")
    pages = c.fetchall()
    conn.close()
    return pages

def get_page_by_title(title):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT title, content, author, created_at, updated_at FROM pages WHERE title = ?", (title,))
    page = c.fetchone()
    conn.close()
    return page


# ===== 메인 함수 =====
def main():
    st.set_page_config(page_title="Wiki System", layout="wide")
    st.title("Wiki System")

    # DB 테이블 생성
    create_user_table()
    create_profile_table()
    create_pages_table()

    # 세션 상태 초기화
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    # ===== 사이드바 체크박스 =====
    page_selection = st.sidebar.checkbox("Home", value=True)
    skeleton_members = st.sidebar.checkbox("Skeleton Members")
    create_page = st.sidebar.checkbox("Create New Page")

    # ===== 로그인/로그아웃 처리 =====
    if st.session_state.logged_in:
        st.success(f"Logged in as {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.stop()
    else:
        if page_selection:
            st.subheader("Login or Sign Up")
            menu = st.radio("Select Option", ["Login", "Sign Up"])
            if menu == "Login":
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.button("Login"):
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Login Successful")
                    else:
                        st.error("Invalid Username or Password")
            elif menu == "Sign Up":
                new_user = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                if st.button("Sign Up"):
                    add_user(new_user, new_password)
                    st.success("Account created! Please login.")
    if skeleton_members:
        st.subheader("Skeleton Members Profiles")
        if st.session_state.get("logged_in", False):
            description = st.text_area("Describe Yourself")
            if st.button("Update Profile"):
                update_profile(st.session_state.username, description)
                st.success("Profile Updated")
        
        st.header("Members' Profiles")
        profiles = get_profiles()
        for username, description in profiles:
            with st.expander(username):
                st.write(description)

    if create_page:
        st.subheader("Create a New Wiki Page")
        if st.session_state.logged_in:
            new_title = st.text_input("Page Title")
            new_content = st.text_area("Page Content")
            if st.button("Create Page"):
                if new_title and new_content:
                    add_page(new_title, new_content, st.session_state.username)
                    st.success("Page created successfully!")
                else:
                    st.error("Please provide both title and content.")
        else:
            st.error("Please log in to create a new page.")

    # 홈 페이지: 최근 페이지 목록
    if page_selection:
        st.subheader("Wiki Home")
        st.write("Welcome to the Wiki System!")
        st.markdown("Recently updated pages:")
        pages = get_all_pages()
        if pages:
            for page in pages:
                title, author, updated_at = page
                st.markdown(f"**[{title}](?page={title})** - Last updated by {author} on {updated_at}")
        else:
            st.info("No pages available yet.")


if __name__ == "__main__":
    main()
