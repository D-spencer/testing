# from database import supabase
# import streamlit as st


# #-------------SIGN UP -----------------
# def sign_up(email, password):
#     try:
#         response = supabase.auth.sign_up({
#             "email": email,
#             "password": password
#         })
#         return response
#     except Exception as e:
#         st.error(f'Signup Error:{e}')

# #------------Login------------------
# def login(email, password):
#     try:
#         response = supabase.auth.sign_in_with_password({
#         "email": email,
#         "password": password
#         })
        
#         if response.user:
#             st.session_state["user"] = response.user
#             return True
#     except Exception as e:
#         st.error(f'Login Error: {e}')
#     return False

# #---------------LOGOUT----------------
# def logout():
#     st.session_state['user'] = None







from database import supabase, get_user_role, get_user_name
import streamlit as st


# ---------------- SIGN UP ----------------
def sign_up(email, password, full_name):
    try:

        # ---------------- CREATE AUTH USER ----------------
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # ---------------- SAVE PROFILE ----------------
        if response.user:

            supabase.table("profiles").insert({
                "id": response.user.id,
                "email": email,
                "full_name": full_name
            }).execute()

        return response

    except Exception as e:
        st.error(f"Signup Error: {e}")


# ---------------- LOGIN ----------------
def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user and response.session:
            st.session_state["user"] = response.user
            st.session_state["session"] = response.session  

            # role logic - fetch role from database and store in session state
            role = get_user_role(response.user.email)
            st.session_state["role"] = role
            full_name = get_user_name(response.user.email)
            st.session_state["full_name"] = full_name

            return True

        return False

    except Exception as e:
        st.error(f"Login Error: {e}")
        return False


# ---------------- LOGOUT ----------------
def logout():
    supabase.auth.sign_out()
    st.session_state["user"] = None
    st.session_state["session"] = None
    st.session_state["role"] = "user"
    st.rerun()



#-----------------Reset Password-----------------
def reset_password(email):
    try:
        response = supabase.auth.reset_password_for_email(
            email, 
            {
                "redirect_to": "https://your-app-url.com/reset-password"
                # "redirect_to": "http://localhost:8501"
            }
        )
        return response
    
    except Exception as e:
        st.error(f"Password Reset Error: {e}")

# ------------------Update Password-----------------
def update_password(new_password):
    try:
        response = supabase.auth.update_user({
            "password": new_password
        })
        return response
    except Exception as e:
        st.error(f"Password Update Error: {e}")

