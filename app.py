import streamlit as st
from nav.tb_page import show_tb_page 
from nav.hiv_page import show_hiv_page
from auth import sign_up, login, logout, reset_password, update_password
from database import get_prediction_history, supabase, get_user_role, save_feedback, get_user_name
import pandas as pd

# Page config
st.set_page_config(page_title='Disease Prediction App' , layout='wide' , initial_sidebar_state='collapsed')

# #-----------------Hide Side bar---------------------------
# ---------------- SESSION STATE INIT ----------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = "user"

if "session" not in st.session_state:
    st.session_state["session"] = None


# ---------------- RESTORE SUPABASE SESSION ----------------
if st.session_state["session"] is None:
    try:
        session = supabase.auth.get_session()

        if session and session.user:
            st.session_state["session"] = session
            st.session_state["user"] = session.user

            # restore role from DB
            role = get_user_role(session.user.email)
            st.session_state["role"] = role
            full_name = get_user_name(session.user.email)
            st.session_state["full_name"] = full_name

    except Exception:
        pass


# ---------------- GET USER ----------------
user = st.session_state.get("user")




# ---------------- HIDE SIDEBAR (ONLY IF NOT LOGGED IN) ----------------
if not user:
    hide_sidebar_style = """
        <style>
            section[data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)


# ---------------- SIDEBAR CONTENT  ----------------
if user and hasattr(user, "email"):
    # st.sidebar.success(f"Welcome, {user.email}")
    st.sidebar.success(f"Welcome, {st.session_state['full_name']}")
    # st.sidebar.info(f"Role: {st.session_state.get('role', 'user')}")

else:
    st.sidebar.warning("Please log in")


st.markdown("""
<style> 
        .block-container{
            padding-top:1rem;
            padding-bottom: 0rem;
            margin-top: 1rem
            }
        
</style>
            """ , unsafe_allow_html=True)

##
if "user" not in st.session_state:
    st.session_state["user"] = None






# ================= AUTH PAGE =================
def auth_page():

    # ---------------- PAGE CONFIG ----------------
    st.set_page_config(
        page_title="Disease Prediction System",
        page_icon="🩺",
        layout="centered"
    )

    # ---------------- CSS ----------------
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
    background: linear-gradient(
        135deg,
        #0f172a,
        #1e1b4b,
        #312e81,
        #111827
    );

    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .auth-box {
        background: rgba(255,255,255,0.97);
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.2);
        margin-top: 50px;
    }

    .title {
        text-align: center;
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #5B4BDB;
    }

    .subtitle {
    text-align: center;
    color: #d1d5db;
    margin-bottom: 30px;
    font-size: 16px;
}
        /* INPUT LABELS */
    .stTextInput label {
        color: white !important;
        font-weight: 600 !important;
    }

    /* CHECKBOX LABEL */
    .stCheckbox label {
        color: white !important;
    }

    /* SMALL TEXT */
    .stMarkdown p {
        color: white !important;
    }
                
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] p,
    div[data-testid="stCheckbox"] span {
    color: white !important;
    opacity: 1 !important;
}

    </style>
    """, unsafe_allow_html=True)

    # ---------------- SESSION STATE ----------------
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signin"
    
    if "reset_mode" not in st.session_state:
        st.session_state.reset_mode = False

    # ---------------- MAIN CONTAINER ----------------
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)


    # =================================================
    #              RESET PASSWORD PAGE
    # =================================================

    if st.session_state.reset_mode:

        st.markdown(
            '<div class="title">Create New Password</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Enter your new password</div>',
            unsafe_allow_html=True
        )

        new_password = st.text_input(
            "🔒 New Password",
            type="password"
        )

        confirm_new_password = st.text_input(
            "🔒 Confirm New Password",
            type="password"
        )

        if st.button(
            "Update Password",
            use_container_width=True
        ):

            if new_password and confirm_new_password:

                if new_password == confirm_new_password:

                    response = update_password(new_password)

                    if response:

                        st.success(
                            "Password updated successfully"
                        )

                        st.balloons()

                        st.session_state.reset_mode = False
                        st.session_state.auth_mode = "signin"

                        st.rerun()

                else:
                    st.error("Passwords do not match")

            else:
                st.warning("Fill all fields")

    # =================================================
    #                  SIGN IN
    # =================================================
    if st.session_state.auth_mode == "signin":

        st.markdown(
            '<div class="title">Welcome Back</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Sign in to continue</div>',
            unsafe_allow_html=True
        )

        with st.form("signin_form"):

            email = st.text_input(
                "Email",
                placeholder="Enter your email"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            
            signin_btn = st.form_submit_button(
                "Sign In",
                use_container_width=True
            )
        

        #================================================
        #                   Reset Password
        #================================================
        st.markdown(
                "<p style='text-align:right; color:white;cursor:pointer;' > Forgot Password?</p>",
                unsafe_allow_html=True
            )
        forgot = st.button("Reset Password" ,use_container_width=False)

        if forgot:
            if email:
                reset_password(email)
                st.success("Password reset link sent to your email")
                st.info("Please check your inbox and follow the instructions to reset your password.")
                st.session_state.reset_mode = True
            else:
                st.warning("Please enter your email to reset password")

        # ---------------- LOGIN LOGIC ----------------
        if signin_btn:

            if email and password:

                success = login(email, password)

                if success:
                    st.success("Login successful")
                    st.balloons()
                    st.rerun()

                else:
                    st.error("Invalid email or password")

            else:
                st.warning("Please fill all fields")

        st.markdown("---")

        st.markdown(
    "<p style='color:white; text-align:center;'>Don't have an account?</p>",
    unsafe_allow_html=True
)

        if st.button(
            "Create New Account",
            use_container_width=True
        ):
            st.session_state.auth_mode = "signup"
            st.rerun()

    


    # =================================================
    #                  SIGN UP
    # =================================================
    else:

        st.markdown(
            '<div class="title">Create Account</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Join the Disease Prediction System</div>',
            unsafe_allow_html=True
        )

        with st.form("signup_form"):

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            email = st.text_input(
                "Email",
                placeholder="Enter your email"
            )

            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Create password"
            )

            confirm_password = st.text_input(
                "🔒 Confirm Password",
                type="password",
                placeholder="Confirm password"
            )

            terms = st.checkbox(
                "I agree to the Terms & Conditions"
            )

            signup_btn = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        # ---------------- SIGNUP LOGIC ----------------
        if signup_btn:

            if all([name, email, password, confirm_password, terms]):

                if password == confirm_password:

                    response = sign_up(email, password, name)

                    if response:
                        st.success("Account created successfully")
                        st.balloons()

                        st.session_state.auth_mode = "signin"
                        st.rerun()

                else:
                    st.error("Passwords do not match")

            else:
                st.warning("Fill all fields")

        st.markdown("---")

        st.markdown(
    "<p style='color:white; text-align:center;'>Already have an account?</p>",
    unsafe_allow_html=True
)

        if st.button(
            "Sign In Instead",
            use_container_width=True
        ):
            st.session_state.auth_mode = "signin"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

#-------------------Dashboard -----------------------
def dashboard():
    

    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-title"> Disease Prediction System</div>
        <div class="hero-subtitle">
            AI-powered Tuberculosis & HIV/AIDS Prediction Platform
        </div>
        <br>
        <div style="opacity:0.85;">
            Logged in as: <b>{st.session_state['user'].email}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    

    disease = st.sidebar.selectbox(
        'Select Disease',
        ['Tuberculosis' , 'HIV/AIDS']
    )

    # main screen 
    if disease == "Tuberculosis":
        show_tb_page()
    elif disease == 'HIV/AIDS':
        show_hiv_page()

    
    st.badge(
    "Feedback or Comment",
    color="primary",
    icon="💬"
    )

    feedback = st.text_area(
    label="feedback",
    label_visibility="collapsed",
    placeholder="Your feedback helps us improve!",
    height=100
    )

    submit_feedback = st.button(
    "Submit Feedback",
    use_container_width=True
    )
    
    if submit_feedback:

        if feedback:

            user_email = st.session_state["user"].email

            response = save_feedback(
                user_email,
                feedback
            )

            if response:

                st.success(
                    "Feedback submitted successfully "
                )

        else:
            st.warning(
                "Please enter your feedback first"
            )
        
    
    st.markdown("""
    <br><br>
    <div style='text-align:center; color:white; opacity:0.7;'>
         AI Disease Prediction Platform <br>
        Built with Streamlit + Supabase + Machine Learning
    </div>
    """, unsafe_allow_html=True)
            
            
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()






# ================= LOAD CSS =================
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )



# ================= APPLY CSS =================
local_css("styles.css")

  

   


## ----------Router -------
if st.session_state["user"] is None:
    auth_page()
else:
    dashboard()