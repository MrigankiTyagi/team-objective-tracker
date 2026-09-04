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
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Arial, Helvetica, sans-serif;
}

/* Main background */

.stApp {
    background-color: #f5f5f5;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #1f1f1f 0%,
            #363636 45%,
            #666666 100%
        );
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Sidebar title */

section[data-testid="stSidebar"] h1 {
    font-size: 24px;
    font-weight: 600;
}

/* Main titles */

h1 {
    color: #222222;
    font-weight: 600;
}

h2 {
    color: #303030;
}

h3 {
    color: #404040;
}

/* Cards */

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #dddddd;
}

/* Buttons */

.stButton > button {
    border-radius: 7px;
    border: 1px solid #555555;
    background-color: #333333;
    color: white;
}

.stButton > button:hover {
    background-color: #555555;
    color: white;
}

/* Inputs */

input, textarea {
    border-radius: 6px !important;
}

/* Progress */

div[data-testid="stProgress"] > div > div {
    background-color: #555555;
}

/* Containers */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: white;
    border-radius: 10px;
}

/* Remove Streamlit menu */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


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

    st.subheader(
        "Create a New Objective"
    )

    with st.form("objective_form"):

        team = st.selectbox(
            "Team",
            [
                "Team A",
                "Team B"
            ]
        )

        objective = st.text_input(
            "Objective"
        )

        description = st.text_area(
            "Description"
        )

        owner = st.text_input(
            "Owner"
        )

        target_date = st.date_input(
            "Target Date",
            date.today()
        )

        next_objective = st.text_input(
            "Next Objective"
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
                    "Objective created."
                )

    st.divider()

    st.subheader(
        "Manage Objectives"
    )

    objectives = get_objectives(
        team_filter
    )

    for objective in objectives:

        with st.container(border=True):

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
                f"Target: {objective['target_date']}"
            )

            progress = st.slider(
                "Achievement %",
                0,
                100,
                int(objective["progress"]),
                key=f"progress_{objective['id']}"
            )

            statuses = [
                "Not Started",
                "In Progress",
                "At Risk",
                "Blocked",
                "Completed"
            ]

            current_status = objective["status"]

            status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(
                    current_status
                ),
                key=f"status_{objective['id']}"
            )

            next_objective = st.text_input(
                "Next Objective",
                value=objective["next_objective"] or "",
                key=f"next_{objective['id']}"
            )

            if st.button(
                "Save Changes",
                key=f"save_{objective['id']}"
            ):

                update_objective(
                    objective["id"],
                    progress,
                    status,
                    next_objective
                )

                st.success(
                    "Objective updated."
                )


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