import streamlit as st
import pandas as pd
import time
import joblib
from database import save_prediction
from streamlit_extras.stylable_container import stylable_container

model = joblib.load('model/TB_model_v1.pkl')



def yes_no(question):
    answer = st.selectbox(
        question, 
        options=['No','Yes'],
            format_func=lambda x: x.title()
    )
    return 1 if answer == 'Yes' else 0

def show_tb_page():

    st.markdown(
    '<div class="section-title">TB Prediction</div>',
    unsafe_allow_html=True
    )
    st.title(':blue[Tuberculosis Prediction]' , text_alignment="center")
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
       
        col1, col2, col3 = st.columns(
        [1,1,1],
        gap="large"
         )

        with col1: 
            fever = yes_no(
                'Have you had fever for more than 2 weeks '
            )

            cough_blood = yes_no(''
            'Are you coughing blood'
            )

            night_sweat = yes_no(
                'Do you experience night sweats'
            )

            chest_pain = yes_no(
            'Do you have a chest pain'
            )
            st.markdown("<br>", unsafe_allow_html=True)
        with col2:
            back_pain = yes_no(
            'Do you have a back pain'
            )

            sputum = yes_no(
            'Is your sputum or mucus mixed with blood'
            )
        
            breath_shortness = yes_no(
            'Do you experience shortness of breath'
            )

            weight_loss = yes_no(
            'Have you experience unexplained weight loss recently'
            )
        st.markdown("<br>", unsafe_allow_html=True)
        with col3:
            body_feel_tired = yes_no(
            'Do you often feel unusually tired or weak'
            )

            lumps = yes_no(
            'Have you noticed any lumps or swellimg on your body'
            )

            continuous_cough = yes_no(
            'Have you had a continuous cough with phlegm'
            )

            swollen_lymph_nodes = yes_no(
            'Do you have swollen lymph nodes'
            )

            loss_of_appetite = yes_no(
                'Have you experienced loss of appetite recently'
            )

    if st.button('Run Prediction'):

        input_data = pd.DataFrame([{
            'two_weeks_fever':fever,
            'coughing_blood': cough_blood,
            'sputum_mixed_with_blood': sputum,
            'night_sweats': night_sweat,
            'chest_pain': chest_pain,
            'back_pain': chest_pain,
            'breath_shortness': breath_shortness,
            'weight_loss': weight_loss,
            'body_feels_tired': body_feel_tired,
            'lumps': lumps,
            'continuous_cough_and_phlegm':continuous_cough,
            'swollen_lymph_nodes': swollen_lymph_nodes,
            'loss_of_appetite': loss_of_appetite
        }])

        with st.spinner('Analyxing patient data...'):
            time.sleep(1.5)

            pred = model.predict(input_data)[0]
            prob = model.predict_proba(input_data)[0][1]

            st.write("### Result")

            if pred == 1:
                st.error(F'High Risk of TB ({round(prob*100,2)}%)')

                st.warning("""
            Recommendation:
            Please visit a healthcare center for proper
            testing and medical consultation.
            """)
            else: 
                st.success(f'Low Risk of TB({round(prob*100, 2)}%)')
                st.info("""
            Maintain healthy habits and regular medical
            checkups.
            """)
                
        save_prediction(
            user_email=st.session_state['user'].email,
            disease='Tuberculosis',
            input_data=input_data.to_dict(orient='records')[0],
            prediction=int(pred),
            probability=float(prob)
        )
