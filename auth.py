from database import supabase, get_user_role, get_user_name
import streamlit as st
import time



# ---------------- SIGN UP ----------------
def sign_up(email, password, full_name):
    try:
        # Sanitize data
        email = email.strip()
        password = password.strip()
        full_name = full_name.strip()

        if not all([email, password, full_name]):
            raise ValueError("Email, password, and full name cannot be blank or empty spaces.")

        # ------------------ CREATE AUTH USER ------------------
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        if response.user:

            # Save profile information
            supabase.table("profiles").insert({
                "id": response.user.id,
                "email": email,
                "full_name": full_name
            }).execute()

            # Save default role
            supabase.table("user_roles").insert({
                "id": response.user.id,
                "email": email,
                "role": "user"
            }).execute()

            st.session_state["user"] = response.user
            st.session_state["role"] = "user"
            st.session_state["full_name"] = full_name or ""

        return response

    except Exception as e:
        st.error(f"Signup Error: {e}")
        return None


# ---------------- LOGIN ----------------
def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })


        if response.user and response.session:


            st.session_state["user"] = None
            st.session_state["session"] = None
            st.session_state["role"] = "user"
            st.session_state["full_name"] = ""

            st.session_state["user"] = response.user
            st.session_state["session"] = response.session  

            # role logic - fetch role from database and store in session state
            role = get_user_role(response.user.id)
            st.session_state["role"] = role
            full_name = get_user_name(response.user.id)
            st.session_state["full_name"] = full_name or ""


            st.session_state["active_user_id"] = response.user.id
            return True
        

        return False

    except Exception as e:
        st.error(f"Login Error: {e}")
        return False


# ---------------- LOGOUT ----------------
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state["user"] = None
    st.session_state["session"] = None
    st.session_state["role"] = "user"
    st.session_state["full_name"] = ""
    st.session_state["active_user_id"] = None

    # Reset forgot-password flow
    st.session_state.auth_mode = "signin"
    st.session_state.reset_step = "request"
    st.session_state.reset_email_value = ""
    st.session_state.otp_timer_start = 0

    st.rerun()




# STEP 1: Send a true Password Reset OTP Code
def send_reset_otp(email):
    try:
        # This triggers the password reset track instead of the magic link track
        response = supabase.auth.reset_password_for_email(email)
        return True
    except Exception as e:
        print(f"Error sending password reset OTP: {e}")
        return False

def verify_otp_and_update_password(email, token, new_password):
    try:
        session = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "recovery"
        })

        if session:
            supabase.auth.update_user({
                "password": new_password
            })
            return True

        return False

    except Exception as e:
        print(f"Verification backend error: {e}")
        return False

def can_request_otp():
    return (time.time() - st.session_state.otp_timer_start) >= st.session_state.otp_cooldown


