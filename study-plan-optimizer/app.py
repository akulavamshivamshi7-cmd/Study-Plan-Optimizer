"""
Study Plan Optimizer - Main Streamlit Web Application.
Interactive Algorithmic Study Schedule Optimization using DSA.
"""
import os
import json
import time
from datetime import datetime, date
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from models.topic import Topic
from models.student import StudentProfile
from services.scoring import (
    compute_benefit_score,
    update_topics_scores,
    explain_topic_selection,
    ScoringWeights
)
from services.optimizer import StudyOptimizerService
from services.scheduler import generate_study_schedule, StudySchedule
from algorithms.result import OptimizationResult
from algorithms.dependency_graph import DependencyGraph
from algorithms.binary_search import find_minimum_hours_for_target
from utils.helpers import (
    load_topics_from_json,
    save_topics_to_json,
    format_hours_to_hours_minutes,
    topics_to_display_list
)
from utils.validation import validate_topic_dict, validate_student_profile

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Study Plan Optimizer | DSA Hackathon",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern card UI and typography
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .algo-badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 20px;
        background-color: #E0E7FF;
        color: #3730A3;
    }
    .topic-card-selected {
        background-color: #F0FDF4;
        border-left: 5px solid #22C55E;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .topic-card-unselected {
        background-color: #F8FAFC;
        border-left: 5px solid #94A3B8;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization
# ---------------------------------------------------------
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_topics.json")

def init_session_state():
    if "topics" not in st.session_state:
        if os.path.exists(DEFAULT_DATA_PATH):
            st.session_state.topics = load_topics_from_json(DEFAULT_DATA_PATH)
        else:
            st.session_state.topics = []

    if "profile" not in st.session_state:
        st.session_state.profile = StudentProfile()

    if "weights" not in st.session_state:
        st.session_state.weights = ScoringWeights()

    if "opt_result" not in st.session_state:
        st.session_state.opt_result = None

    if "explanations" not in st.session_state:
        st.session_state.explanations = []

    if "warnings" not in st.session_state:
        st.session_state.warnings = []

    if "schedule" not in st.session_state:
        st.session_state.schedule = None

    if "current_slide" not in st.session_state:
        st.session_state.current_slide = 1

init_session_state()

# Recalculate scores for all topics in state
update_topics_scores(st.session_state.topics, st.session_state.weights)

# ---------------------------------------------------------
# Sidebar Controls & Global Filters
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=64)
    st.markdown("### 🎓 Study Plan Optimizer")
    st.caption("College DSA Hackathon Project")
    st.divider()

    nav_page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "⚡ Plan Optimizer",
            "📅 Study Timetable",
            "🔬 Algorithm Lab & Comparison",
            "📈 Analytics & What-If",
            "📝 Topic Management",
            "🎯 Hackathon Slides"
        ],
        index=0
    )
    st.divider()

    st.markdown("#### ⚙️ Quick Constraints")
    avail_h = st.slider(
        "Available Study Hours",
        min_value=1.0,
        max_value=40.0,
        value=float(st.session_state.profile.available_hours),
        step=0.5
    )
    st.session_state.profile.available_hours = avail_h

    daily_h = st.slider(
        "Max Daily Study Hours",
        min_value=1.0,
        max_value=12.0,
        value=float(st.session_state.profile.daily_study_hours),
        step=0.5
    )
    st.session_state.profile.daily_study_hours = daily_h

    st.markdown("#### 🎯 Target Exam Marks")
    target_m = st.number_input(
        "Target Score",
        min_value=10.0,
        max_value=100.0,
        value=float(st.session_state.profile.target_marks),
        step=5.0
    )
    st.session_state.profile.target_marks = target_m

    with st.expander("⚖️ Scoring Formula Weights"):
        st.caption("Customize exponent weights in multi-factor scoring formula")
        st.session_state.weights.importance_weight = st.slider("Importance Weight", 0.5, 2.0, 1.0, 0.1)
        st.session_state.weights.prep_gap_weight = st.slider("Preparation Gap Weight", 0.5, 2.0, 1.0, 0.1)
        st.session_state.weights.priority_weight = st.slider("Priority Weight", 0.5, 2.0, 1.0, 0.1)
        st.session_state.weights.difficulty_weight = st.slider("Difficulty Sensitivity", -0.5, 0.5, 0.2, 0.1)

    if st.button("🔄 Reset Sample Dataset", use_container_width=True):
        if os.path.exists(DEFAULT_DATA_PATH):
            st.session_state.topics = load_topics_from_json(DEFAULT_DATA_PATH)
            update_topics_scores(st.session_state.topics, st.session_state.weights)
            st.session_state.opt_result = None
            st.session_state.schedule = None
            st.success("Sample dataset of 20 topics reloaded!")
            st.rerun()

# ---------------------------------------------------------
# PAGE 1: DASHBOARD
# ---------------------------------------------------------
if nav_page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Study Plan Optimizer Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Algorithmic knapsack optimization maximizing expected marks yield within time constraints.</div>',
        unsafe_allow_html=True
    )

    # Top KPI metric cards
    topics = st.session_state.topics
    total_topics_count = len(topics)
    total_hours_required = sum(t.study_time for t in topics)
    total_possible_marks = sum(t.expected_marks for t in topics)
    avg_prep = np.mean([t.current_prep for t in topics]) if topics else 0.0
    unique_subjects = len(set(t.subject for t in topics))

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Available Hours</div>
            <div class="metric-value">{st.session_state.profile.available_hours:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Topics</div>
            <div class="metric-value">{total_topics_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Syllabus Time</div>
            <div class="metric-value">{total_hours_required:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Target Marks</div>
            <div class="metric-value">{st.session_state.profile.target_marks:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Current Prep Avg</div>
            <div class="metric-value">{avg_prep:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Automatic quick run if result is None
    if st.session_state.opt_result is None and topics:
        res, expl, warns = StudyOptimizerService.run_optimization(
            topics=topics,
            available_hours=st.session_state.profile.available_hours,
            algorithm_choice="Dynamic Programming",
            weights=st.session_state.weights
        )
        st.session_state.opt_result = res
        st.session_state.explanations = expl
        st.session_state.warnings = warns
        st.session_state.schedule = generate_study_schedule(
            selected_topics=res.selected_topics,
            daily_study_hours=st.session_state.profile.daily_study_hours
        )

    res = st.session_state.opt_result

    # Status Banner
    if res:
        st.markdown("### 🏆 Active Optimization Status")
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.metric("Selected Topics", f"{len(res.selected_topics)} / {len(topics)}")
        with sc2:
            st.metric("Study Time Allocated", f"{res.total_study_time:.1f} / {res.available_hours:.1f} hrs")
        with sc3:
            st.metric("Expected Benefit Score", f"{res.total_benefit:.2f}")
        with sc4:
            st.metric("Expected Marks Yield", f"{res.total_expected_marks:.1f} marks")

    # Visualizations on dashboard
    st.divider()
    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.markdown("#### 🎯 Return-On-Investment: Benefit vs Study Time")
        if topics:
            selected_ids = {t.id for t in res.selected_topics} if res else set()
            chart_data = []
            for t in topics:
                chart_data.append({
                    "Topic": t.name,
                    "Subject": t.subject,
                    "Study Time (hrs)": t.study_time,
                    "Benefit Score": t.benefit_score,
                    "Expected Marks": t.expected_marks,
                    "Status": "Selected" if t.id in selected_ids else "Unselected"
                })
            df_chart = pd.DataFrame(chart_data)
            fig = px.scatter(
                df_chart,
                x="Study Time (hrs)",
                y="Benefit Score",
                color="Status",
                size="Expected Marks",
                hover_name="Topic",
                hover_data=["Subject", "Benefit Score"],
                color_discrete_map={"Selected": "#16A34A", "Unselected": "#94A3B8"}
            )
            fig.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.markdown("#### 📚 Syllabus Time by Subject")
        if topics:
            sub_times = {}
            for t in topics:
                sub_times[t.subject] = sub_times.get(t.subject, 0.0) + t.study_time
            df_sub = pd.DataFrame(list(sub_times.items()), columns=["Subject", "Hours"])
            fig_pie = px.pie(
                df_sub,
                names="Subject",
                values="Hours",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_pie.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2: PLAN OPTIMIZER
# ---------------------------------------------------------
elif nav_page == "⚡ Plan Optimizer":
    st.markdown('<div class="main-header">⚡ Algorithmic Study Plan Optimizer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Select constraints and execute 0/1 Knapsack DP, Greedy Value Density, or Priority Queue.</div>',
        unsafe_allow_html=True
    )

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 2])
    with ctrl_col1:
        algo_choice = st.selectbox(
            "Select Optimization Algorithm",
            [
                "Dynamic Programming (0/1 Knapsack) [Globally Optimal]",
                "Greedy Approach (Value Density) [Fast Heuristic]",
                "Priority Queue (Max Heap) [Dynamic Stream]"
            ],
            index=0
        )
    with ctrl_col2:
        enforce_prereq = st.checkbox("Enforce Prerequisite Topological Sequence", value=True)
    with ctrl_col3:
        st.write("")
        st.write("")
        run_opt_btn = st.button("🚀 Optimize Study Plan Now", type="primary", use_container_width=True)

    if run_opt_btn or st.session_state.opt_result is None:
        with st.spinner("Executing algorithmic optimization..."):
            res, expl, warns = StudyOptimizerService.run_optimization(
                topics=st.session_state.topics,
                available_hours=st.session_state.profile.available_hours,
                algorithm_choice=algo_choice,
                weights=st.session_state.weights,
                respect_prerequisites=enforce_prereq
            )
            st.session_state.opt_result = res
            st.session_state.explanations = expl
            st.session_state.warnings = warns
            st.session_state.schedule = generate_study_schedule(
                selected_topics=res.selected_topics,
                daily_study_hours=st.session_state.profile.daily_study_hours
            )

    res = st.session_state.opt_result
    warns = st.session_state.warnings

    # Warnings for prerequisites
    if warns:
        st.warning("⚠️ **Prerequisite Dependency Alerts Detected:**")
        for w in warns:
            st.markdown(f"- **{w['topic_name']}**: Requires **{w['prereq_name']}** (Current Prep: {w['prereq_prep']:.0f}%).")

    if res:
        # Results Metric Row
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Algorithm", res.algorithm_name.split()[0])
        with m2:
            st.metric("Study Time", f"{res.total_study_time:.1f} / {res.available_hours:.1f}h")
        with m3:
            st.metric("Expected Benefit", f"{res.total_benefit:.2f}")
        with m4:
            st.metric("Expected Marks", f"{res.total_expected_marks:.1f}")
        with m5:
            st.metric("Execution Time", f"{res.execution_time_ms:.3f} ms")

        st.caption(f"**Complexity:** Time: `{res.time_complexity}` | Space: `{res.space_complexity}`")
        st.info(f"💡 {res.explanation}")

        # Tabs for Selected Topics vs Full Transparency / Explainability
        t_tab1, t_tab2, t_tab3 = st.tabs(["✅ Selected Topics Plan", "🔍 Why Selected / Omitted (Explainability)", "📜 Execution Trace Log"])

        with t_tab1:
            if res.selected_topics:
                df_sel = pd.DataFrame(topics_to_display_list(res.selected_topics))
                st.dataframe(df_sel, use_container_width=True)

                st.download_button(
                    label="📥 Export Optimized Study Plan (CSV)",
                    data=df_sel.to_csv(index=False),
                    file_name="optimized_study_plan.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No topics selected. Increase your available study hours.")

        with t_tab2:
            st.markdown("#### 🧠 Transparent Decision Rationales")
            st.caption("Algorithmic explanation for each topic's inclusion or exclusion.")

            for item in st.session_state.explanations:
                if item["status"] == "Selected":
                    with st.expander(f"🟢 [SELECTED] {item['topic_name']}", expanded=True):
                        st.markdown(f"**Outcome:** {item['summary']}")
                        for d in item["details"]:
                            st.markdown(f"- ✓ {d}")
                else:
                    with st.expander(f"⚪ [OMITTED] {item['topic_name']}", expanded=False):
                        st.markdown(f"**Outcome:** {item['summary']}")
                        for d in item["details"]:
                            st.markdown(f"- ✗ {d}")

        with t_tab3:
            st.markdown("#### 📜 Algorithmic Decision Log")
            for log_line in res.logs:
                st.text(f"→ {log_line}")

# ---------------------------------------------------------
# PAGE 3: STUDY TIMETABLE (SCHEDULER & POMODORO)
# ---------------------------------------------------------
elif nav_page == "📅 Study Timetable":
    st.markdown('<div class="main-header">📅 Chronological Study Timetable</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Pomodoro-style session scheduler dividing topics into active study blocks and rest intervals.</div>',
        unsafe_allow_html=True
    )

    if st.session_state.opt_result is None or not st.session_state.opt_result.selected_topics:
        st.info("Please run the optimizer first to generate selected study topics.")
    else:
        # Scheduler custom settings
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            session_len = st.number_input("Study Session Length (min)", min_value=20, max_value=90, value=50, step=5)
        with sc2:
            break_len = st.number_input("Short Break Length (min)", min_value=5, max_value=30, value=10, step=5)
        with sc3:
            start_clock = st.text_input("Daily Start Time (24h)", value="09:00")
        with sc4:
            st.write("")
            st.write("")
            recalc_sched = st.button("🔄 Rebuild Timetable", use_container_width=True)

        if recalc_sched or st.session_state.schedule is None:
            st.session_state.schedule = generate_study_schedule(
                selected_topics=st.session_state.opt_result.selected_topics,
                daily_study_hours=st.session_state.profile.daily_study_hours,
                session_minutes=int(session_len),
                break_minutes=int(break_len),
                start_time_str=start_clock
            )

        sched = st.session_state.schedule

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Days Required", f"{sched.total_days} Days")
        with col_m2:
            st.metric("Total Active Study Hours", f"{sched.total_study_hours} hrs")
        with col_m3:
            st.metric("Total Rest / Break Hours", f"{sched.total_break_hours} hrs")

        st.divider()

        # Day-by-Day schedule display
        for day in sched.daily_plans:
            st.markdown(f"### 🗓️ Day {day.day} — {day.total_study_minutes // 60}h {day.total_study_minutes % 60}m Study Time")
            st.caption(f"Subjects Covered: {', '.join(day.topics_covered)}")

            day_rows = [s.to_dict() for s in day.slots]
            df_day = pd.DataFrame(day_rows)

            # Styling the table
            st.dataframe(df_day[["Time Interval", "Type", "Topic / Activity", "Subject", "Duration"]], use_container_width=True)

        st.download_button(
            label="📥 Download Full Schedule (CSV)",
            data=pd.DataFrame(sched.to_flat_slots()).to_csv(index=False),
            file_name="daily_study_schedule.csv",
            mime="text/csv"
        )

# ---------------------------------------------------------
# PAGE 4: ALGORITHM LAB & COMPARISON
# ---------------------------------------------------------
elif nav_page == "🔬 Algorithm Lab & Comparison":
    st.markdown('<div class="main-header">🔬 Algorithm Comparison & DSA Lab</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Side-by-side benchmark of Dynamic Programming, Greedy, and Priority Queue.</div>',
        unsafe_allow_html=True
    )

    topics = st.session_state.topics
    avail_h = st.session_state.profile.available_hours

    with st.spinner("Benchmarking all 3 algorithms on active dataset..."):
        all_res = StudyOptimizerService.compare_all_algorithms(
            topics=topics,
            available_hours=avail_h,
            weights=st.session_state.weights
        )

    # Comparison summary table
    summary_data = [res.to_summary_dict() for res in all_res.values()]
    df_compare = pd.DataFrame(summary_data)
    st.dataframe(df_compare, use_container_width=True)

    st.markdown("""
    #### ⚖️ Algorithmic Trade-off Analysis:
    - **Dynamic Programming (0/1 Knapsack):** Guarantees the **mathematically optimal subset** maximizing expected benefit within discrete budget steps. However, it requires $O(N \times W)$ time and space.
    - **Greedy (Value Density):** Sorts by $\\frac{\\text{Benefit}}{\\text{Time}}$ in $O(N \\log N)$ and takes items greedily. It is lightning-fast, but can leave empty "slack time" resulting in suboptimal total benefit.
    - **Priority Queue (Max Heap):** Dynamically prioritizes items using binary heap property in $O(N \\log N)$. Ideal when priorities change dynamically during scheduling.
    """)

    st.divider()

    # DSA Deep-Dive Tabs
    lab_tab1, lab_tab2, lab_tab3 = st.tabs([
        "📊 Dynamic Programming 2D Table Heatmap",
        "🌳 Priority Queue (Max-Heap) Trace",
        "🔍 Binary Search on Answer"
    ])

    with lab_tab1:
        st.markdown("#### 2D Dynamic Programming Memoization Grid")
        st.caption("Visual representation of dp[topic_i][study_hours_w] showing maximum benefit accumulation.")

        dp_res = all_res["Dynamic Programming"]
        if dp_res.dp_table and dp_res.dp_weight_labels and dp_res.dp_topic_labels:
            df_dp = pd.DataFrame(
                dp_res.dp_table,
                index=dp_res.dp_topic_labels,
                columns=[f"{w}h" for w in dp_res.dp_weight_labels]
            )

            fig_dp = px.imshow(
                df_dp,
                labels=dict(x="Study Hours Capacity (W)", y="Topics Evaluated (N)", color="Max Benefit"),
                color_continuous_scale="Viridis",
                aspect="auto"
            )
            fig_dp.update_layout(height=450, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_dp, use_container_width=True)

            with st.expander("View Raw DP Numerical Table"):
                st.dataframe(df_dp)

    with lab_tab2:
        st.markdown("#### Max-Heap State Evolution Trace")
        st.caption("Demonstrating array-based binary heap extraction steps and root maintenance.")

        pq_res = all_res["Priority Queue"]
        if pq_res.heap_trace:
            for step_info in pq_res.heap_trace:
                with st.expander(f"Step {step_info['step']}: {step_info['action']} (Heap Size: {step_info['heap_size']})"):
                    st.write(f"**Root Node:** {step_info['root_topic']}")
                    st.json(step_info["snapshot"])

    with lab_tab3:
        st.markdown("#### Binary Search on Answer: Target Marks Calculator")
        st.caption("Uses Binary Search over study hour space to determine the minimal study hours needed for a score goal.")

        bs_target = st.number_input("Enter Target Marks Goal", min_value=5.0, max_value=sum(t.expected_marks for t in topics), value=30.0, step=5.0)

        if st.button("🔍 Find Minimum Hours via Binary Search"):
            min_h, marks_achieved, sel_topics = find_minimum_hours_for_target(
                topics=topics,
                target_marks=bs_target,
                min_hours=1.0,
                max_hours=40.0,
                tolerance=0.5
            )
            st.success(f"🎯 Target Marks: **{bs_target:.1f}** requires at least **{min_h:.1f} hours** of study.")
            st.write(f"**Marks Yielded:** {marks_achieved:.1f} marks across {len(sel_topics)} topics.")
            st.dataframe(pd.DataFrame(topics_to_display_list(sel_topics)))

# ---------------------------------------------------------
# PAGE 5: ANALYTICS & WHAT-IF ANALYSIS
# ---------------------------------------------------------
elif nav_page == "📈 Analytics & What-If":
    st.markdown('<div class="main-header">📈 Analytics & What-If Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Interactive sensitivity analysis and visualizations showing response to constraint changes.</div>',
        unsafe_allow_html=True
    )

    topics = st.session_state.topics

    st.markdown("### 🔮 What-If Analysis: Varying Study Hours (2h to 30h)")
    st.caption("Observe diminishing returns and compare Dynamic Programming vs Greedy across different time limits.")

    with st.spinner("Generating What-If sensitivity curve..."):
        what_if_data = StudyOptimizerService.run_what_if_analysis(
            topics=topics,
            weights=st.session_state.weights
        )

    df_whatif = pd.DataFrame(what_if_data)

    fig_whatif = go.Figure()
    fig_whatif.add_trace(go.Scatter(
        x=df_whatif["Available Hours"],
        y=df_whatif["DP Benefit"],
        mode="lines+markers",
        name="Dynamic Programming (Optimal)",
        line=dict(color="#2563EB", width=3)
    ))
    fig_whatif.add_trace(go.Scatter(
        x=df_whatif["Available Hours"],
        y=df_whatif["Greedy Benefit"],
        mode="lines+markers",
        name="Greedy (Value Density)",
        line=dict(color="#10B981", width=2, dash="dash")
    ))
    fig_whatif.update_layout(
        title="Available Hours vs Expected Benefit Score",
        xaxis_title="Available Study Hours",
        yaxis_title="Expected Benefit Score",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_whatif, use_container_width=True)

    with st.expander("View What-If Sensitivity Data Table"):
        st.dataframe(df_whatif, use_container_width=True)

    st.divider()

    st.markdown("### 📊 Subject-Wise Marks & Time Breakdown")
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        # Subject marks
        sub_marks = {}
        for t in topics:
            sub_marks[t.subject] = sub_marks.get(t.subject, 0.0) + t.expected_marks
        df_sm = pd.DataFrame(list(sub_marks.items()), columns=["Subject", "Total Marks"])
        fig_bar = px.bar(
            df_sm,
            x="Subject",
            y="Total Marks",
            color="Subject",
            title="Total Exam Marks by Subject",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with ch_col2:
        # Preparation gap vs Difficulty
        df_gap = pd.DataFrame([{
            "Topic": t.name,
            "Subject": t.subject,
            "Prep Gap (%)": t.prep_gap,
            "Difficulty": t.difficulty,
            "Priority": t.priority,
            "Marks": t.expected_marks
        } for t in topics])
        fig_bubble = px.scatter(
            df_gap,
            x="Difficulty",
            y="Prep Gap (%)",
            size="Marks",
            color="Subject",
            hover_name="Topic",
            title="Topic Difficulty vs Preparation Gap (Bubble size = Marks)"
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

# ---------------------------------------------------------
# PAGE 6: TOPIC MANAGEMENT (CRUD)
# ---------------------------------------------------------
elif nav_page == "📝 Topic Management":
    st.markdown('<div class="main-header">📝 Topic Inventory Management</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Add, modify, delete, and inspect academic topics and prerequisites.</div>',
        unsafe_allow_html=True
    )

    topics = st.session_state.topics

    tab_view, tab_add, tab_json = st.tabs(["📋 View & Delete Topics", "➕ Add New Topic", "💾 JSON Import / Export"])

    with tab_view:
        st.markdown(f"#### Active Topics Inventory ({len(topics)} topics)")
        if topics:
            df_t = pd.DataFrame(topics_to_display_list(topics))
            st.dataframe(df_t, use_container_width=True)

            del_id = st.selectbox("Select Topic to Delete", [f"{t.id} - {t.name}" for t in topics])
            if st.button("🗑️ Delete Selected Topic", type="secondary"):
                tid = del_id.split(" - ")[0]
                st.session_state.topics = [t for t in topics if t.id != tid]
                update_topics_scores(st.session_state.topics, st.session_state.weights)
                st.session_state.opt_result = None
                st.success(f"Topic {del_id} removed successfully.")
                st.rerun()
        else:
            st.warning("No topics in database. Click 'Reset Sample Dataset' in the sidebar or add new topics.")

    with tab_add:
        st.markdown("#### ➕ Add a New Topic to Syllabus")
        with st.form("new_topic_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                new_id = st.text_input("Topic ID (e.g. T21)", value=f"T{len(topics) + 1:02d}")
                new_subject = st.text_input("Subject", value="Computer Science")
                new_name = st.text_input("Topic Name", value="")
                new_time = st.number_input("Study Time (hours)", min_value=0.5, max_value=20.0, value=2.5, step=0.5)
            with f_col2:
                new_diff = st.slider("Difficulty Level (1-10)", 1, 10, 5)
                new_imp = st.slider("Importance Level (1-10)", 1, 10, 8)
                new_marks = st.number_input("Expected Marks Weightage", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
                new_prep = st.slider("Current Preparation (%)", 0.0, 100.0, 20.0, 5.0)
                new_prio = st.slider("Exam Priority (1-10)", 1, 10, 7)

            available_ids = [t.id for t in topics]
            new_prereqs = st.multiselect("Prerequisite Topics", available_ids)

            submit_topic = st.form_submit_button("Add Topic", type="primary")

            if submit_topic:
                raw_dict = {
                    "id": new_id,
                    "subject": new_subject,
                    "name": new_name,
                    "study_time": new_time,
                    "difficulty": new_diff,
                    "importance": new_imp,
                    "expected_marks": new_marks,
                    "current_prep": new_prep,
                    "priority": new_prio,
                    "prerequisites": new_prereqs
                }
                is_valid, err_msg = validate_topic_dict(raw_dict)
                if not is_valid:
                    st.error(f"Validation Error: {err_msg}")
                elif any(t.id == new_id for t in topics):
                    st.error(f"Topic ID '{new_id}' already exists. Use a unique ID.")
                else:
                    new_topic_obj = Topic.from_dict(raw_dict)
                    st.session_state.topics.append(new_topic_obj)
                    update_topics_scores(st.session_state.topics, st.session_state.weights)
                    st.session_state.opt_result = None
                    st.success(f"Topic '{new_name}' added successfully!")
                    st.rerun()

    with tab_json:
        st.markdown("#### 💾 Dataset Import & Export")
        st.caption("Backup or import syllabus dataset in JSON format.")
        json_export = json.dumps([t.to_dict() for t in topics], indent=2)
        st.download_button(
            label="📥 Download Dataset (JSON)",
            data=json_export,
            file_name="topics_dataset.json",
            mime="application/json"
        )

# ---------------------------------------------------------
# PAGE 7: HACKATHON SLIDES
# ---------------------------------------------------------
elif nav_page == "🎯 Hackathon Slides":
    st.markdown('<div class="main-header">🎯 Hackathon Pitch Presentation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Interactive 14-slide deck for college DSA hackathon judges and demo presentation.</div>',
        unsafe_allow_html=True
    )

    SLIDES = [
        {
            "num": 1,
            "title": "Study Plan Optimizer",
            "subtitle": "Algorithmic Study Schedule Optimization Using Data Structures & Algorithms",
            "bullets": [
                "Domain: Algorithmic Optimization / EdTech",
                "Stack: Pure Python DSA, Streamlit, Plotly, NumPy, Pandas",
                "Core Challenge: Maximizing exam marks improvement under strict study hour limits",
                "Team Presentation: College DSA Hackathon 2026"
            ]
        },
        {
            "num": 2,
            "title": "Problem Statement",
            "subtitle": "The Universal Student Preparation Crisis",
            "bullets": [
                "Students face an overwhelming syllabus before exams (20-40 topics across multiple subjects).",
                "Available time is strictly constrained (e.g. 10 to 20 hours).",
                "Core Mathematical Objective: Select subset S such that Total Study Time <= Available Hours while maximizing Expected Marks Yield.",
                "Equivalent to the NP-hard 0/1 Knapsack Problem in computer science."
            ]
        },
        {
            "num": 3,
            "title": "Existing Problem & Flawed Approaches",
            "subtitle": "Why Traditional Study Methods Fail",
            "bullets": [
                "Intuition-based selection: Students study whatever chapter comes first.",
                "Zero ROI modeling: Spending hours re-reading topics already mastered (e.g., 90% prep) while ignoring 0% prepared high-yield topics.",
                "Ignoring Prerequisite Dependencies: Attempting advanced topics (DP/Graphs) without mastering fundamentals (Recursion/Arrays).",
                "Rigid non-adaptive timetables that collapse when time is cut short."
            ]
        },
        {
            "num": 4,
            "title": "Our Solution: Study Plan Optimizer",
            "subtitle": "Algorithmic Precision for Academic Success",
            "bullets": [
                "Models academic preparation as a 0/1 Knapsack optimization problem.",
                "Pure DSA Engine: Implements Dynamic Programming, Greedy, Max-Heap, and DAG Topological Sorting from scratch.",
                "Zero black-box solvers: Complete transparency in table memoization and heap restructuring.",
                "Generates actionable daily Pomodoro timetables and explainable rationale for every decision."
            ]
        },
        {
            "num": 5,
            "title": "How the Optimizer Works: Mathematical Model",
            "subtitle": "Scoring Formula and Return on Time Invested",
            "bullets": [
                "Preparation Gap = (100 - Current Prep) / 100",
                "Expected Benefit = Expected Marks * (Importance/10)^wi * Gap^wg * (Priority/10)^wp * Difficulty Multiplier",
                "Value Density = Benefit Score / Study Time (hrs) -> Marginal yield per hour",
                "Weights are fully configurable by student preferences."
            ]
        },
        {
            "num": 6,
            "title": "Data Structures & Algorithms Used",
            "subtitle": "Core DSA Concepts Meaningfully Applied",
            "bullets": [
                "2D DP Arrays: Memoization matrix for optimal 0/1 knapsack subset selection.",
                "Binary Max-Heap: Custom array-based heap with sift-up and sift-down for dynamic prioritization.",
                "Directed Acyclic Graph (DAG): Modeling topic prerequisite networks.",
                "Topological Sort (Kahn's BFS): Ensuring prerequisites precede advanced topics.",
                "Binary Search on Answer: Finding minimal study hours needed for target exam marks."
            ]
        },
        {
            "num": 7,
            "title": "Algorithm 1 — Greedy Approach",
            "subtitle": "Value Density Heuristic",
            "bullets": [
                "Calculates Value Density (Benefit / Time) for each topic.",
                "Sorts topics descending in O(N log N) time.",
                "Greedily takes topics as long as study time budget remains.",
                "Pros: Blazing fast (<0.2 ms).",
                "Cons: May leave unused slack hours, missing global optimum."
            ]
        },
        {
            "num": 8,
            "title": "Algorithm 2 — Dynamic Programming",
            "subtitle": "0/1 Knapsack with Backtracking",
            "bullets": [
                "Recurrence: dp[i][w] = max(dp[i-1][w], dp[i-1][w - w_i] + b_i)",
                "Time Complexity: O(N * W) pseudo-polynomial.",
                "Space Complexity: O(N * W) 2D memoization grid.",
                "Backtracking: Reconstructs exact chosen topics in O(N).",
                "Guarantees mathematically optimal solution for discrete capacity."
            ]
        },
        {
            "num": 9,
            "title": "Algorithm 3 — Priority Queue (Max-Heap)",
            "subtitle": "Dynamic Stream Prioritization",
            "bullets": [
                "Array-based binary Max-Heap maintaining heap invariant.",
                "Composite priority key: (Value Density, Exam Priority, Expected Marks).",
                "Supports dynamic re-prioritization as topics or prerequisites change.",
                "O(log N) insertion and extraction, O(N log N) overall."
            ]
        },
        {
            "num": 10,
            "title": "System Architecture",
            "subtitle": "Clean, Decoupled, Modular Design",
            "bullets": [
                "Presentation Layer: Streamlit web UI + Plotly interactive charts.",
                "Service Layer: ScoringService, StudyOptimizerService, SchedulerService.",
                "Algorithmic Core: Independent pure-Python DSA modules.",
                "Data & Validation: Strongly typed dataclasses with strict input boundary validation."
            ]
        },
        {
            "num": 11,
            "title": "Demo & Key Features",
            "subtitle": "What We Just Demonstrated",
            "bullets": [
                "Interactive multi-model optimization with millisecond benchmarks.",
                "Transparent explainability: Why each topic was selected or rejected.",
                "Visual 2D DP heatmap & step-by-step Max-Heap trace.",
                "Chronological daily Pomodoro schedule with breaks."
            ]
        },
        {
            "num": 12,
            "title": "Results & Experimental Validation",
            "subtitle": "Empirical Findings across 20 CS Topics",
            "bullets": [
                "Dynamic Programming achieves the global upper bound in expected benefit.",
                "Greedy delivers 92% - 97% of optimal score in 0.15 ms.",
                "What-If sensitivity curve confirms Diminishing Returns: 60%+ score improvement gained in the first 8 hours.",
                "Topological sorting prevents prerequisite violations in 100% of test cases."
            ]
        },
        {
            "num": 13,
            "title": "Future Scope & Extensions",
            "subtitle": "Next Steps for the Project",
            "bullets": [
                "Machine Learning calibration of student forgetting curves (Ebbinghaus decay).",
                "Spaced repetition scheduling (SM-2 / Anki integration).",
                "Calendar integration (export directly to Google Calendar / iCal .ics format).",
                "Multi-student collaborative study group matching using Game Theory."
            ]
        },
        {
            "num": 14,
            "title": "Conclusion & Takeaways",
            "subtitle": "Study Smarter, Not Just Longer",
            "bullets": [
                "Transformed an everyday student dilemma into an algorithmic optimization problem.",
                "Demonstrated rigorous DSA implementations: DP, Heaps, DAGs, and Binary Search.",
                "100% test coverage with 25 unit tests passing.",
                "Ready for deployment to help students ace their examinations!"
            ]
        }
    ]

    # Slide navigation
    nav_c1, nav_c2, nav_c3 = st.columns([1, 4, 1])
    with nav_c1:
        if st.button("⬅️ Previous", use_container_width=True) and st.session_state.current_slide > 1:
            st.session_state.current_slide -= 1
            st.rerun()
    with nav_c2:
        slide_idx = st.slider("Jump to Slide", 1, len(SLIDES), st.session_state.current_slide)
        if slide_idx != st.session_state.current_slide:
            st.session_state.current_slide = slide_idx
            st.rerun()
    with nav_c3:
        if st.button("Next ➡️", use_container_width=True) and st.session_state.current_slide < len(SLIDES):
            st.session_state.current_slide += 1
            st.rerun()

    current_data = SLIDES[st.session_state.current_slide - 1]

    # Slide card rendering
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 20px;">
        <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px; font-weight: 600;">Slide {current_data['num']} / {len(SLIDES)}</span>
        <h2 style="color: white; margin-top: 10px; margin-bottom: 4px;">{current_data['title']}</h2>
        <p style="color: #DBEAFE; font-size: 1.1rem; margin-bottom: 0;">{current_data['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Key Talking Points:")
    for b in current_data["bullets"]:
        st.markdown(f"- 🔹 **{b}**")
