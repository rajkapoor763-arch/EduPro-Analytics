import streamlit as st
import pandas as pd
import plotly.express as px


# ── Custom CSS — Dark Theme ──────────────
st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] {
    background-color: #0f1117;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #161b27;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #1e2535;
    border: 1px solid #2e3a50;
    border-radius: 12px;
    padding: 15px;
}

/* Metric value color */
[data-testid="stMetricValue"] {
    color: #4f9eff;
    font-size: 1.8rem;
}

/* All text white */
h1, h2, h3, p, label {
    color: #e2e8f0 !important;
}

/* Divider color */
hr {
    border-color: #2e3a50;
}
</style>
""", unsafe_allow_html=True)



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


# ── Animated Header ──────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e3a5f, #2563eb);
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
">
    <h1 style="
        color: white;
        font-size: 2.5rem;
        margin: 0;
    ">🎓 EduPro Analytics Dashboard</h1>
    <p style="
        color: #93c5fd;
        font-size: 1.1rem;
        margin-top: 10px;
    ">Data-driven Instructor & Course Quality Evaluation</p>
    <p style="
        color: #60a5fa;
        font-size: 0.9rem;
    ">60 Teachers · 60 Courses · 10,000 Transactions</p>
</div>
""", unsafe_allow_html=True)

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


# ── Chart 3: Experience vs Rating ────────
st.subheader("📈 Experience vs Teacher Rating")

fig3 = px.scatter(
    t_filtered,
    x='YearsOfExperience',
    y='TeacherRating',
    color='Gender',
    size='TeacherRating',
    hover_name='TeacherName',
    trendline='ols',
    color_discrete_map={'Male': '#2563EB', 'Female': '#EC4899'},
    labels={
        'YearsOfExperience': 'Years of Experience',
        'TeacherRating': 'Teacher Rating'
    }
)
fig3.update_layout(plot_bgcolor='white')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── Chart 4: Category Ratings ────────────
st.subheader("🎯 Course Rating by Category")

category_rating = m_filtered.groupby('CourseCategory')['CourseRating']\
                             .mean().round(2)\
                             .reset_index()\
                             .sort_values('CourseRating')

fig4 = px.bar(
    category_rating,
    x='CourseRating',
    y='CourseCategory',
    orientation='h',
    color='CourseRating',
    color_continuous_scale='RdYlGn',
    text='CourseRating',
    labels={'CourseCategory': 'Category', 'CourseRating': 'Avg Rating'}
)
fig4.update_traces(textposition='outside')
fig4.update_layout(plot_bgcolor='white', coloraxis_showscale=False)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── Chart 5: Tier vs Enrollments ─────────
st.subheader("💰 Instructor Tier vs Enrollments")

tier_avg = t_filtered.groupby('Tier', observed=True)['Enrollments']\
                     .mean().round(0).reset_index()

fig5 = px.bar(
    tier_avg,
    x='Tier',
    y='Enrollments',
    color='Tier',
    color_discrete_map={
        'Low': '#EF4444',
        'Mid': '#F59E0B',
        'High': '#22C55E'
    },
    text='Enrollments'
)
fig5.update_traces(textposition='outside')
fig5.update_layout(plot_bgcolor='white', showlegend=False)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── Chart 6: Heatmap ─────────────────────
st.subheader("🔥 Course Rating Heatmap: Category vs Level")

heatmap_data = m_filtered.groupby(
    ['CourseCategory', 'CourseLevel']
)['CourseRating'].mean().unstack().round(2)

fig6 = px.imshow(
    heatmap_data,
    color_continuous_scale='RdYlGn',
    zmin=1, zmax=5,
    text_auto=True,
    aspect='auto',
    labels={'x': 'Course Level', 'y': 'Category', 'color': 'Avg Rating'}
)
fig6.update_layout(width=700, height=500)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ── Leaderboard Table ─────────────────────
st.subheader("🏅 Instructor Leaderboard")

leaderboard = t_filtered[['TeacherName', 'Expertise', 'Gender',
                           'YearsOfExperience', 'TeacherRating',
                           'Enrollments', 'Tier']]\
                .sort_values('TeacherRating', ascending=False)\
                .reset_index(drop=True)

leaderboard.index += 1
st.dataframe(leaderboard, use_container_width=True)

st.markdown("---")
st.caption("EduPro Analytics Dashboard | 60 Teachers · 60 Courses · 10,000 Transactions")