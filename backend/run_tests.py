#!/usr/bin/env python
"""
Comprehensive Test Runner for BYN Platform
Run all tests with detailed reporting and coverage analysis.
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import argparse
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byn.settings')

import django
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line


class TestRunner:
    """Comprehensive test runner with reporting"""
    
    def __init__(self):
        self.start_time = None
        self.results = {
            'summary': {},
            'detailed': {},
            'coverage': {},
            'performance': {}
        }
    
    def run_tests(self, test_type='all', verbose=True, coverage=False, parallel=False):
        """Run tests based on specified type"""
        
        self.start_time = time.time()
        print(f"\n{'='*60}")
        print(f"BYN Platform Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        if test_type == 'all':
            self.run_all_tests(verbose, coverage, parallel)
        elif test_type == 'unit':
            self.run_unit_tests(verbose, coverage)
        elif test_type == 'integration':
            self.run_integration_tests(verbose, coverage)
        elif test_type == 'performance':
            self.run_performance_tests(verbose)
        elif test_type == 'security':
            self.run_security_tests(verbose)
        else:
            self.run_specific_tests(test_type, verbose, coverage)
        
        self.print_summary()
        self.save_results()
    
    def run_all_tests(self, verbose=True, coverage=False, parallel=False):
        """Run all test categories"""
        print("🧪 Running Complete Test Suite...\n")
        
        test_categories = [
            ('Authentication Tests', 'tests.test_authentication'),
            ('User Profile Tests', 'tests.test_user_profiles'),
            ('Company Tests', 'tests.test_companies'),
            ('Job System Tests', 'tests.test_jobs'),
            ('Feed Tests', 'tests.test_feed'),
            ('Connections Tests', 'tests.test_connections'),
        ]
        
        for category_name, test_module in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 50)
            self.run_test_module(test_module, verbose, coverage)
    
    def run_unit_tests(self, verbose=True, coverage=False):
        """Run unit tests only"""
        print("🔬 Running Unit Tests...\n")
        
        unit_tests = [
            'tests.test_authentication.UserRegistrationTestCase',
            'tests.test_authentication.UserLoginTestCase',
            'tests.test_user_profiles.UserProfileTestCase',
            'tests.test_user_profiles.ExperienceTestCase',
            'tests.test_user_profiles.EducationTestCase',
            'tests.test_user_profiles.SkillsTestCase',
            'tests.test_companies.CompanyTestCase',
            'tests.test_companies.IndustryTestCase',
            'tests.test_jobs.JobTestCase',
        ]
        
        for test_class in unit_tests:
            self.run_test_module(test_class, verbose, coverage)
    
    def run_integration_tests(self, verbose=True, coverage=False):
        """Run integration tests"""
        print("🔗 Running Integration Tests...\n")
        
        integration_tests = [
            'tests.test_authentication.SecurityTestCase',
            'tests.test_user_profiles.UserSearchTestCase',
            'tests.test_companies.CompanySearchTestCase',
            'tests.test_jobs.JobSearchAndFilterTestCase',
        ]
        
        for test_class in integration_tests:
            self.run_test_module(test_class, verbose, coverage)
    
    def run_performance_tests(self, verbose=True):
        """Run performance tests"""
        print("⚡ Performance tests are not implemented yet...\n")
        print("✅ SKIPPED - Performance tests module was removed")
    
    def run_security_tests(self, verbose=True):
        """Run security-focused tests"""
        print("🔒 Running Security Tests...\n")
        
        security_tests = [
            'tests.test_authentication.SecurityTestCase',
            'tests.test_authentication.TokenSecurityTestCase',
        ]
        
        for test_class in security_tests:
            self.run_test_module(test_class, verbose, False)
    
    def run_specific_tests(self, test_path, verbose=True, coverage=False):
        """Run specific test module or class"""
        print(f"🎯 Running Specific Tests: {test_path}\n")
        self.run_test_module(test_path, verbose, coverage)
    
    def run_test_module(self, test_path, verbose=True, coverage=False):
        """Execute a specific test module"""
        try:
            # Build Django test command with custom test settings
            cmd = ['python', 'manage.py', 'test', test_path, '--settings=byn.test_settings']
            
            if verbose:
                cmd.append('-v')
                cmd.append('2')
            
            if coverage:
                # Add coverage if requested
                cmd = ['coverage', 'run', '--append', '--source=.'] + cmd[1:]
            
            # Run the test
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Parse results
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Store results
            self.results['detailed'][test_path] = {
                'success': success,
                'duration': duration,
                'output': output
            }
            
            # Print results
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {test_path} ({duration:.2f}s)")
            
            if not success and verbose:
                print(f"Error Output:\n{result.stderr}")
                
        except Exception as e:
            print(f"❌ ERROR running {test_path}: {str(e)}")
            self.results['detailed'][test_path] = {
                'success': False,
                'duration': 0,
                'output': str(e)
            }
    
    def run_coverage_analysis(self):
        """Generate coverage report"""
        try:
            print("\n📊 Generating Coverage Report...\n")
            
            # Generate coverage report
            result = subprocess.run(['coverage', 'report'], capture_output=True, text=True)
            coverage_output = result.stdout
            
            # Generate HTML report
            subprocess.run(['coverage', 'html'], capture_output=True)
            
            # Parse coverage data
            lines = coverage_output.split('\n')
            for line in lines:
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        self.results['coverage']['total'] = parts[-1]
            
            print("Coverage Report:")
            print(coverage_output)
            print("\n📁 HTML coverage report generated in htmlcov/")
            
        except Exception as e:
            print(f"❌ Error generating coverage report: {str(e)}")
    
    def run_linting(self):
        """Run code quality checks"""
        print("\n🧹 Running Code Quality Checks...\n")
        
        # Run flake8
        try:
            result = subprocess.run(['flake8', '.'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Flake8: No issues found")
            else:
                print(f"⚠️  Flake8 issues found:\n{result.stdout}")
        except:
            print("❌ Flake8 not installed or failed to run")
        
        # Run pylint on key modules
        key_modules = ['accounts', 'companies', 'jobs']
        for module in key_modules:
            try:
                result = subprocess.run(['pylint', module], capture_output=True, text=True)
                score_line = [line for line in result.stdout.split('\n') if 'Your code has been rated' in line]
                if score_line:
                    print(f"📊 Pylint {module}: {score_line[0].split('Your code has been rated at ')[1]}")
            except:
                print(f"❌ Pylint failed for {module}")
    
    def print_summary(self):
        """Print test summary"""
        total_time = time.time() - self.start_time
        
        passed = sum(1 for result in self.results['detailed'].values() if result['success'])
        failed = len(self.results['detailed']) - passed
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests Run: {len(self.results['detailed'])}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        if 'total' in self.results.get('coverage', {}):
            print(f"📊 Code Coverage: {self.results['coverage']['total']}")
        
        print(f"{'='*60}\n")
        
        # Store summary
        self.results['summary'] = {
            'total_tests': len(self.results['detailed']),
            'passed': passed,
            'failed': failed,
            'total_time': total_time,
            'success_rate': passed / len(self.results['detailed']) if self.results['detailed'] else 0
        }
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"📁 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
    
    def generate_html_report(self):
        """Generate HTML test report"""
        try:
            html_content = self.create_html_report()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_report_{timestamp}.html"
            
            with open(filename, 'w') as f:
                f.write(html_content)
            
            print(f"📊 HTML report generated: {filename}")
            
        except Exception as e:
            print(f"❌ Error generating HTML report: {str(e)}")
    
    def create_html_report(self):
        """Create HTML test report"""
        summary = self.results['summary']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>BYN Platform Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .test-results {{ margin-top: 20px; }}
                .test-item {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BYN Platform Test Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <p>{summary.get('total_tests', 0)}</p>
                </div>
                <div class="metric">
                    <h3 class="passed">Passed</h3>
                    <p>{summary.get('passed', 0)}</p>
                </div>
                <div class="metric">
                    <h3 class="failed">Failed</h3>
                    <p>{summary.get('failed', 0)}</p>
                </div>
                <div class="metric">
                    <h3>Success Rate</h3>
                    <p>{summary.get('success_rate', 0):.1%}</p>
                </div>
                <div class="metric">
                    <h3>Duration</h3>
                    <p>{summary.get('total_time', 0):.2f}s</p>
                </div>
            </div>
            
            <div class="test-results">
                <h2>Detailed Results</h2>
        """
        
        for test_name, result in self.results['detailed'].items():
            status_class = "passed" if result['success'] else "failed"
            status_text = "PASSED" if result['success'] else "FAILED"
            
            html += f"""
                <div class="test-item">
                    <h4 class="{status_class}">{test_name} - {status_text}</h4>
                    <p>Duration: {result['duration']:.2f}s</p>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(description='BYN Platform Test Runner')
    parser.add_argument('test_type', nargs='?', default='all',
                       help='Type of tests to run: all, unit, integration, performance, security, or specific test path')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Run with coverage analysis')
    parser.add_argument('-p', '--parallel', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--lint', action='store_true',
                       help='Run code quality checks')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Run linting if requested
    if args.lint:
        runner.run_linting()
    
    # Run tests
    runner.run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )
    
    # Generate coverage report if requested
    if args.coverage:
        runner.run_coverage_analysis()
    
    # Generate HTML report if requested
    if args.html:
        runner.generate_html_report()


if __name__ == '__main__':
    main() 