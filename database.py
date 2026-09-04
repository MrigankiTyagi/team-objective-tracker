import os
import dotenv
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
load_dotenv()

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not configured.")

    return psycopg2.connect(database_url)


# =========================================================
# TEAMS
# =========================================================

def get_teams():

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute("""
        SELECT *
        FROM teams
        ORDER BY name
    """)

    teams = cursor.fetchall()

    cursor.close()
    conn.close()

    return teams


# =========================================================
# OBJECTIVES
# =========================================================

def get_objectives(team=None):

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    if team and team != "All Teams":

        cursor.execute("""
            SELECT
                objectives.*,
                teams.name AS team_name
            FROM objectives
            JOIN teams
                ON objectives.team_id = teams.id
            WHERE teams.name = %s
            ORDER BY target_date
        """, (team,))

    else:

        cursor.execute("""
            SELECT
                objectives.*,
                teams.name AS team_name
            FROM objectives
            JOIN teams
                ON objectives.team_id = teams.id
            ORDER BY target_date
        """)

    objectives = cursor.fetchall()

    cursor.close()
    conn.close()

    return objectives


def create_objective(
    team,
    objective,
    description,
    owner,
    target_date,
    next_objective
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM teams
        WHERE name = %s
    """, (team,))

    team_record = cursor.fetchone()

    if not team_record:
        cursor.close()
        conn.close()
        raise Exception("Team not found.")

    team_id = team_record[0]

    cursor.execute("""
        INSERT INTO objectives (
            team_id,
            objective,
            description,
            owner,
            target_date,
            progress,
            status,
            next_objective
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            0,
            'Not Started',
            %s
        )
    """, (
        team_id,
        objective,
        description,
        owner,
        target_date,
        next_objective
    ))

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# EDIT OBJECTIVE
# =========================================================

def edit_objective(
    objective_id,
    team,
    objective,
    description,
    owner,
    target_date,
    progress,
    status,
    next_objective
):

    conn = get_connection()

    cursor = conn.cursor()

    # Find team ID
    cursor.execute("""
        SELECT id
        FROM teams
        WHERE name = %s
    """, (team,))

    team_record = cursor.fetchone()

    if not team_record:
        cursor.close()
        conn.close()
        raise Exception("Team not found.")

    team_id = team_record[0]

    # Update complete objective
    cursor.execute("""
        UPDATE objectives
        SET
            team_id = %s,
            objective = %s,
            description = %s,
            owner = %s,
            target_date = %s,
            progress = %s,
            status = %s,
            next_objective = %s
        WHERE id = %s
    """, (
        team_id,
        objective,
        description,
        owner,
        target_date,
        progress,
        status,
        next_objective,
        objective_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# DELETE OBJECTIVE
# =========================================================

def delete_objective(objective_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM objectives
        WHERE id = %s
    """, (objective_id,))

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# SIMPLE PROGRESS UPDATE
# =========================================================

def update_objective(
    objective_id,
    progress,
    status,
    next_objective
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE objectives
        SET
            progress = %s,
            status = %s,
            next_objective = %s
        WHERE id = %s
    """, (
        progress,
        status,
        next_objective,
        objective_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# MEETINGS
# =========================================================

def create_meeting(
    team,
    meeting_date,
    meeting_title,
    attendees,
    notes,
    decisions,
    next_steps
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM teams
        WHERE name = %s
    """, (team,))

    team_record = cursor.fetchone()

    if not team_record:
        cursor.close()
        conn.close()
        raise Exception("Team not found.")

    team_id = team_record[0]

    cursor.execute("""
        INSERT INTO meetings (
            team_id,
            meeting_date,
            meeting_title,
            attendees,
            notes,
            decisions,
            next_steps
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        team_id,
        meeting_date,
        meeting_title,
        attendees,
        notes,
        decisions,
        next_steps
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_meetings(team=None):

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    if team and team != "All Teams":

        cursor.execute("""
            SELECT
                meetings.*,
                teams.name AS team_name
            FROM meetings
            JOIN teams
                ON meetings.team_id = teams.id
            WHERE teams.name = %s
            ORDER BY meeting_date DESC
        """, (team,))

    else:

        cursor.execute("""
            SELECT
                meetings.*,
                teams.name AS team_name
            FROM meetings
            JOIN teams
                ON meetings.team_id = teams.id
            ORDER BY meeting_date DESC
        """)

    meetings = cursor.fetchall()

    cursor.close()
    conn.close()

    return meetings


# =========================================================
# PROGRESS HISTORY
# =========================================================

def create_progress_update(
    objective_id,
    team,
    update_date,
    progress,
    update_text,
    blockers,
    next_step
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM teams
        WHERE name = %s
    """, (team,))

    team_record = cursor.fetchone()

    if not team_record:
        cursor.close()
        conn.close()
        raise Exception("Team not found.")

    team_id = team_record[0]

    cursor.execute("""
        INSERT INTO progress_updates (
            objective_id,
            team_id,
            update_date,
            progress,
            update_text,
            blockers,
            next_step
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        objective_id,
        team_id,
        update_date,
        progress,
        update_text,
        blockers,
        next_step
    ))

    if progress == 100:
        status = "Completed"

    elif blockers:
        status = "At Risk"

    elif progress > 0:
        status = "In Progress"

    else:
        status = "Not Started"

    cursor.execute("""
        UPDATE objectives
        SET
            progress = %s,
            status = %s,
            next_objective =
                CASE
                    WHEN %s <> ''
                    THEN %s
                    ELSE next_objective
                END
        WHERE id = %s
    """, (
        progress,
        status,
        next_step,
        next_step,
        objective_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_progress_history(objective_id):

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute("""
        SELECT *
        FROM progress_updates
        WHERE objective_id = %s
        ORDER BY update_date DESC, id DESC
    """, (objective_id,))

    updates = cursor.fetchall()

    cursor.close()
    conn.close()

    return updates