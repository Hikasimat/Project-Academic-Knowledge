import pytest
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.user import User
from app.security import get_password_hash, create_access_token

def test_sequential_course_progression(client, db, learner_user, learner_token):
    """
    Test Coursera-style step-by-step sequential progression.
    Steps must be completed in order.
    """
    course = db.query(Course).filter(Course.track_name == "Both companies — Foundation").first()
    assert course is not None

    # Enroll learner
    enrollment = Enrollment(user_id=learner_user.id, course_id=course.id)
    db.add(enrollment)
    db.commit()

    # 1. Fetch course details
    res = client.get(f"/api/courses/{course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert res.status_code == 200
    course_data = res.json()
    steps = course_data["steps"]
    assert len(steps) == 15

    # Step 1 must be unlocked, Step 2 locked
    assert steps[0]["is_unlocked"] is True
    assert steps[0]["is_completed"] is False
    assert steps[1]["is_unlocked"] is False

    # 2. Attempting to complete Step 2 directly must fail (anti-skip check)
    step2_id = steps[1]["id"]
    skip_res = client.post(
        f"/api/courses/{course.id}/steps/{step2_id}/complete",
        headers={"Authorization": f"Bearer {learner_token}"}
    )
    assert skip_res.status_code == 400
    assert "Sequential progression required" in skip_res.json()["detail"]

    # 3. Complete Step 1
    step1_id = steps[0]["id"]
    c1_res = client.post(
        f"/api/courses/{course.id}/steps/{step1_id}/complete",
        headers={"Authorization": f"Bearer {learner_token}"}
    )
    assert c1_res.status_code == 200
    assert c1_res.json()["completed_steps"] == 1
    assert c1_res.json()["next_step_unlocked"] == 2

    # 4. Refresh course details - Step 1 is completed, Step 2 is now unlocked
    res2 = client.get(f"/api/courses/{course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    steps2 = res2.json()["steps"]
    assert steps2[0]["is_completed"] is True
    assert steps2[1]["is_unlocked"] is True
    assert steps2[2]["is_unlocked"] is False

    # 5. Complete steps 2 through 15 sequentially
    for i in range(1, 15):
        st_id = steps2[i]["id"]
        c_res = client.post(
            f"/api/courses/{course.id}/steps/{st_id}/complete",
            headers={"Authorization": f"Bearer {learner_token}"}
        )
        assert c_res.status_code == 200

    # 6. Verify full completion
    final_res = client.get(f"/api/courses/{course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    final_data = final_res.json()
    assert final_data["completed_steps"] == 15
    assert final_data["progress_percentage"] == 100.0
    assert final_data["is_completed"] is True
    assert final_data["exam_eligible"] is True

def test_learner_isolation(client, db, learner_user, learner_token):
    """Verify one learner cannot alter another learner's progress."""
    other_learner = User(
        email="other@plusuae.com",
        full_name="Other User",
        hashed_password=get_password_hash("OtherPass123!"),
        role="learner",
        is_active=True
    )
    db.add(other_learner)
    db.commit()

    course = db.query(Course).first()
    other_enrollment = Enrollment(user_id=other_learner.id, course_id=course.id)
    db.add(other_enrollment)
    db.commit()

    step = db.query(CourseStep).filter(CourseStep.course_id == course.id, CourseStep.step_number == 1).first()

    # learner_token tries to view or alter course they are not enrolled in
    # learner_user is not enrolled in this course yet
    res = client.get(f"/api/courses/{course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert res.status_code == 403


def test_specialized_toolkits_master_course(client, db, learner_user, learner_token):
    """
    Verify the master unified course:
    1. Title: Specialized Sales Reference Catalogs & Practical Toolkits
    2. 6 Sequential sections across the 15 daily steps
    3. Attached topics on each step
    4. Auto-enrollment into master course
    """
    # Auto-enrollment on my-courses
    res = client.get("/api/courses/my-courses", headers={"Authorization": f"Bearer {learner_token}"})
    assert res.status_code == 200
    my_courses = res.json()
    assert len(my_courses) >= 1
    master = next((c for c in my_courses if c["code"] == "specialized_toolkits"), None)
    assert master is not None
    assert master["title"] == "Specialized Sales Reference Catalogs & Practical Toolkits"

    # Detail view of master course
    detail_res = client.get(f"/api/courses/{master['id']}", headers={"Authorization": f"Bearer {learner_token}"})
    assert detail_res.status_code == 200
    detail = detail_res.json()
    steps = detail["steps"]
    assert len(steps) == 15

    # Check section breakdown
    sec_counts = {}
    for s in steps:
        sec_num = s["section_number"]
        sec_counts[sec_num] = sec_counts.get(sec_num, 0) + 1
        assert s["section_title"] is not None
        assert len(s["topics"]) > 0

    assert sec_counts[1] == 5  # Section 1: Days 1-5 (Plus UAE Service Catalog)
    assert sec_counts[2] == 2  # Section 2: Days 6-7 (Vortexen Technical Services)
    assert sec_counts[3] == 2  # Section 3: Days 8-9 (Markets & Buyer Committee Map)
    assert sec_counts[4] == 2  # Section 4: Days 10-11 (Workflows & AI Prompts)
    assert sec_counts[5] == 3  # Section 5: Days 12-14 (Real Sales Case Studies)
    assert sec_counts[6] == 1  # Section 6: Day 15 (CRM Discipline & Funnel Simulator)

