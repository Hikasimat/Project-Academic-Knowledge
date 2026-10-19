import pytest

def test_serve_index_html(client):
    """Verify that root URL serves the integrated index.html."""
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    content = res.text
    # Verify core branding & title
    assert "PLUS UAE" in content
    assert "VORTEXEN" in content
    assert "AI Sales Academy" in content
    # Verify sections
    assert 'id="home"' in content
    assert 'id="plus"' in content
    assert 'id="vortexen"' in content
    assert 'id="targets"' in content
    assert 'id="outreach"' in content
    assert 'id="crosssell"' in content
    assert 'id="events"' in content
    assert 'id="cases"' in content
    assert 'id="automation"' in content
    assert 'id="training"' in content
    assert 'id="certificate"' in content
    assert 'id="admin"' in content
    # Verify modals
    assert 'id="authModal"' in content
    assert 'id="verifyModal"' in content

def test_static_assets_mounted(client):
    """Verify static assets are mounted and accessible."""
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
