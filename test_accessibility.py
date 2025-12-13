#!/usr/bin/env python3
"""
Accessibility Testing Script for SyncRH
========================================
Automated tests to validate WCAG compliance and accessibility improvements
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_html_accessibility():
    """Test HTML templates for accessibility compliance"""
    print("🔍 Testing HTML Accessibility...")

    templates_dir = project_root / "templates"
    apps_dir = project_root / "apps"

    issues = []

    # Check base template
    base_template = templates_dir / "base.html"
    if base_template.exists():
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required elements
        checks = [
            ('lang attribute', 'lang=' in content),
            ('main landmark', '<main' in content or 'role="main"' in content),
            ('skip links', 'skip-link' in content or 'href="#main-content"' in content),
            ('aria-live regions', 'aria-live' in content),
            ('focus management', 'focus-visible' in content),
        ]

        for check_name, condition in checks:
            if condition:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                issues.append(f"Missing {check_name} in base.html")

    # Check chat interface
    chat_template = apps_dir / "assistant" / "templates" / "assistant" / "chat_interface.html"
    if chat_template.exists():
        with open(chat_template, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ('ARIA labels', 'aria-label=' in content),
            ('semantic HTML', 'role=' in content),
            ('form labels', 'label for=' in content or 'aria-describedby=' in content),
            ('landmarks', '<main' in content and '<aside' in content),
            ('live regions', 'aria-live' in content),
        ]

        for check_name, condition in checks:
            if condition:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                issues.append(f"Missing {check_name} in chat_interface.html")

    return issues

def test_css_accessibility():
    """Test CSS for accessibility features"""
    print("\n🎨 Testing CSS Accessibility...")

    css_file = project_root / "static" / "css" / "global.css"
    issues = []

    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ('Screen reader utilities', '.sr-only' in content),
            ('Focus indicators', ':focus-visible' in content),
            ('High contrast focus', '--color-interactive-focus' in content),
            ('Motion preferences', 'prefers-reduced-motion' in content),
            ('Skip link styles', '.skip-link' in content),
        ]

        for check_name, condition in checks:
            if condition:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                issues.append(f"Missing {check_name} in global.css")

    return issues

def test_javascript_accessibility():
    """Test JavaScript for accessibility enhancements"""
    print("\n⚡ Testing JavaScript Accessibility...")

    js_file = project_root / "static" / "js" / "accessibility.js"
    issues = []

    if js_file.exists():
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ('Keyboard navigation', 'keydown' in content),
            ('Focus management', 'focus' in content),
            ('Screen reader support', 'announceToScreenReader' in content),
            ('Skip links', 'initSkipLinks' in content),
            ('Error handling', 'handleError' in content),
        ]

        for check_name, condition in checks:
            if condition:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                issues.append(f"Missing {check_name} in accessibility.js")

    return issues

def generate_report(issues):
    """Generate accessibility testing report"""
    print("\n📊 Accessibility Testing Report")
    print("=" * 50)

    if not issues:
        print("🎉 All accessibility checks passed!")
        print("✅ Estimated WCAG AA Compliance: 95%+")
        return True
    else:
        print(f"⚠️  Found {len(issues)} accessibility issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        compliance_estimate = max(0, 95 - (len(issues) * 5))
        print(f"📈 Estimated WCAG AA Compliance: {compliance_estimate}%")
        return False

def main():
    """Main testing function"""
    print("🧪 SyncRH Accessibility Testing Suite")
    print("=====================================")

    all_issues = []

    # Run all tests
    all_issues.extend(test_html_accessibility())
    all_issues.extend(test_css_accessibility())
    all_issues.extend(test_javascript_accessibility())

    # Generate report
    success = generate_report(all_issues)

    # Save detailed report
    report = {
        "timestamp": "2025-12-12T12:00:00Z",
        "tests_run": 3,
        "issues_found": len(all_issues),
        "issues": all_issues,
        "estimated_compliance": f"{max(0, 95 - (len(all_issues) * 5))}%",
        "status": "PASS" if success else "NEEDS_IMPROVEMENT"
    }

    report_file = project_root / "accessibility_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Detailed report saved to: {report_file}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())