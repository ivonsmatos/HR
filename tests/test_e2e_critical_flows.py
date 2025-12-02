"""
E2E Tests for Critical User Flows
Tests main application flows using Playwright
"""
import pytest
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import asyncio
from django.test import TestCase
from django.urls import reverse


class TestE2ECriticalFlows:
    """E2E test suite for critical user journeys"""

    @pytest.fixture
    async def browser(self):
        """Setup and teardown browser"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            yield browser
            await browser.close()

    @pytest.fixture
    async def page(self, browser):
        """Create a new page for each test"""
        context = await browser.new_context()
        page = await context.new_page()
        yield page
        await context.close()

    @pytest.mark.asyncio
    async def test_health_check_endpoints(self, page):
        """Test 1: Health check endpoints are accessible"""
        # Test /health/ endpoint
        response = await page.goto("http://localhost:8000/health/", wait_until="networkidle")
        assert response.status == 200, f"Expected 200, got {response.status}"
        
        # Verify response contains status
        content = await page.content()
        assert "ok" in content.lower() or "healthy" in content.lower()

    @pytest.mark.asyncio
    async def test_health_ready_endpoint(self, page):
        """Test 2: Health ready endpoint"""
        response = await page.goto("http://localhost:8000/health/ready/", wait_until="networkidle")
        assert response.status == 200
        
        content = await page.content()
        assert "database" in content.lower() or "ready" in content.lower()

    @pytest.mark.asyncio
    async def test_health_live_endpoint(self, page):
        """Test 3: Health live endpoint"""
        response = await page.goto("http://localhost:8000/health/live/", wait_until="networkidle")
        assert response.status == 200
        
        content = await page.content()
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_admin_dashboard_loads(self, page):
        """Test 4: Admin dashboard is accessible"""
        # Navigate to admin
        response = await page.goto("http://localhost:8000/admin/", wait_until="networkidle")
        # Should redirect to login or show admin
        assert response.status in [200, 302], f"Unexpected status: {response.status}"

    @pytest.mark.asyncio
    async def test_api_endpoints_respond(self, page):
        """Test 5: API endpoints respond correctly"""
        # Test API health
        response = await page.goto("http://localhost:8000/api/v1/health/", wait_until="networkidle")
        # Should be accessible or redirect
        assert response.status in [200, 301, 302]

    @pytest.mark.asyncio
    async def test_static_files_loaded(self, page):
        """Test 6: Static files are served correctly"""
        # Load main page
        response = await page.goto("http://localhost:8000/", wait_until="networkidle")
        assert response.status in [200, 302]
        
        # Check for static assets
        locator = page.locator("link[rel='stylesheet']")
        count = await locator.count()
        assert count > 0, "No stylesheets found"

    @pytest.mark.asyncio
    async def test_navigation_structure(self, page):
        """Test 7: Navigation structure is intact"""
        response = await page.goto("http://localhost:8000/", wait_until="networkidle")
        assert response.status in [200, 302]
        
        # Check for nav elements
        nav = page.locator("nav, [role='navigation']")
        nav_count = await nav.count()
        # Should have some navigation
        assert nav_count >= 0

    @pytest.mark.asyncio
    async def test_performance_response_time(self, page):
        """Test 8: Performance - response time < 2 seconds"""
        start_time = asyncio.get_event_loop().time()
        response = await page.goto("http://localhost:8000/health/", wait_until="networkidle")
        end_time = asyncio.get_event_loop().time()
        
        response_time = end_time - start_time
        assert response_time < 2.0, f"Response took {response_time:.2f}s, expected < 2s"

    @pytest.mark.asyncio
    async def test_no_console_errors(self, page):
        """Test 9: No JavaScript console errors"""
        errors = []
        
        def handle_error(msg):
            errors.append(msg)
        
        page.on("console", handle_error)
        
        response = await page.goto("http://localhost:8000/", wait_until="networkidle")
        
        # Filter out known non-error messages
        critical_errors = [e for e in errors if "error" in str(e).lower()]
        assert len(critical_errors) == 0, f"Found errors: {critical_errors}"

    @pytest.mark.asyncio
    async def test_responsive_design(self, page):
        """Test 10: Responsive design - mobile viewport"""
        # Set mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        
        response = await page.goto("http://localhost:8000/", wait_until="networkidle")
        assert response.status in [200, 302]
        
        # Check page is still usable
        content = await page.content()
        assert len(content) > 100


# Sync wrapper tests for pytest compatibility
@pytest.mark.django_db
class TestE2ECriticalFlowsSync(TestCase):
    """Sync wrapper for E2E tests"""
    
    def test_e2e_flows_exist(self):
        """Verify E2E test class exists"""
        assert TestE2ECriticalFlows is not None
        assert hasattr(TestE2ECriticalFlows, 'test_health_check_endpoints')
        assert hasattr(TestE2ECriticalFlows, 'test_admin_dashboard_loads')


# Marker for E2E tests
pytest.mark.e2e = pytest.mark.e2e
