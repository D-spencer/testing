from supabase import create_client
import streamlit as st

SUPABASE_URL =  st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL, 
    SUPABASE_KEY)



def save_prediction(
        user_email,
        disease,
        input_data,
        prediction,
        probability
):
    try:
        data = {
        "user_email": user_email,
        "disease": disease,
        "input_data": input_data,
        "prediction": prediction,
        "probability": probability
        }

        response = supabase.table("predictions").insert(data).execute()
        return response
    except Exception as e:
        st.error(f"Failed to save to database: {e}")



#-------------prediction history----------------
def get_prediction_history(user_email):
    try:
        response = (
            supabase
            .table("predictions")
            .select("*")
            .eq("user_email", user_email)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        st.error(f"Failed to fetch prediction history: {e}")
        return []
        

#--------------get all predictions for admin----------------
def get_all_predictions():
    try:
        response = (
            supabase
            .table("predictions")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        st.error(f"Failed to fetch all predictions: {e}")
        return []
    

#--------------role function----------------

def get_user_role(user_id):
    try:
        response = (
            supabase
            .table("user_roles")
            .select("role")
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            return response.data[0]["role"]

        # Default role if no record exists
        return "user"

    except Exception as e:
        st.error(f"Failed to fetch user role: {e}")
        return "user"


# ================= SAVE FEEDBACK =================
def save_feedback(user_email, feedback):

    try:

        response = supabase.table("feedback").insert({

            "user_email": user_email,
            "feedback": feedback

        }).execute()

        return response

    except Exception as e:
        st.error(f"Feedback Error: {e}")


def get_user_name(user_id):
    result = supabase.table("profiles") \
        .select("full_name") \
        .eq("id", user_id) \
        .single() \
        .execute()

    if result.data:
        return result.data["full_name"]

    return "User"


# from supabase import create_client
# import streamlit as st


# def get_supabase():
#     return create_client(
#         st.secrets["SUPABASE_URL"],
#         st.secrets["SUPABASE_KEY"]
#     )


# # ================= SAVE PREDICTION =================
# def save_prediction(
#         user_email,
#         disease,
#         input_data,
#         prediction,
#         probability
# ):
#     supabase = get_supabase()

#     try:
#         data = {
#             "user_email": user_email,
#             "disease": disease,
#             "input_data": input_data,
#             "prediction": prediction,
#             "probability": probability
#         }

#         response = supabase.table("predictions").insert(data).execute()
#         return response

#     except Exception as e:
#         st.error(f"Failed to save to database: {e}")


# # ================= USER HISTORY =================
# def get_prediction_history(user_email):
#     supabase = get_supabase()

#     try:
#         response = (
#             supabase
#             .table("predictions")
#             .select("*")
#             .eq("user_email", user_email)
#             .order("created_at", desc=True)
#             .execute()
#         )

#         return response.data

#     except Exception as e:
#         st.error(f"Failed to fetch prediction history: {e}")
#         return []


# # ================= ADMIN HISTORY =================
# def get_all_predictions():
#     supabase = get_supabase()

#     try:
#         response = (
#             supabase
#             .table("predictions")
#             .select("*")
#             .order("created_at", desc=True)
#             .execute()
#         )

#         return response.data

#     except Exception as e:
#         st.error(f"Failed to fetch all predictions: {e}")
#         return []


# # ================= USER ROLE =================
# # def get_user_role(user_id):
# #     supabase = get_supabase()

# #     try:
# #         response = (
# #             supabase
# #             .table("user_roles")
# #             .select("role")
# #             .eq("id", user_id)
# #             .execute()
# #         )

# #         if response.data:
# #             return response.data[0]["role"]

# #         return "user"

# #     except Exception as e:
# #         st.error(f"Failed to fetch user role: {e}")
# #         return "user"


# def get_user_role(user_id):
#     try:
#         supabase = get_supabase()

#         response = (
#             supabase
#             .table("user_roles")
#             .select("*")
#             .eq("id", user_id)
#             .execute()
#         )

      
#         if response.data:
#             return response.data[0]["role"]

#         return "user"

#     except Exception as e:
#         st.error(f"Failed to fetch user role: {e}")
#         return "user"

# # ================= FEEDBACK =================
# def save_feedback(user_email, feedback):
#     supabase = get_supabase()

#     try:
#         response = (
#             supabase
#             .table("feedback")
#             .insert({
#                 "user_email": user_email,
#                 "feedback": feedback
#             })
#             .execute()
#         )

#         return response

#     except Exception as e:
#         st.error(f"Feedback Error: {e}")


# # ================= USER NAME =================
# def get_user_name(user_id):
#     supabase = get_supabase()

#     try:
#         result = (
#             supabase
#             .table("profiles")
#             .select("full_name")
#             .eq("id", user_id)
#             .single()
#             .execute()
#         )

#         if result.data:
#             return result.data["full_name"]

#     except Exception as e:
#         st.error(f"Failed to fetch user name: {e}")

#     return "User"