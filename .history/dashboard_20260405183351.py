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


# ── Sidebar Filters ─────────────────────
st.sidebar.title("🔍 Filters")

expertise_list = sorted(teachers["Expertise"].unique().tolist())
selected_expertise = st.sidebar.multiselect(
    "Instructor Expertise",
    expertise_list,
    default=expertise_list
)

level_list = sorted(courses["CourseLevel"].unique().tolist())
selected_level = st.sidebar.multiselect(
    "Course Level",
    level_list,
    default=level_list
)

# Filter apply karo
t_filtered = teachers[teachers["Expertise"].isin(selected_expertise)]
m_filtered = master[
    (master["Expertise"].isin(selected_expertise)) &
    (master["CourseLevel"].isin(selected_level))
]

st.markdown("---")

# ── Chart 1: Rating Distribution ────────
st.subheader("📊 Teacher Rating Distribution")

fig1 = px.histogram(
    t_filtered,
    x="TeacherRating",
    nbins=20,
    color_discrete_sequence=['#2563EB'],
    labels={'TeacherRating': 'Teacher Rating'}
)
fig1.add_vline(
    x=t_filtered["TeacherRating"].mean(),
    line_dash='dash',
    line_color='red',
    annotation_text=f"Mean: {t_filtered['TeacherRating'].mean():.2f}"
)
fig1.update_layout(plot_bgcolor='white')
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ── Chart 2: Top 10 Teachers ─────────────
st.subheader("🏆 Top 10 Teachers by Enrollments")

top10 = t_filtered.nlargest(10, 'Enrollments')

fig2 = px.bar(
    top10.sort_values('Enrollments'),
    x='Enrollments',
    y='TeacherName',
    orientation='h',
    color='TeacherRating',
    color_continuous_scale='Blues',
    text='Enrollments'
)
fig2.update_traces(textposition='outside')
fig2.update_layout(plot_bgcolor='white')
st.plotly_chart(fig2, use_container_width=True)