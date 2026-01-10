#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime

class SimpleAPITester:
    def __init__(self, base_url="https://admin-central-38.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0

    def test(self, name, method, endpoint, expected_status=200, data=None):
        """Run a single test"""
        url = f"{self.api_url}{endpoint}"
        self.tests_run += 1
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            
            success = response.status_code == expected_status
            status = "✅ PASS" if success else "❌ FAIL"
            
            print(f"{status} {name} - {response.status_code}")
            
            if success:
                self.tests_passed += 1
                return True, response.json() if response.text else {}
            else:
                if response.text:
                    print(f"     Error: {response.text[:100]}")
                return False, {}
                
        except Exception as e:
            print(f"❌ FAIL {name} - Exception: {str(e)}")
            return False, {}

def main():
    print("🚀 Admin Dashboard API Quick Test")
    print("=" * 50)
    
    tester = SimpleAPITester()
    
    # Test login first
    print("\n📋 Authentication Tests:")
    success, _ = tester.test("Admin Login", "POST", "/auth/login", 200, {
        "email": "admin@admin.com", 
        "password": "admin123"
    })
    
    if success:
        print("✅ Login successful - session established")
    else:
        print("❌ Login failed")
        return 1
    
    # Test dashboard
    print("\n📊 Dashboard Tests:")
    tester.test("Dashboard Stats", "GET", "/dashboard/stats")
    
    # Test site content endpoints
    print("\n🎨 Site Content Tests:")
    tester.test("Get Hero Section", "GET", "/content/hero")
    tester.test("Get Services", "GET", "/content/services")
    tester.test("Get Pricing", "GET", "/content/pricing")
    tester.test("Get Testimonials", "GET", "/content/testimonials")
    tester.test("Get Banners", "GET", "/content/banners")
    tester.test("Get Media", "GET", "/content/media")
    tester.test("Get FAQs", "GET", "/content/faqs")
    
    # Test CRUD endpoints
    print("\n📝 CRUD Tests:")
    tester.test("Get Users", "GET", "/users")
    tester.test("Get Products", "GET", "/products")
    tester.test("Get Pages", "GET", "/pages")
    tester.test("Get Orders", "GET", "/orders")
    tester.test("Get Categories", "GET", "/categories")
    
    # Test settings
    print("\n⚙️ Settings Tests:")
    tester.test("Get Settings", "GET", "/settings")
    tester.test("Get Activity Logs", "GET", "/activity-logs")
    
    # Test content creation (basic)
    print("\n➕ Content Creation Tests:")
    
    # Create a service
    service_data = {
        "title": f"Test Service {datetime.now().strftime('%H%M%S')}",
        "description": "Test service description",
        "icon": "star",
        "order": 1,
        "is_active": True
    }
    success, service = tester.test("Create Service", "POST", "/content/services", 200, service_data)
    
    if success and 'id' in service:
        service_id = service['id']
        # Update the service
        tester.test("Update Service", "PUT", f"/content/services/{service_id}", 200, {
            "title": "Updated Test Service"
        })
        # Delete the service
        tester.test("Delete Service", "DELETE", f"/content/services/{service_id}")
    
    # Create a FAQ
    faq_data = {
        "question": f"Test Question {datetime.now().strftime('%H%M%S')}?",
        "answer": "This is a test answer.",
        "category": "general",
        "order": 1,
        "is_active": True
    }
    success, faq = tester.test("Create FAQ", "POST", "/content/faqs", 200, faq_data)
    
    if success and 'id' in faq:
        faq_id = faq['id']
        tester.test("Delete FAQ", "DELETE", f"/content/faqs/{faq_id}")
    
    # Results
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Total Tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed}")
    print(f"Failed: {tester.tests_run - tester.tests_passed}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! API is working well.")
        return 0
    elif success_rate >= 70:
        print("⚠️ Good, but some issues found.")
        return 0
    else:
        print("❌ Multiple API issues detected.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
