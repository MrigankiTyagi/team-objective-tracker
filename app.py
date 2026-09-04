import streamlit as st
from datetime import date

from database import (
    get_teams,
    get_objectives,
    create_objective,
    update_objective,
    create_meeting,
    get_meetings,
    create_progress_update,
    get_progress_history
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Team Objective Tracker",
    layout="wide"
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Team Objective Tracker")

st.sidebar.markdown(
    "Meeting notes, objectives and progress"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Objectives",
        "Meeting Notes",
        "Progress Updates"
    ]
)

st.sidebar.divider()

team_filter = st.sidebar.selectbox(
    "Team",
    [
        "All Teams",
        "Team A",
        "Team B"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("Dashboard")

    objectives = get_objectives(
        team_filter
    )

    total = len(objectives)

    completed = len([
        x for x in objectives
        if x["status"] == "Completed"
    ])

    at_risk = len([
        x for x in objectives
        if x["status"] == "At Risk"
    ])

    in_progress = len([
        x for x in objectives
        if x["status"] == "In Progress"
    ])

    if total:
        average = round(
            sum(
                x["progress"]
                for x in objectives
            ) / total
        )
    else:
        average = 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Objectives",
        total
    )

    c2.metric(
        "Average Achievement",
        f"{average}%"
    )

    c3.metric(
        "Completed",
        completed
    )

    c4.metric(
        "At Risk",
        at_risk
    )

    st.divider()

    st.subheader("Objective Progress")

    if not objectives:

        st.info(
            "No objectives have been created."
        )

    for objective in objectives:

        with st.container(border=True):

            left, right = st.columns(
                [3, 1]
            )

            with left:

                st.markdown(
                    f"### {objective['objective']}"
                )

                st.write(
                    f"Team: {objective['team_name']}"
                )

                st.write(
                    f"Owner: {objective['owner']}"
                )

                st.write(
                    f"Target date: "
                    f"{objective['target_date']}"
                )

                if objective["description"]:
                    st.write(
                        objective["description"]
                    )

                if objective["next_objective"]:

                    st.markdown(
                        f"**Next objective:** "
                        f"{objective['next_objective']}"
                    )

            with right:

                st.metric(
                    "Achievement",
                    f"{objective['progress']}%"
                )

                st.progress(
                    objective["progress"] / 100
                )

                if objective["status"] == "Completed":

                    st.success(
                        "Completed"
                    )

                elif objective["status"] == "At Risk":

                    st.warning(
                        "At Risk"
                    )

                elif objective["status"] == "Blocked":

                    st.error(
                        "Blocked"
                    )

                elif objective["status"] == "In Progress":

                    st.info(
                        "In Progress"
                    )

                else:

                    st.write(
                        "Not Started"
                    )


# =========================================================
# OBJECTIVES
# =========================================================

elif page == "Objectives":

    st.title("Objectives")

    st.markdown(
        "Create, edit and manage team objectives."
    )

    st.divider()

    # =====================================================
    # CREATE OBJECTIVE
    # =====================================================

    st.subheader("Create New Objective")

    with st.form("objective_form"):

        team = st.selectbox(
            "Team",
            ["Team A", "Team B"]
        )

        objective = st.text_input(
            "Objective",
            placeholder="Enter the objective"
        )

        description = st.text_area(
            "Description",
            placeholder="Describe what needs to be achieved"
        )

        owner = st.text_input(
            "Owner",
            placeholder="Person responsible"
        )

        target_date = st.date_input(
            "Target Date",
            date.today()
        )

        next_objective = st.text_input(
            "Next Objective",
            placeholder="What should happen after this objective?"
        )

        submitted = st.form_submit_button(
            "Create Objective"
        )

        if submitted:

            if not objective.strip():

                st.error(
                    "Objective is required."
                )

            else:

                create_objective(
                    team,
                    objective,
                    description,
                    owner,
                    target_date,
                    next_objective
                )

                st.success(
                    "Objective created successfully."
                )

                st.rerun()

    st.divider()

    # =====================================================
    # EXISTING OBJECTIVES
    # =====================================================

    st.subheader("Existing Objectives")

    objectives = get_objectives(
        team_filter
    )

    if not objectives:

        st.info(
            "No objectives found."
        )

    for obj in objectives:

        with st.container(border=True):

            st.markdown(
                f"### {obj['objective']}"
            )

            st.write(
                f"Team: {obj['team_name']}"
            )

            st.write(
                f"Owner: {obj['owner'] or 'Not assigned'}"
            )

            st.write(
                f"Target Date: {obj['target_date']}"
            )

            st.progress(
                obj["progress"] / 100
            )

            st.write(
                f"Achievement: {obj['progress']}%"
            )

            st.write(
                f"Status: {obj['status']}"
            )

            if obj["description"]:

                st.write(
                    obj["description"]
                )

            if obj["next_objective"]:

                st.markdown(
                    f"**Next Objective:** "
                    f"{obj['next_objective']}"
                )

            st.divider()

            # =================================================
            # EDIT
            # =================================================

            with st.expander(
                "Edit Objective"
            ):

                edit_team = st.selectbox(
                    "Team",
                    ["Team A", "Team B"],
                    index=(
                        0
                        if obj["team_name"] == "Team A"
                        else 1
                    ),
                    key=f"edit_team_{obj['id']}"
                )

                edited_objective_name = st.text_input(
                    "Objective",
                 value=obj["objective"],
                 key=f"edit_objective_{obj['id']}"
                )

                edit_description = st.text_area(
                    "Description",
                    value=obj["description"] or "",
                    key=f"edit_description_{obj['id']}"
                )

                edit_owner = st.text_input(
                    "Owner",
                    value=obj["owner"] or "",
                    key=f"edit_owner_{obj['id']}"
                )

                existing_date = obj["target_date"]

                if existing_date is None:
                    existing_date = date.today()

                edit_target_date = st.date_input(
                    "Target Date",
                    value=existing_date,
                    key=f"edit_date_{obj['id']}"
                )

                edit_progress = st.slider(
                    "Achievement %",
                    0,
                    100,
                    int(obj["progress"]),
                    key=f"edit_progress_{obj['id']}"
                )

                statuses = [
                    "Not Started",
                    "In Progress",
                    "At Risk",
                    "Blocked",
                    "Completed"
                ]

                current_status = obj["status"]

                if current_status not in statuses:
                    current_status = "Not Started"

                edit_status = st.selectbox(
                    "Status",
                    statuses,
                    index=statuses.index(
                        current_status
                    ),
                    key=f"edit_status_{obj['id']}"
                )

                edit_next_objective = st.text_input(
                    "Next Objective",
                    value=obj["next_objective"] or "",
                    key=f"edit_next_{obj['id']}"
                )

                if st.button(
                    "Save Changes",
                    key=f"edit_save_{obj['id']}"
                ):

                    edit_objective(
                        obj["id"],
                        edit_team,
                        edited_objective_name,
                        edit_description,
                        edit_owner,
                        edit_target_date,
                        edit_progress,
                        edit_status,
                        edit_next_objective
                    )

                    st.success(
                        "Objective updated successfully."
                    )

                    st.rerun()

            # =================================================
            # DELETE
            # =================================================

            with st.expander(
                "Delete Objective"
            ):

                st.warning(
                    "Deleting this objective will permanently "
                    "remove it and its progress history."
                )

                confirm_delete = st.checkbox(
                    "I understand that this cannot be undone.",
                    key=f"confirm_delete_{obj['id']}"
                )

                if st.button(
                    "Delete Objective",
                    key=f"delete_{obj['id']}"
                ):

                    if not confirm_delete:

                        st.error(
                            "Please confirm the deletion first."
                        )

                    else:

                        delete_objective(
                            obj["id"]
                        )

                        st.success(
                            "Objective deleted."
                        )

                        st.rerun()

# =========================================================
# MEETING NOTES
# =========================================================

elif page == "Meeting Notes":

    st.title("Meeting Notes")

    with st.form("meeting_form"):

        team = st.selectbox(
            "Team",
            [
                "Team A",
                "Team B"
            ]
        )

        meeting_title = st.text_input(
            "Meeting Title"
        )

        meeting_date = st.date_input(
            "Meeting Date",
            date.today()
        )

        attendees = st.text_input(
            "Attendees"
        )

        notes = st.text_area(
            "What Was Discussed?",
            height=220
        )

        decisions = st.text_area(
            "Decisions Made",
            height=150
        )

        next_steps = st.text_area(
            "Next Steps",
            height=150
        )

        save = st.form_submit_button(
            "Save Meeting"
        )

        if save:

            if not meeting_title:

                st.error(
                    "Meeting title is required."
                )

            elif not notes:

                st.error(
                    "Meeting notes are required."
                )

            else:

                create_meeting(
                    team,
                    meeting_date,
                    meeting_title,
                    attendees,
                    notes,
                    decisions,
                    next_steps
                )

                st.success(
                    "Meeting saved."
                )

    st.divider()

    st.subheader(
        "Meeting History"
    )

    meetings = get_meetings(
        team_filter
    )

    for meeting in meetings:

        with st.expander(
            f"{meeting['meeting_date']} | "
            f"{meeting['team_name']} | "
            f"{meeting['meeting_title']}"
        ):

            st.write(
                f"Attendees: {meeting['attendees']}"
            )

            st.markdown(
                "#### Discussion"
            )

            st.write(
                meeting["notes"]
            )

            st.markdown(
                "#### Decisions"
            )

            st.write(
                meeting["decisions"]
            )

            st.markdown(
                "#### Next Steps"
            )

            st.write(
                meeting["next_steps"]
            )


# =========================================================
# PROGRESS UPDATES
# =========================================================

elif page == "Progress Updates":

    st.title("Progress Updates")

    objectives = get_objectives(
        team_filter
    )

    if not objectives:

        st.info(
            "Create an objective first."
        )

    else:

        objective_map = {
            f"{x['team_name']} — "
            f"{x['objective']}":
            x
            for x in objectives
        }

        selected_name = st.selectbox(
            "Select Objective",
            list(objective_map.keys())
        )

        objective = objective_map[
            selected_name
        ]

        st.subheader(
            objective["objective"]
        )

        st.write(
            f"Current achievement: "
            f"**{objective['progress']}%**"
        )

        st.progress(
            objective["progress"] / 100
        )

        st.divider()

        update_date = st.date_input(
            "Update Date",
            date.today()
        )

        progress = st.slider(
            "New Achievement %",
            0,
            100,
            int(objective["progress"])
        )

        update_text = st.text_area(
            "Progress Update",
            height=180,
            placeholder=(
                "Describe what has been achieved "
                "since the previous update."
            )
        )

        blockers = st.text_area(
            "Blockers",
            height=120
        )

        next_step = st.text_area(
            "Next Step",
            height=120
        )

        if st.button(
            "Save Progress Update"
        ):

            if not update_text:

                st.error(
                    "Please enter a progress update."
                )

            else:

                create_progress_update(
                    objective["id"],
                    objective["team_name"],
                    update_date,
                    progress,
                    update_text,
                    blockers,
                    next_step
                )

                st.success(
                    "Progress update saved."
                )

        st.divider()

        st.subheader(
            "Progress History"
        )

        history = get_progress_history(
            objective["id"]
        )

        if not history:

            st.info(
                "No progress history yet."
            )

        for item in history:

            with st.container(border=True):

                st.write(
                    f"{item['update_date']} — "
                    f"{item['progress']}%"
                )

                st.write(
                    item["update_text"]
                )

                if item["blockers"]:

                    st.warning(
                        f"Blockers: "
                        f"{item['blockers']}"
                    )

                if item["next_step"]:

                    st.info(
                        f"Next step: "
                        f"{item['next_step']}"
                    )
# =========================================================
# FINAL APPLICATION STYLING
# =========================================================

st.markdown("""
<style>

/* =====================================================
   MAIN PAGE - FORCE DARK TEXT
===================================================== */

section.main {
    background-color: #f3f4f6 !important;
}

section.main * {
    color: #1f2937 !important;
}


/* =====================================================
   HEADINGS
===================================================== */

section.main h1 {
    color: #111827 !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
}

section.main h2 {
    color: #111827 !important;
    font-weight: 700 !important;
}

section.main h3 {
    color: #111827 !important;
    font-weight: 600 !important;
}

section.main h4 {
    color: #111827 !important;
    font-weight: 600 !important;
}


/* =====================================================
   NORMAL TEXT
===================================================== */

section.main p {
    color: #374151 !important;
}

section.main label {
    color: #374151 !important;
}

section.main span {
    color: #374151 !important;
}

section.main div {
    color: #374151 !important;
}


/* =====================================================
   METRICS
===================================================== */

section.main [data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

section.main [data-testid="stMetric"] * {
    color: #111827 !important;
}

section.main [data-testid="stMetricLabel"] {
    color: #6b7280 !important;
}

section.main [data-testid="stMetricValue"] {
    color: #111827 !important;
}


/* =====================================================
   CARDS
===================================================== */

section.main [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
}

section.main [data-testid="stVerticalBlockBorderWrapper"] * {
    color: #1f2937 !important;
}


/* =====================================================
   TEXT INPUTS
===================================================== */

section.main input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #9ca3af !important;
}

section.main textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #9ca3af !important;
}

section.main input::placeholder,
section.main textarea::placeholder {
    color: #6b7280 !important;
}


/* =====================================================
   SELECT BOX
===================================================== */

section.main [data-baseweb="select"] {
    background-color: #ffffff !important;
}

section.main [data-baseweb="select"] * {
    color: #111827 !important;
}


/* =====================================================
   DATE INPUT
===================================================== */

section.main [data-testid="stDateInput"] input {
    background-color: #ffffff !important;
    color: #111827 !important;
}


/* =====================================================
   SLIDERS
===================================================== */

section.main [data-testid="stSlider"] * {
    color: #374151 !important;
}


/* =====================================================
   BUTTONS
===================================================== */

section.main .stButton button {
    background-color: #34373b !important;
    color: #ffffff !important;
    border: 1px solid #34373b !important;
}

section.main .stButton button * {
    color: #ffffff !important;
}

section.main .stButton button:hover {
    background-color: #4b4f54 !important;
}


/* =====================================================
   PROGRESS BAR
===================================================== */

section.main [data-testid="stProgress"] {
    background-color: #d1d5db !important;
}

section.main [data-testid="stProgress"] > div {
    background-color: #d1d5db !important;
}

section.main [data-testid="stProgress"] > div > div {
    background-color: #4b5563 !important;
}


/* =====================================================
   EXPANDERS
===================================================== */

section.main [data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
}

section.main [data-testid="stExpander"] * {
    color: #1f2937 !important;
}


/* =====================================================
   ALERTS
===================================================== */

section.main [data-testid="stAlert"] {
    color: #1f2937 !important;
}

section.main [data-testid="stAlert"] * {
    color: #1f2937 !important;
}


/* =====================================================
   SIDEBAR
   Keep sidebar white text
===================================================== */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #202124 0%,
        #3b3d40 50%,
        #707378 100%
    ) !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}


/* Sidebar select box */

section[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #111318 !important;
    border-radius: 8px !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #ffffff !important;
}


/* =====================================================
   SIDEBAR BUTTONS / RADIO
===================================================== */

section[data-testid="stSidebar"] button {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] label {
    color: #ffffff !important;
}


/* =====================================================
   STREAMLIT HEADER
===================================================== */

header[data-testid="stHeader"] {
    background-color: #f3f4f6 !important;
}


/* =====================================================
   REMOVE STREAMLIT FOOTER
===================================================== */

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)