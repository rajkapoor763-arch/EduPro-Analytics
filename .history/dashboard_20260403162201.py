import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config( 
    page_title="EduPro Analytics", 
    page_icon="🎓",
    layout="wide"
)

@st.cache_data
def load_data():
    teachers     = pd.read_csv("EduPro Online Platform.xlsx - Teachers.csv")
    courses      = pd.read_csv("EduPro Online Platform.xlsx - Courses.csv")
    transactions = pd.read_csv("EduPro Online Platform.xlsx - Transactions.csv")

    teachers["Tier"] = pd.cut(
        teachers["TeacherRating"],
        bins=[0, 2, 3.5, 5],
        labels=["Low", "Mid", "High"]
    )
    enroll = transactions.groupby("TeacherID")\
                         .size().reset_index(name='Enrollments')
    teachers = teachers.merge(enroll, on="TeacherID", how="left")
    master = transactions.merge(teachers, on="TeacherID")\
                         .merge(courses, on="CourseID")
    return teachers, courses, master

teachers, courses, master = load_data()

st.title("🎓 EduPro — Instructor & Course Analytics")
st.markdown("*Data-driven evaluation of teaching effectiveness*")
st.markdown("---")

st.subheader("📌 Key Metrics")

k1,k2,k3,k4=st.columns(4)

k1.metric("Avg Teacher Rating", 
          f"{teachers['TeacherRating'].mean():.2f} ⭐")

k2.metric("Avg Course Rating",  
          f"{courses['CourseRating'].mean():.2f} ⭐")

k3.metric("Total Enrollments",  
          f"{len(master):,}")

k4.metric("Total Teachers",     
          f"{teachers['TeacherID'].nunique()}")

st.markdown("---")