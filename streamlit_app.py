import streamlit as st
import hashlib
import sqlite3

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

def main():
    st.set_page_config(page_title="Wiki System", layout="wide")
    st.title("Wiki Login System")
    create_user_table()
    
    menu = ["Login", "Sign Up"]
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
    
    col1, col2 = st.columns([8, 1])
    with col2:
        if not st.session_state.logged_in:
            if st.button("Login", key="login_btn_header"):
                st.session_state.menu_choice = "Login"
            if st.button("Sign Up", key="signup_btn_header"):
                st.session_state.menu_choice = "Sign Up"
    
    if st.session_state.logged_in:
        st.success(f"Logged in as {st.session_state.username}")
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    else:
        if "menu_choice" in st.session_state:
            choice = st.session_state.menu_choice
        else:
            choice = "Login"
        
        if choice == "Login":
            st.subheader("Login Section")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", key="login_btn"):
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login Successful")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
        elif choice == "Sign Up":
            st.subheader("Create New Account")
            new_user = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            if st.button("Sign Up", key="signup_btn"):
                add_user(new_user, new_password)
                st.success("Account created! Go to Login.")
                st.rerun()

if __name__ == "__main__":
    main()
