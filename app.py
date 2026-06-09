import streamlit as st
import time
from nav.tb_page import show_tb_page 
from nav.hiv_page import show_hiv_page
from auth import sign_up, login, logout, send_reset_otp, verify_otp_and_update_password,can_resend_otp
from database import supabase, get_user_role, save_feedback, get_user_name
from streamlit_autorefresh import st_autorefresh
from streamlit_extras.stylable_container import stylable_container






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

        if session and getattr(session, "user", None) is not None:
            st.session_state["session"] = session
            st.session_state["user"] = session.user
            
            # Safe check: Only query the database if the email actually exists
            if session.user.email:
                role = get_user_role(session.user.email)
                st.session_state["role"] = role
                
                full_name = get_user_name(session.user.email)
                st.session_state["full_name"] = full_name
            else:
                st.session_state["role"] = "user"
        else:
            # Cleanly ensure states are cleared if there's no session
            st.session_state["session"] = None
            st.session_state["user"] = None
            st.session_state["role"] = "user"

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
        background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81, #111827);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Titles and Subtitles inside the white box */
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #5B4BDB;
    }

    .subtitle {
        text-align: center;
        color: #666; /* Darker gray for readability on white */
        margin-bottom: 30px;
        font-size: 16px;
    }

    /* Small text outside the box stays white */
    .stMarkdown p {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- SESSION STATE ----------------
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signin"

  
    if "reset_email_value" not in st.session_state:
        st.session_state.reset_email_value = ""

    if "reset_step" not in st.session_state:
        st.session_state.reset_step = "request"
    if "otp_timer_start" not in st.session_state:
        st.session_state.otp_timer_start = 0

    if "otp_cooldown" not in st.session_state:
        st.session_state.otp_cooldown = 60  # seconds

    
        
    # ---------------- MAIN CONTAINER (CENTERED) ----------------
    # Use columns to NARROW the container on the screen
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1]) 

    with col2:
        with stylable_container(
            key="auth_box",
            css_styles="""
                {
            
          background-color: var(--secondary-background-color); 
            padding: 40px;
            border-radius: 25px;
            box-shadow: 0px 10px 40px rgba(0,0,0,0.2);
            border: 1px solid rgba(128, 128, 128, 0.2);
        }

        /* Target ONLY the email input using its unique key */
        div[data-testid="stVerticalBlock"] > div:has(input[key="auth_email"]) {
            width: calc(100% - 2px) !important; /* Adjust this slightly if needed */
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: -32px !important; /* Keeps the 'joined' look */
        }

        input[key="auth_email"] {
            border-bottom-left-radius: 0px !important;
            border-bottom-right-radius: 0px !important;
            border-bottom: none !important;
        }

        /* Ensure the form below is also centered and matching */
        [data-testid="stForm"] {
            border-top: none !important;
            border-top-left-radius: 0px !important;
            border-top-right-radius: 0px !important;
            }
            """,
        ):
                if st.session_state.auth_mode == "otp_reset":
                    st.markdown('<div class="title">Reset Password via OTP</div>', unsafe_allow_html=True)

                    # =================================================
                    # STEP 1: REQUEST OTP
                    # =================================================
                    if st.session_state.reset_step == "request":

                        email = st.text_input("Email", placeholder="Enter your email", key="auth_reset_email_input")

                        st.markdown('<div class="subtitle">A 6-digit code will be sent to your inbox</div>', unsafe_allow_html=True)

                        if st.button("Send Reset Code", use_container_width=True):

                            if email:
                                if st.session_state.otp_timer_start == 0 or can_resend_otp():

                                    with st.spinner("Sending code..."):
                                        if send_reset_otp(email.strip()):
                                            st.success("A 6-digit code has been sent to your email.")

                                            st.session_state.reset_email_value = email.strip()
                                            st.session_state.reset_step = "verify"

                                            # START TIMER
                                            st.session_state.otp_timer_start = time.time()

                                            st.rerun()
                                        else:
                                            st.error("Failed to send code. Are you sure this email is correct, Try again.")

                                else:
                                    remaining = int(st.session_state.otp_cooldown - (time.time() - st.session_state.otp_timer_start))
                                    st.warning(f"Please wait {remaining}s before requesting another code.")
                            else:
                                st.warning("Please enter your email address.")

                        if st.button("← Back to Sign In", use_container_width=True):
                            st.session_state.auth_mode = "signin"
                            st.rerun()

                    # =================================================
                    # STEP 2: VERIFY OTP + RESET PASSWORD
                    # =================================================
                    elif st.session_state.reset_step == "verify":

                        st.markdown('<div class="subtitle">Enter OTP and new password</div>', unsafe_allow_html=True)

                        st_autorefresh(interval=1000, key="otp_timer")

                        # ---------------- COOLDOWN DISPLAY ----------------
                        remaining = int(
                            st.session_state.otp_cooldown -
                            (time.time() - st.session_state.otp_timer_start)
                        )

                        if remaining > 0:
                            st.info(f"⏳ Resend OTP in {remaining}s")
                        else:
                            st.success("✅ You can resend OTP now")

                        # ---------------- RESEND OTP BUTTON ----------------
                        if can_resend_otp(
                            st.session_state.otp_timer_start,
                            st.session_state.otp_cooldown
                        ):

                            if st.button("Resend OTP", use_container_width=True):

                                with st.spinner("Resending code..."):
                                    if send_reset_otp(st.session_state.reset_email_value):
                                        st.success("New OTP sent!")

                                        st.session_state.otp_timer_start = time.time()
                                        st.rerun()
                                    else:
                                        st.error("Failed to resend OTP")

                        else:
                            remaining = int(
                                st.session_state.otp_cooldown -
                                (time.time() - st.session_state.otp_timer_start)
                            )

                            st.button(f"Resend OTP ({remaining}s)", disabled=True, use_container_width=True)
                        # ---------------- OTP + PASSWORD FIELDS ----------------
                        otp_code = st.text_input("Enter 6-digit OTP Code", max_chars=6, placeholder="000000")
                        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
                        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")

                        # ---------------- VERIFY BUTTON ----------------
                        
                        if st.button("Verify & Update Password", use_container_width=True):
                            

                            if otp_code and new_password and confirm_password:

                                if new_password == confirm_password:

                                    with st.spinner("Verifying code and updating password..."):

                                        success = verify_otp_and_update_password(
                                            st.session_state.reset_email_value,
                                            otp_code.strip(),
                                            new_password.strip()
                                        )

                                        if success:
                                            st.success("Password updated successfully!")
                                            st.balloons()

                                            # RESET EVERYTHING CLEANLY
                                            st.session_state.auth_mode = "signin"
                                            st.session_state.reset_step = "request"
                                            st.session_state.reset_email_value = ""

                                            # reset timer
                                            st.session_state.otp_timer_start = 0

                                            st.rerun()

                                        else:
                                            st.error("Invalid or expired OTP code. Please try again.")

                                else:
                                    st.error("Passwords do not match.")

                            else:
                                st.warning("Please fill out all fields.")

                        # ---------------- BACK BUTTON ----------------
                        if st.button("← Request New Code", use_container_width=True):
                            st.session_state.reset_step = "request"
                            st.session_state.reset_email_value = ""
                            st.rerun()


                # =================================================
                #                   SIGN IN
                # =================================================
                elif st.session_state.auth_mode == "signin":
                    st.markdown('<div class="title">Welcome Back</div>', unsafe_allow_html=True)
                    st.markdown('<div class="subtitle">Sign in to continue</div>', unsafe_allow_html=True)

                    email = st.text_input("Email", placeholder="Enter your email", key="auth_email")

                    with st.form("signin_form"):
                    
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        signin_btn = st.form_submit_button("Sign In", use_container_width=True)

                    # Locate your old button section inside the signin block and swap it to this:
                    if st.button("Forgot Password?"):
                        st.session_state.auth_mode = "otp_reset"
                        st.rerun()

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
                    st.markdown("<p style='color:#31333F; text-align:center;'>Don't have an account?</p>", unsafe_allow_html=True)
                    if st.button("Create New Account", use_container_width=True):
                        st.session_state.auth_mode = "signup"
                        st.rerun()

                # =================================================
                #                   SIGN UP
                # =================================================
                else:
                    st.markdown('<div class="title">Create Account</div>', unsafe_allow_html=True)
                    st.markdown('<div class="subtitle">Join the system</div>', unsafe_allow_html=True)

                    with st.form("signup_form"):
                        name = st.text_input("Full Name", placeholder="Enter your full name")
                        email = st.text_input("Email", placeholder="Enter your email")
                        password = st.text_input("Password", type="password")
                        confirm_password = st.text_input("Confirm Password", type="password")
                        terms = st.checkbox("I agree to the Terms & Conditions")
                        signup_btn = st.form_submit_button("Create Account", use_container_width=True)

                    # 1. Create an empty container right above your button
                    # This dictates exactly where the error message will appear on the screen
                    error_container = st.empty()

                    if signup_btn:
                        clean_name = name.strip()
                        clean_email = email.strip()
                        clean_password = password.strip()
                        clean_confirm = confirm_password.strip()

                        # 2. Use error_container.warning() or .error() instead of st.warning() or st.error()
                        if not all([clean_name, clean_email, clean_password, clean_confirm]):
                            error_container.warning("All fields are required. Please fill them out completely.")
                        
                        elif clean_password != clean_confirm:
                            error_container.error("Passwords do not match.")
                            
                        elif not terms:
                            error_container.error("You must agree to the Terms & Conditions.")
                            
                        else:
                            with st.spinner("Creating your account..."):
                                response = sign_up(clean_email, clean_password, clean_name)
                                
                                if response:
                                    st.success("Account created successfully!")
                                    st.balloons()
                                    
                                    st.session_state.auth_mode = "signin"
                                    st.rerun()

                    st.markdown("---")

                    if st.button("Sign In Instead", use_container_width=True):
                        st.session_state.auth_mode = "signin"
                        st.rerun()


#-------------------Dashboard -----------------------
def dashboard():
    

    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-title"> Disease Prediction System</div>
        <div class="hero-subtitle">
            ML-powered Tuberculosis & HIV/AIDS Prediction Platform
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
         PREEMPTIVE DIAGNOSIS OF CHRONIC DISEASE:
TUBERCULOSIS And HIV/AIDS USING A QUESTIONNAIRE BASED MACHINE
LEARNING APPROACE <br>
        Built with Streamlit + Supabase + Machine Learning(Group 2)
    </div>
    """, unsafe_allow_html=True)
            
            
    st.sidebar.divider()
    if st.sidebar.button("Logout", icon=":material/logout:"):
        logout()
        st.rerun()

    # st.sidebar.button("Logout", icon=":material/exit_to_app:")
    
   







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