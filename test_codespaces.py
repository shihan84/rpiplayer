#!/usr/bin/env python3
"""
V-Player Enterprise - Codespaces Testing Suite
Comprehensive testing script for GitHub Codespaces environment
"""

import os
import sys
import time
import requests
import subprocess
import json
from pathlib import Path

class CodespacesTester:
    """Test V-Player Enterprise in Codespaces environment"""
    
    def __init__(self):
        self.base_url = "http://localhost:5005"
        self.test_results = []
        self.app_process = None
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status} {message}")
    
    def check_environment(self):
        """Check Codespaces environment"""
        print("\n🔍 Checking Codespaces Environment...")
        
        # Check if running in Codespaces
        codespace_name = os.environ.get('CODESPACE_NAME')
        if codespace_name:
            self.log_test("Codespaces Detection", "PASS", f"Running in {codespace_name}")
        else:
            self.log_test("Codespaces Detection", "WARN", "Not in Codespaces, but continuing tests")
        
        # Check Python version
        python_version = sys.version
        self.log_test("Python Version", "PASS", python_version.split()[0])
        
        # Check required directories
        required_dirs = ['templates', 'static', 'logs']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                self.log_test(f"Directory {dir_name}", "PASS", "Exists")
            else:
                self.log_test(f"Directory {dir_name}", "FAIL", "Missing")
        
        # Check required files
        required_files = ['app.py', 'config.py', 'requirements.txt']
        for file_name in required_files:
            if Path(file_name).exists():
                self.log_test(f"File {file_name}", "PASS", "Exists")
            else:
                self.log_test(f"File {file_name}", "FAIL", "Missing")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("\n📦 Checking Dependencies...")
        
        try:
            import flask
            self.log_test("Flask", "PASS", flask.__version__)
        except ImportError:
            self.log_test("Flask", "FAIL", "Not installed")
        
        try:
            import flask_socketio
            self.log_test("Flask-SocketIO", "PASS", "Installed")
        except ImportError:
            self.log_test("Flask-SocketIO", "FAIL", "Not installed")
        
        try:
            import psutil
            self.log_test("psutil", "PASS", psutil.__version__)
        except ImportError:
            self.log_test("psutil", "FAIL", "Not installed")
        
        try:
            import requests
            self.log_test("requests", "PASS", requests.__version__)
        except ImportError:
            self.log_test("requests", "FAIL", "Not installed")
    
    def start_application(self):
        """Start V-Player application"""
        print("\n🚀 Starting V-Player Application...")
        
        try:
            # Start the application in background
            self.app_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for application to start
            time.sleep(5)
            
            # Check if process is running
            if self.app_process.poll() is None:
                self.log_test("Application Start", "PASS", "Process running")
            else:
                self.log_test("Application Start", "FAIL", "Process not running")
                return False
            
            # Check if port is accessible
            try:
                response = requests.get(f"{self.base_url}/", timeout=10)
                if response.status_code == 200:
                    self.log_test("Port Accessibility", "PASS", f"Port 5005 accessible")
                    return True
                else:
                    self.log_test("Port Accessibility", "FAIL", f"Status {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                self.log_test("Port Accessibility", "FAIL", str(e))
                return False
                
        except Exception as e:
            self.log_test("Application Start", "FAIL", str(e))
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        endpoints = [
            ("/", "Home Page"),
            ("/api/system/info", "System Info"),
            ("/api/network/status", "Network Status"),
            ("/api/network/interfaces", "Network Interfaces"),
            ("/api/cloudflare/status", "Cloudflare Status"),
            ("/api/outputs/list", "Outputs List"),
            ("/api/channels/list", "Channels List")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"API {description}", "PASS", f"Status {response.status_code}")
                else:
                    self.log_test(f"API {description}", "FAIL", f"Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"API {description}", "FAIL", str(e))
    
    def test_web_interface(self):
        """Test web interface components"""
        print("\n🖥️ Testing Web Interface...")
        
        try:
            # Get main page
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Main Page Load", "PASS", "Page loaded successfully")
                
                # Check for key elements
                content = response.text
                
                elements = [
                    ("V-Player Enterprise", "Title"),
                    ("AWS Elemental MediaLive", "Branding"),
                    ("Network", "Network Tab"),
                    ("Outputs", "Outputs Tab"),
                    ("Cloudflare Zero Trust", "Cloudflare Section"),
                    ("Broadcast", "Broadcast Controls")
                ]
                
                for element, description in elements:
                    if element in content:
                        self.log_test(f"UI Element {description}", "PASS", "Found")
                    else:
                        self.log_test(f"UI Element {description}", "FAIL", "Not found")
            else:
                self.log_test("Main Page Load", "FAIL", f"Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Main Page Load", "FAIL", str(e))
    
    def test_network_features(self):
        """Test network configuration features"""
        print("\n🌐 Testing Network Features...")
        
        # Test network status API
        try:
            response = requests.get(f"{self.base_url}/api/network/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Network Status API", "PASS", "Response received")
                
                # Check for expected fields
                expected_fields = ['interfaces', 'wifi_available', 'ethernet_available']
                for field in expected_fields:
                    if field in data:
                        self.log_test(f"Network Field {field}", "PASS", "Present")
                    else:
                        self.log_test(f"Network Field {field}", "WARN", "Missing")
            else:
                self.log_test("Network Status API", "FAIL", f"Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Network Status API", "FAIL", str(e))
        
        # Test WiFi scan (if available)
        try:
            response = requests.get(f"{self.base_url}/api/network/wifi/scan")
            if response.status_code == 200:
                self.log_test("WiFi Scan API", "PASS", "Scan completed")
            else:
                self.log_test("WiFi Scan API", "WARN", f"Status {response.status_code} (may not be available in Codespaces)")
        except requests.exceptions.RequestException as e:
            self.log_test("WiFi Scan API", "WARN", str(e))
    
    def test_cloudflare_integration(self):
        """Test Cloudflare Zero Trust integration"""
        print("\n🔒 Testing Cloudflare Zero Trust...")
        
        try:
            # Test Cloudflare status
            response = requests.get(f"{self.base_url}/api/cloudflare/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Cloudflare Status API", "PASS", "Response received")
                
                # Check for expected fields
                if 'method' in data and data['method'] == 'dashboard-first-2024':
                    self.log_test("Cloudflare Method", "PASS", "Dashboard-First 2024")
                else:
                    self.log_test("Cloudflare Method", "WARN", "Method not as expected")
            else:
                self.log_test("Cloudflare Status API", "FAIL", f"Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Cloudflare Status API", "FAIL", str(e))
        
        # Test instructions generation
        try:
            response = requests.post(
                f"{self.base_url}/api/cloudflare/instructions",
                json={
                    "hostname": "test.vplayer.com",
                    "local_port": 5005
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Cloudflare Instructions", "PASS", "Generated successfully")
                else:
                    self.log_test("Cloudflare Instructions", "FAIL", "Generation failed")
            else:
                self.log_test("Cloudflare Instructions", "FAIL", f"Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Cloudflare Instructions", "FAIL", str(e))
    
    def test_image_builder(self):
        """Test Raspberry Pi image builder"""
        print("\n🏗️ Testing Image Builder...")
        
        try:
            # Run image builder
            result = subprocess.run(
                [sys.executable, 'build_rpi_image.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_test("Image Builder Script", "PASS", "Executed successfully")
                
                # Check if build directory was created
                build_dir = Path('build/rpi-image')
                if build_dir.exists():
                    self.log_test("Build Directory", "PASS", "Created successfully")
                    
                    # Check for key files
                    key_files = [
                        'opt/vplayer/app.py',
                        'etc/systemd/system/vplayer.service',
                        'usr/local/bin/vplayer-setup.sh'
                    ]
                    
                    for file_path in key_files:
                        full_path = build_dir / file_path
                        if full_path.exists():
                            self.log_test(f"Image File {file_path}", "PASS", "Created")
                        else:
                            self.log_test(f"Image File {file_path}", "FAIL", "Missing")
                else:
                    self.log_test("Build Directory", "FAIL", "Not created")
            else:
                self.log_test("Image Builder Script", "FAIL", f"Return code {result.returncode}")
                
        except subprocess.TimeoutExpired:
            self.log_test("Image Builder Script", "WARN", "Timeout (may be normal)")
        except Exception as e:
            self.log_test("Image Builder Script", "FAIL", str(e))
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warned_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            "timestamp": time.time(),
            "environment": {
                "codespace": os.environ.get('CODESPACE_NAME', 'Unknown'),
                "python_version": sys.version,
                "platform": sys.platform
            },
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warned": warned_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "results": self.test_results
        }
        
        # Save report
        report_file = Path('test_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n🎯 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Warnings: {warned_tests}")
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        print(f"   📄 Report saved to: {report_file.absolute()}")
        
        return report
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        if self.app_process:
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=5)
                self.log_test("Cleanup", "PASS", "Application stopped")
            except subprocess.TimeoutExpired:
                self.app_process.kill()
                self.log_test("Cleanup", "WARN", "Application force killed")
            except Exception as e:
                self.log_test("Cleanup", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting V-Player Enterprise Codespaces Test Suite")
        print("=" * 60)
        
        try:
            # Run all test phases
            self.check_environment()
            self.check_dependencies()
            
            if self.start_application():
                self.test_api_endpoints()
                self.test_web_interface()
                self.test_network_features()
                self.test_cloudflare_integration()
                self.test_image_builder()
            
            # Generate report
            report = self.generate_test_report()
            
            return report
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            return None
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            return None
        finally:
            self.cleanup()

def main():
    """Main function"""
    tester = CodespacesTester()
    
    try:
        report = tester.run_all_tests()
        
        if report:
            # Determine exit code based on results
            if report['summary']['failed'] > 0:
                sys.exit(1)
            else:
                sys.exit(0)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
