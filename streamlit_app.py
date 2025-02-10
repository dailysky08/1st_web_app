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
    st.set_page_config(page_title="Wiki 시스템", layout="wide")
    st.title("Wiki 시스템")

    # DB 테이블 생성
    create_user_table()
    create_profile_table()
    create_pages_table()

    # 세션 상태 초기화
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    # ===== 사이드바 라디오 버튼 =====
    page_selection = st.sidebar.radio("페이지 선택", ["홈", "자유문서 아카이브", "Skeleton 회원"], index=0)

    # ===== 로그인/로그아웃 처리 =====
    if st.session_state.logged_in:
        st.success(f"{st.session_state.username}로 로그인되었습니다.")
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.stop()
    else:
        if page_selection == "홈":
            st.subheader("로그인 또는 회원가입")
            menu = st.radio("옵션 선택", ["로그인", "회원가입"])
            if menu == "로그인":
                username = st.text_input("사용자 이름")
                password = st.text_input("비밀번호", type="password")
                if st.button("로그인"):
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("로그인 성공")
                    else:
                        st.error("잘못된 사용자 이름 또는 비밀번호")
            elif menu == "회원가입":
                new_user = st.text_input("사용자 이름")
                new_password = st.text_input("비밀번호", type="password")
                if st.button("회원가입"):
                    add_user(new_user, new_password)
                    st.success("계정이 생성되었습니다! 로그인해주세요.")
        elif page_selection == "Skeleton 회원":
            st.subheader("Skeleton 회원 프로필")
            if st.session_state.get("logged_in", False):
                description = st.text_area("자기소개")
                if st.button("프로필 업데이트"):
                    update_profile(st.session_state.username, description)
                    st.success("프로필이 업데이트되었습니다.")
            
            st.header("회원 프로필")
            profiles = get_profiles()
            for username, description in profiles:
                with st.expander(username):
                    st.write(description)

    # ===== 자유문서 아카이브 =====
    if page_selection == "자유문서 아카이브":
        st.subheader("자유문서 아카이브")
        if st.session_state.logged_in:
            action = st.radio("문서 관리", ["문서 읽기", "문서 수정", "문서 삭제", "문서 생성"])
            
            if action == "문서 생성":
                st.subheader("새로운 문서 생성")
                new_title = st.text_input("페이지 제목")
                new_content = st.text_area("페이지 내용")
                if st.button("문서 생성"):
                    if new_title and new_content:
                        add_page(new_title, new_content, st.session_state.username)
                        st.success("문서가 생성되었습니다!")
                    else:
                        st.error("제목과 내용을 모두 입력하세요.")
            elif action == "문서 수정":
                st.subheader("문서 수정")
                pages = get_all_pages()
                if pages:
                    page_titles = [page[0] for page in pages]
                    selected_title = st.selectbox("문서 제목 선택", page_titles)
                    if selected_title:
                        page = get_page_by_title(selected_title)
                        if page:
                            title, content, author, created_at, updated_at = page
                            st.markdown(f"# {title}")
                            updated_content = st.text_area("수정할 내용", value=content)
                            if st.button("수정 저장"):
                                if updated_content:
                                    update_page(title, updated_content, st.session_state.username)
                                    st.success("문서가 수정되었습니다!")
                                else:
                                    st.error("내용을 입력해주세요.")
                else:
                    st.info("등록된 문서가 없습니다.")
            elif action == "문서 삭제":
                st.subheader("문서 삭제")
                pages = get_all_pages()
                if pages:
                    page_titles = [page[0] for page in pages]
                    selected_title = st.selectbox("문서 제목 선택", page_titles)
                    if selected_title:
                        if st.button("문서 삭제"):
                            conn = sqlite3.connect("users.db")
                            c = conn.cursor()
                            c.execute("DELETE FROM pages WHERE title = ?", (selected_title,))
                            conn.commit()
                            conn.close()
                            st.success("문서가 삭제되었습니다.")
                else:
                    st.info("삭제할 문서가 없습니다.")
            elif action == "문서 읽기":
                st.subheader("문서 읽기")
                pages = get_all_pages()
                if pages:
                    page_titles = [page[0] for page in pages]
                    selected_title = st.selectbox("문서 제목 선택", page_titles)
                    if selected_title:
                        page = get_page_by_title(selected_title)
                        if page:
                            title, content, author, created_at, updated_at = page
                            st.markdown(f"# {title}")
                            st.markdown(f"**작성자:** {author} | **생성일:** {created_at} | **마지막 수정:** {updated_at}")
                            st.write(content)
                else:
                    st.info("등록된 문서가 없습니다.")
        else:
            st.error("로그인 후 자유문서 아카이브를 사용할 수 있습니다.")


if __name__ == "__main__":
    main()
