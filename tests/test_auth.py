import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import User, Invitation
from app.security import generate_invitation_token, get_password_hash

def test_no_public_registration(client):
    """Verify that no public self-registration endpoint exists."""
    response = client.post("/api/auth/register", json={"email": "hacker@test.com", "password": "pass"})
    assert response.status_code in [404, 405]

def test_admin_login_success(client, admin_user):
    """Verify valid credentials return JWT token and profile."""
    response = client.post("/api/auth/login", json={
        "email": admin_user.email,
        "password": "AdminPass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"
    assert data["user"]["email"] == admin_user.email

def test_invalid_login_rejected(client, admin_user):
    """Verify invalid credentials return 401."""
    response = client.post("/api/auth/login", json={
        "email": admin_user.email,
        "password": "WrongPassword!"
    })
    assert response.status_code == 401

def test_deactivated_account_blocked(client, db, learner_user):
    """Verify deactivated user cannot log in."""
    learner_user.is_active = False
    db.commit()

    response = client.post("/api/auth/login", json={
        "email": learner_user.email,
        "password": "LearnerPass123!"
    })
    assert response.status_code == 403
    assert "deactivated" in response.json()["detail"].lower()

def test_admin_creates_learner_and_activation(client, admin_token, db):
    """Verify administrator creates learner with track, and learner activates account."""
    # 1. Admin creates learner
    res = client.post("/api/admin/learners", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "email": "ahmed.khalil@example.com",
        "full_name": "Ahmed Khalil",
        "course_track": "Plus UAE — Sales"
    })
    assert res.status_code == 200
    create_data = res.json()
    token = create_data["invitation_token"]
    assert token is not None

    # 2. Validate invitation
    val_res = client.get(f"/api/auth/validate-invite?token={token}")
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is True
    assert val_res.json()["email"] == "ahmed.khalil@example.com"
    assert val_res.json()["course_track"] == "Plus UAE — Sales"

    # 3. Learner activates account
    act_res = client.post("/api/auth/activate", json={
        "token": token,
        "password": "AhmedSecurePass2026!"
    })
    assert act_res.status_code == 200
    assert "access_token" in act_res.json()
    assert act_res.json()["user"]["email"] == "ahmed.khalil@example.com"

    # 4. Token cannot be reused
    reused_res = client.post("/api/auth/activate", json={
        "token": token,
        "password": "AnotherPassword123!"
    })
    assert reused_res.status_code == 400

def test_expired_invitation_rejected(client, db, learner_user):
    """Verify expired invitations are rejected."""
    token = generate_invitation_token()
    inv = Invitation(
        user_id=learner_user.id,
        token=token,
        course_track="Both companies — Foundation",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired 1 hour ago
        is_used=False
    )
    db.add(inv)
    db.commit()

    val_res = client.get(f"/api/auth/validate-invite?token={token}")
    assert val_res.json()["is_valid"] is False

    act_res = client.post("/api/auth/activate", json={
        "token": token,
        "password": "NewSecurePassword123!"
    })
    assert act_res.status_code == 400

def test_learner_cannot_access_admin_endpoints(client, learner_token):
    """Verify role authorization blocks learners from administrative endpoints."""
    res = client.get("/api/admin/learners", headers={"Authorization": f"Bearer {learner_token}"})
    assert res.status_code == 403
