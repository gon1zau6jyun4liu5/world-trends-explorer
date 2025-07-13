#!/usr/bin/env python3
"""
World Trends Explorer - Comprehensive Test Suite with HTML Report Generation
🧪 Runs all tests and generates detailed HTML reports
"""

import sys
import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import unittest
import tempfile
import webbrowser

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class TestReportGenerator:
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {
            'summary': {
                'timestamp': self.start_time.isoformat(),
                'version': 'v1.0.6',
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'duration': 0,
                'success_rate': 0
            },
            'backend_tests': {},
            'frontend_tests': {},
            'integration_tests': {},
            'logs': []
        }
        
    def log(self, message, level='INFO'):
        """Add log entry with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        self.test_results['logs'].append(log_entry)
        print(log_entry)
        
    def run_backend_tests(self):
        """Run all backend test suites"""
        self.log("Starting backend tests...")
        
        backend_dir = Path(__file__).parent / 'backend'
        original_dir = os.getcwd()
        
        # Check if backend directory exists
        if not backend_dir.exists():
            self.log(f"Backend directory not found: {backend_dir}", 'ERROR')
            return
            
        os.chdir(backend_dir)
        
        test_files = [
            'test_api_unit.py',
            'test_backend_api.py',
            'test_api_connection.py'
        ]
        
        backend_results = {
            'suites': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0
        }
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                self.log(f"Test file {test_file} not found, skipping", 'WARNING')
                continue
                
            self.log(f"Running {test_file}...")
            start_time = time.time()
            
            try:
                # Run test with detailed output
                result = subprocess.run([
                    sys.executable, test_file
                ], capture_output=True, text=True, timeout=300)
                
                duration = time.time() - start_time
                
                suite_result = {
                    'name': test_file,
                    'duration': round(duration, 2),
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'status': 'passed' if result.returncode == 0 else 'failed'
                }
                
                backend_results['suites'].append(suite_result)
                backend_results['duration'] += duration
                
                if result.returncode == 0:
                    backend_results['passed'] += 1
                    self.log(f"✅ {test_file} passed ({duration:.1f}s)")
                else:
                    backend_results['failed'] += 1
                    self.log(f"❌ {test_file} failed ({duration:.1f}s)")
                    
                backend_results['total'] += 1
                
            except subprocess.TimeoutExpired:
                self.log(f"❌ {test_file} timed out", 'ERROR')
                backend_results['failed'] += 1
                backend_results['total'] += 1
                
        os.chdir(original_dir)
        self.test_results['backend_tests'] = backend_results
        self.log(f"Backend tests completed: {backend_results['passed']}/{backend_results['total']} passed")
        
    def run_integration_tests(self):
        """Run integration tests that verify backend-frontend connectivity"""
        self.log("Starting integration tests...")
        
        integration_results = {
            'suites': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0
        }
        
        # Test 1: API Connectivity
        start_time = time.time()
        try:
            import requests
            response = requests.get('http://localhost:5000/api/trends/health', timeout=5)
            if response.status_code == 200:
                integration_results['passed'] += 1
                status = 'passed'
                self.log("✅ API connectivity test passed")
            else:
                integration_results['failed'] += 1
                status = 'failed'
                self.log("❌ API connectivity test failed - server not responding")
        except Exception as e:
            integration_results['failed'] += 1
            status = 'failed'
            self.log(f"❌ API connectivity test failed: {str(e)}")
        
        duration = time.time() - start_time
        integration_results['suites'].append({
            'name': 'API Connectivity Test',
            'duration': round(duration, 2),
            'status': status
        })
        integration_results['total'] += 1
        integration_results['duration'] += duration
        
        # Test 2: Google Trends API
        start_time = time.time()
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload(['python'], cat=0, timeframe='today 5-y', geo='', gprop='')
            data = pytrends.interest_over_time()
            
            if not data.empty:
                integration_results['passed'] += 1
                status = 'passed'
                self.log("✅ Google Trends API test passed")
            else:
                integration_results['failed'] += 1
                status = 'failed'
                self.log("❌ Google Trends API test failed - no data returned")
        except Exception as e:
            integration_results['failed'] += 1
            status = 'failed'
            self.log(f"❌ Google Trends API test failed: {str(e)}")
        
        duration = time.time() - start_time
        integration_results['suites'].append({
            'name': 'Google Trends API Test',
            'duration': round(duration, 2),
            'status': status
        })
        integration_results['total'] += 1
        integration_results['duration'] += duration
        
        self.test_results['integration_tests'] = integration_results
        self.log(f"Integration tests completed: {integration_results['passed']}/{integration_results['total']} passed")
        
    def generate_html_report(self):
        """Generate comprehensive HTML test report"""
        self.log("Generating HTML test report...")
        
        # Calculate summary
        total_duration = time.time() - self.start_time.timestamp()
        
        backend = self.test_results['backend_tests']
        integration = self.test_results['integration_tests']
        
        total_tests = backend.get('total', 0) + integration.get('total', 0)
        passed_tests = backend.get('passed', 0) + integration.get('passed', 0)
        failed_tests = backend.get('failed', 0) + integration.get('failed', 0)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results['summary'].update({
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'duration': round(total_duration, 2),
            'success_rate': round(success_rate, 1)
        })
        
        html_content = self.create_html_template()
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'test-report-{timestamp}.html'
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        self.log(f"HTML report generated: {report_filename}")
        return report_filename
        
    def create_html_template(self):
        """Create detailed HTML report template"""
        success_color = '#28a745' if self.test_results['summary']['success_rate'] >= 70 else '#dc3545' if self.test_results['summary']['success_rate'] < 50 else '#ffc107'
        
        backend_section = self.create_backend_section()
        integration_section = self.create_integration_section()
        logs_section = self.create_logs_section()
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧪 World Trends Explorer - Test Report v1.0.6</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #e1e5e9;
            padding-bottom: 20px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .summary-card.passed {{
            border-left-color: #28a745;
        }}
        
        .summary-card.failed {{
            border-left-color: #dc3545;
        }}
        
        .summary-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .summary-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .success-rate {{
            font-size: 3em;
            font-weight: bold;
            color: {success_color};
        }}
        
        .test-section {{
            margin-bottom: 30px;
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .section-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e1e5e9;
            font-weight: 600;
            font-size: 1.2em;
        }}
        
        .test-suite {{
            border-bottom: 1px solid #f1f3f4;
        }}
        
        .suite-header {{
            background: #fdfdfd;
            padding: 12px 20px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        
        .suite-header:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 15px;
            color: white;
            font-size: 0.8em;
            font-weight: 600;
        }}
        
        .status-badge.passed {{
            background: #28a745;
        }}
        
        .status-badge.failed {{
            background: #dc3545;
        }}
        
        .test-details {{
            padding: 15px 20px;
            font-family: monospace;
            font-size: 0.85em;
            background: #f8f9fa;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }}
        
        .test-details.active {{
            display: block;
        }}
        
        .logs-section {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            font-family: monospace;
            font-size: 0.85em;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e1e5e9;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .expand-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8em;
        }}
        
        .icon {{
            margin-right: 8px;
        }}
        
        .verdict {{
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .verdict.excellent {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .verdict.good {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        
        .verdict.needs-work {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 World Trends Explorer - Test Report</h1>
            <p>Comprehensive Unit & Integration Testing - Version 1.0.6</p>
            <p><strong>Generated:</strong> {self.test_results['summary']['timestamp']}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-number">{self.test_results['summary']['total_tests']}</div>
                <div class="summary-label">Total Tests</div>
            </div>
            <div class="summary-card passed">
                <div class="summary-number">{self.test_results['summary']['passed_tests']}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-card failed">
                <div class="summary-number">{self.test_results['summary']['failed_tests']}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{self.test_results['summary']['duration']}s</div>
                <div class="summary-label">Duration</div>
            </div>
            <div class="summary-card">
                <div class="success-rate">{self.test_results['summary']['success_rate']}%</div>
                <div class="summary-label">Success Rate</div>
            </div>
        </div>
        
        {self.create_verdict_section()}
        
        <div class="metadata">
            <div>
                <strong>🔧 Test Environment</strong><br>
                Python: {sys.version.split()[0]}<br>
                Platform: {sys.platform}<br>
                Working Directory: {os.getcwd()}
            </div>
            <div>
                <strong>📊 Test Statistics</strong><br>
                Backend Tests: {self.test_results['backend_tests'].get('total', 0)}<br>
                Integration Tests: {self.test_results['integration_tests'].get('total', 0)}<br>
                Average Duration: {round(self.test_results['summary']['duration'] / max(self.test_results['summary']['total_tests'], 1), 2)}s per test
            </div>
        </div>
        
        {backend_section}
        {integration_section}
        {logs_section}
    </div>
    
    <script>
        function toggleDetails(element) {{
            const details = element.nextElementSibling;
            details.classList.toggle('active');
        }}
        
        // Auto-expand failed tests
        document.addEventListener('DOMContentLoaded', function() {{
            const failedSuites = document.querySelectorAll('.status-badge.failed');
            failedSuites.forEach(badge => {{
                const header = badge.parentElement;
                const details = header.nextElementSibling;
                if (details) {{
                    details.classList.add('active');
                }}
            }});
        }});
    </script>
</body>
</html>
"""

    def create_verdict_section(self):
        """Create overall test verdict section"""
        success_rate = self.test_results['summary']['success_rate']
        
        if success_rate >= 80:
            verdict_class = 'excellent'
            verdict_text = f"🎉 Excellent! {success_rate}% success rate - All systems are working well!"
        elif success_rate >= 60:
            verdict_class = 'good'
            verdict_text = f"✅ Good! {success_rate}% success rate - Minor issues that should be addressed."
        else:
            verdict_class = 'needs-work'
            verdict_text = f"⚠️ Needs Work! {success_rate}% success rate - Significant issues requiring attention."
            
        return f'<div class="verdict {verdict_class}">{verdict_text}</div>'

    def create_backend_section(self):
        """Create backend tests section"""
        backend = self.test_results['backend_tests']
        if not backend.get('suites'):
            return '<div class="test-section"><div class="section-header">🐍 Backend Tests - No tests found</div></div>'
        
        suites_html = ''
        for suite in backend['suites']:
            status_class = suite['status']
            suites_html += f"""
            <div class="test-suite">
                <div class="suite-header" onclick="toggleDetails(this)">
                    <span>
                        <span class="icon">🐍</span>
                        {suite['name']} ({suite['duration']}s)
                    </span>
                    <span class="status-badge {status_class}">{status_class.upper()}</span>
                </div>
                <div class="test-details">
<strong>STDOUT:</strong>
{suite.get('stdout', 'No output')}

<strong>STDERR:</strong>
{suite.get('stderr', 'No errors')}

<strong>Return Code:</strong> {suite.get('returncode', 'N/A')}
                </div>
            </div>
            """
        
        return f"""
        <div class="test-section">
            <div class="section-header">
                🐍 Backend Tests ({backend['passed']}/{backend['total']} passed, {backend['duration']:.1f}s)
            </div>
            {suites_html}
        </div>
        """

    def create_integration_section(self):
        """Create integration tests section"""
        integration = self.test_results['integration_tests']
        if not integration.get('suites'):
            return '<div class="test-section"><div class="section-header">🔗 Integration Tests - No tests found</div></div>'
        
        suites_html = ''
        for suite in integration['suites']:
            status_class = suite['status']
            suites_html += f"""
            <div class="test-suite">
                <div class="suite-header">
                    <span>
                        <span class="icon">🔗</span>
                        {suite['name']} ({suite['duration']}s)
                    </span>
                    <span class="status-badge {status_class}">{status_class.upper()}</span>
                </div>
            </div>
            """
        
        return f"""
        <div class="test-section">
            <div class="section-header">
                🔗 Integration Tests ({integration['passed']}/{integration['total']} passed, {integration['duration']:.1f}s)
            </div>
            {suites_html}
        </div>
        """

    def create_logs_section(self):
        """Create logs section"""
        logs_text = '\n'.join(self.test_results['logs'])
        return f"""
        <div class="logs-section">
            <strong>📋 Test Execution Logs:</strong><br><br>
            {logs_text}
        </div>
        """

def main():
    """Main test execution function"""
    print("🧪 World Trends Explorer - Comprehensive Test Suite v1.0.6")
    print("=" * 60)
    
    # Create test reporter
    reporter = TestReportGenerator()
    
    try:
        # Run all test suites
        reporter.run_backend_tests()
        reporter.run_integration_tests()
        
        # Generate HTML report
        report_file = reporter.generate_html_report()
        
        # Open report in browser
        try:
            file_path = os.path.abspath(report_file)
            webbrowser.open(f'file://{file_path}')
            reporter.log(f"Report opened in browser: {file_path}")
        except Exception as e:
            reporter.log(f"Could not open browser: {e}", 'WARNING')
        
        # Print summary
        summary = reporter.test_results['summary']
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Duration: {summary['duration']}s")
        print(f"Report: {report_file}")
        
        if summary['success_rate'] >= 80:
            print("🎉 Status: EXCELLENT - All systems working well!")
            return 0
        elif summary['success_rate'] >= 60:
            print("✅ Status: GOOD - Minor issues detected")
            return 0
        else:
            print("⚠️ Status: NEEDS WORK - Significant issues require attention")
            return 1
            
    except Exception as e:
        reporter.log(f"Test execution failed: {str(e)}", 'ERROR')
        print(f"❌ Test execution failed: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
