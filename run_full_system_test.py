#!/usr/bin/env python3
"""
Comprehensive system test for Media Bias Detection System
"""

import sys
import os
import subprocess
import time
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

def run_command(command, cwd=None, timeout=30):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            timeout=timeout,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_python_dependencies():
    """Test Python dependencies"""
    print("Testing Python dependencies...")
    
    required_modules = [
        ('pymongo', 'pymongo'),
        ('flask', 'flask'), 
        ('requests', 'requests'), 
        ('beautifulsoup4', 'bs4'), 
        ('scikit-learn', 'sklearn'), 
        ('nltk', 'nltk'), 
        ('pytest', 'pytest')
    ]
    
    missing = []
    for display_name, import_name in required_modules:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(display_name)
    
    if missing:
        print(f"✗ Missing Python modules: {', '.join(missing)}")
        return False
    else:
        print("✓ All Python dependencies available")
        return True

def test_component_functionality():
    """Test core component functionality"""
    print("Testing core components...")
    
    success, stdout, stderr = run_command("python test_system_components.py")
    
    if success and "All component tests passed!" in stdout:
        print("✓ All core components working")
        return True
    else:
        print(f"✗ Component tests failed: {stderr}")
        return False

def test_unit_tests():
    """Run unit tests"""
    print("Running unit tests...")
    
    # Run specific unit tests that don't require server
    test_commands = [
        "python -m pytest tests/test_bias_analysis.py::TestLanguageDetector -v",
        "python -m pytest tests/test_bias_analysis.py::TestSentimentAnalyzer::test_positive_sentiment_english -v",
        "python -m pytest tests/test_bias_analysis.py::TestBiasAnalyzer::test_complete_bias_analysis -v",
        "python -m pytest tests/test_scrapers.py::TestBaseScraper::test_user_agent_rotation -v"
    ]
    
    all_passed = True
    for cmd in test_commands:
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"✗ Test failed: {cmd}")
            all_passed = False
    
    if all_passed:
        print("✓ Unit tests passed")
        return True
    else:
        print("✗ Some unit tests failed")
        return False

def test_frontend_build():
    """Test frontend build"""
    print("Testing frontend build...")
    
    # Check if Node.js is available
    success, stdout, stderr = run_command("node --version")
    if not success:
        print("✗ Node.js not available")
        return False
    
    # Check if npm dependencies are installed
    if not os.path.exists("frontend/node_modules"):
        print("Installing npm dependencies...")
        success, stdout, stderr = run_command("npm install", cwd="frontend", timeout=120)
        if not success:
            print(f"✗ npm install failed: {stderr}")
            return False
    
    # Build frontend
    success, stdout, stderr = run_command("npm run build", cwd="frontend", timeout=60)
    if success:
        print("✓ Frontend builds successfully")
        return True
    else:
        print(f"✗ Frontend build failed: {stderr}")
        return False

def test_api_server():
    """Test API server functionality"""
    print("Testing API server...")
    
    # Start API server in background
    print("Starting API server...")
    
    # Set environment variable and start server
    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    
    try:
        server_process = subprocess.Popen(
            [sys.executable, "api/app.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✓ API server health check passed")
                
                # Test bias analysis endpoint
                test_data = {
                    "text": "This is an excellent government policy.",
                    "language": "english"
                }
                
                response = requests.post(
                    "http://localhost:5000/api/bias/analyze-text",
                    json=test_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'overall_bias_score' in result:
                        print("✓ Bias analysis endpoint working")
                        return True
                    else:
                        print("✗ Bias analysis response missing required fields")
                        return False
                else:
                    print(f"✗ Bias analysis endpoint failed: {response.status_code}")
                    return False
            else:
                print(f"✗ API server health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("✗ Could not connect to API server")
            return False
            
    except Exception as e:
        print(f"✗ Failed to start API server: {e}")
        return False
        
    finally:
        # Clean up server process
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            try:
                server_process.kill()
            except:
                pass

def test_docker_configuration():
    """Test Docker configuration"""
    print("Testing Docker configuration...")
    
    # Check if Docker files exist
    docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.dev.yml"]
    
    missing_files = []
    for file in docker_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ Missing Docker files: {', '.join(missing_files)}")
        return False
    
    # Check if docker is available (optional)
    success, stdout, stderr = run_command("docker --version")
    if success:
        print("✓ Docker configuration files present and Docker available")
    else:
        print("✓ Docker configuration files present (Docker not installed)")
    
    return True

def test_scripts():
    """Test utility scripts"""
    print("Testing utility scripts...")
    
    scripts_dir = "scripts"
    if not os.path.exists(scripts_dir):
        print("✗ Scripts directory not found")
        return False
    
    # Check for key scripts
    key_scripts = ["deploy.sh", "backup.sh", "test-system.sh"]
    
    missing_scripts = []
    for script in key_scripts:
        script_path = os.path.join(scripts_dir, script)
        if not os.path.exists(script_path):
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"✗ Missing scripts: {', '.join(missing_scripts)}")
        return False
    else:
        print("✓ All key scripts present")
        return True

def generate_test_report(results):
    """Generate a test report"""
    print("\n" + "=" * 60)
    print("SYSTEM TEST REPORT")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
    
    print()
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed. Please fix issues before deployment.")
        return False

def main():
    """Run comprehensive system tests"""
    print("Media Bias Detection System - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Component Functionality", test_component_functionality),
        ("Unit Tests", test_unit_tests),
        ("Frontend Build", test_frontend_build),
        ("API Server", test_api_server),
        ("Docker Configuration", test_docker_configuration),
        ("Utility Scripts", test_scripts),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Generate report
    success = generate_test_report(results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)