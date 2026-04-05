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
    teachers     = pd.read_csv("EduPro Online Platform.xlsx-Teachers.csv")
    courses      = pd.read_csv("EduPro Online Platform.xlsx-Courses.csv")
    transactions = pd.read_csv("EduPro Online Platform.xlsx-Transactions.csv")

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