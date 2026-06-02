import streamlit as st
import pandas as pd
import joblib
import time
from database import save_prediction
from streamlit_extras.stylable_container import stylable_container


# LOAD MODEL
model = joblib.load('model/Hiv_model_v1.pkl')


def show_hiv_page():

    st.markdown(
    '<div class="section-title">HIV/AIDS Prediction</div>',
    unsafe_allow_html=True
    )
    st.title(':blue[Hiv/Aids Prediction]' , text_alignment="center")
    st.write("Fill in the questionnaire below.")


    with stylable_container(
    key="tb_card",
    css_styles="""
    {
        background: rgba(8,12,28,0.92);

        border-radius: 24px;

        padding: 32px;

        border: 1px solid rgba(120,119,198,0.18);

        transition:
            box-shadow 0.3s ease,
            border-color 0.3s ease;
    }

    &:hover {

        border-color: rgba(180,120,255,0.35);

        box-shadow:
            0 0 18px rgba(0,140,255,0.18),
            0 0 40px rgba(162,0,255,0.22);
    }
    """
    ):
        col1, col2 = st.columns(2)

        with col1:

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=18
            )

            marital_status = st.selectbox(
                "Marital Status",
                options=[
                    "unmarried",
                    "married",
                    "divorced",
                    "widowed",
                    "cohabiting"
                ],
                format_func=lambda x: x.replace("_", " ").title()
            )

            std = st.selectbox(
                "History of STD",
                options=["no", "yes"],
                format_func=lambda x: x.title()
            )

            educational_background = st.selectbox(
                "Educational Background",
                options=[
                    "college degree",
                    "senior high school",
                    "junior high school",
                    "illiteracy",
                    "primary school"
                ],
                format_func=lambda x: x.title()
            )

            hiv_test_in_past_year = st.selectbox(
                "HIV Test in Past Year",
                options=["no", "yes"],
                format_func=lambda x: x.title()
            )

        with col2:

            aids_education = st.selectbox(
                "Received AIDS Education",
                options=["no", "yes"],
                format_func=lambda x: x.title()
            )

            places_of_seeking_sex_partners = st.selectbox(
                "Places of Seeking Sex Partners",
                options=[
                    "bar",
                    "park",
                    "internet",
                    "public bath",
                    "others"
                ],
                format_func=lambda x: x.title()
            )

            sexual_orientation = st.selectbox(
                "Sexual Orientation",
                options=[
                    "heterosexual",
                    "bisexual",
                    "homosexual"
                ],
                format_func=lambda x: x.title()
            )

            drug_taking = st.selectbox(
                "Drug Taking",
                options=["no", "yes"],
                format_func=lambda x: x.title()
            )

    # PREDICTION BUTTON
    if st.button("Run Prediction"):

        input_data = pd.DataFrame([{

            "age": age,

            "marital_status": marital_status,

            "std": std,

            "educational_background":
                educational_background,

            "hiv_test_in_past_year":
                hiv_test_in_past_year,

            "aids_education":
                aids_education,

            "places_of_seeking_sex_partners":
                places_of_seeking_sex_partners,

            "sexual_orientation":
                sexual_orientation,

            "drug_taking":
                drug_taking
        }])

        with st.spinner("Analyzing patient data..."):

            time.sleep(1.5)

            pred = model.predict(input_data)[0]

            prob = model.predict_proba(input_data)[0][1]

        st.write("## Result")

        if pred == 1:

            st.error(
                f"High Risk of HIV/AIDS ({round(prob*100,2)}%)"
            )

            st.warning("""
            Recommendation:
            Please visit a healthcare center for proper
            testing and medical consultation.
            """)

        else:

            st.success(
                f"Low Risk of HIV/AIDS ({round((1-prob)*100,2)}%)"
            )

            st.info("""
            Maintain healthy habits and regular medical
            checkups.
            """)

        save_prediction(
            user_email=st.session_state['user'].email,
            disease='HIV/AIDS',
            input_data=input_data.to_dict(orient='records')[0],
            prediction=int(pred),
            probability=float(prob)
        )





