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

def main():
    st.set_page_config(page_title="Wiki System", layout="wide")
    st.title("Wiki System")
    create_user_table()
    create_profile_table()
    
    page = st.sidebar.selectbox("Navigation", ["Login / Sign Up", "Skeleton Members"])
    
    if page == "Login / Sign Up":
        st.header("User Authentication")
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ""
        
        if not st.session_state.logged_in:
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
                        st.stop()
                    else:
                        st.error("Invalid Username or Password")
            elif menu == "Sign Up":
                new_user = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                if st.button("Sign Up"):
                    add_user(new_user, new_password)
                    st.success("Account created! Please login.")
                    st.stop()
        else:
            st.success(f"Logged in as {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.stop()
    
    elif page == "Skeleton Members":
        st.header("Skeleton Members")
        if st.session_state.get("logged_in", False):
            description = st.text_area("Describe Yourself")
            if st.button("Update Profile"):
                update_profile(st.session_state.username, description)
                st.success("Profile Updated")
                st.stop()
        
        st.header("Members' Profiles")
        profiles = get_profiles()
        for username, description in profiles:
            with st.expander(username):
                st.write(description)

if __name__ == "__main__":
    main()
