import requests
import sys
import json
from datetime import datetime

class AdminDashboardAPITester:
    def __init__(self, base_url="https://admin-central-38.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()  # Use session for cookies
        self.created_ids = {
            'users': [],
            'products': [],
            'pages': [],
            'orders': [],
            'categories': [],
            'services': [],
            'pricing': [],
            'testimonials': [],
            'banners': [],
            'media': [],
            'faqs': []
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.text else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test Authentication endpoints"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        # Test admin login
        login_data = {
            "email": "admin@admin.com",
            "password": "admin123"
        }
        
        success, response = self.run_test("Admin Login", "POST", "/auth/login", 200, login_data)
        if success:
            print("✅ Login successful")
            
            # Test get current user
            success, user_info = self.run_test("Get Current User", "GET", "/auth/me", 200)
            if success:
                print(f"✅ Current user: {user_info.get('name', 'Unknown')}")
            
            # Test admin info
            success, admin_info = self.run_test("Get Admin Info", "GET", "/auth/admin-info", 200)
            
            return True
        else:
            print("❌ Login failed - cannot proceed with authenticated tests")
            return False

    def test_site_content_hero(self):
        """Test Hero Section content management"""
        print("\n" + "="*50)
        print("TESTING HERO SECTION")
        print("="*50)
        
        # Test GET hero section
        success, hero = self.run_test("Get Hero Section", "GET", "/content/hero", 200)
        if not success:
            return False
        
        # Test UPDATE hero section
        update_data = {
            "title": "Test Hero Title",
            "subtitle": "Test Hero Subtitle",
            "description": "Test hero description",
            "button_text": "Test Button",
            "background_color": "#1e293b",
            "text_color": "#ffffff"
        }
        
        success, _ = self.run_test("Update Hero Section", "PUT", "/content/hero", 200, update_data)
        return success

    def test_site_content_services(self):
        """Test Services content management"""
        print("\n" + "="*50)
        print("TESTING SERVICES")
        print("="*50)
        
        # Test GET services
        success, services = self.run_test("Get Services", "GET", "/content/services", 200)
        if not success:
            return False
        
        # Test CREATE service
        test_service = {
            "title": f"Test Service {datetime.now().strftime('%H%M%S')}",
            "description": "Test service description",
            "icon": "star",
            "order": 1,
            "is_active": True
        }
        
        success, created_service = self.run_test("Create Service", "POST", "/content/services", 200, test_service)
        if success and 'id' in created_service:
            service_id = created_service['id']
            self.created_ids['services'].append(service_id)
            print(f"✅ Created service with ID: {service_id}")
            
            # Test UPDATE service
            update_data = {"title": "Updated Test Service", "description": "Updated description"}
            success, _ = self.run_test(f"Update Service {service_id}", "PUT", f"/content/services/{service_id}", 200, update_data)
            
            # Test DELETE service
            success, _ = self.run_test(f"Delete Service {service_id}", "DELETE", f"/content/services/{service_id}", 200)
            if success:
                self.created_ids['services'].remove(service_id)
        
        return True

    def test_site_content_pricing(self):
        """Test Pricing content management"""
        print("\n" + "="*50)
        print("TESTING PRICING")
        print("="*50)
        
        # Test GET pricing
        success, pricing = self.run_test("Get Pricing", "GET", "/content/pricing", 200)
        if not success:
            return False
        
        # Test CREATE pricing
        test_pricing = {
            "name": f"Test Plan {datetime.now().strftime('%H%M%S')}",
            "price": 99.99,
            "currency": "₺",
            "period": "ay",
            "description": "Test pricing plan",
            "features": ["Feature 1", "Feature 2", "Feature 3"],
            "is_popular": False,
            "button_text": "Satın Al",
            "order": 1,
            "is_active": True
        }
        
        success, created_pricing = self.run_test("Create Pricing", "POST", "/content/pricing", 200, test_pricing)
        if success and 'id' in created_pricing:
            pricing_id = created_pricing['id']
            self.created_ids['pricing'].append(pricing_id)
            print(f"✅ Created pricing with ID: {pricing_id}")
            
            # Test UPDATE pricing
            update_data = {"name": "Updated Test Plan", "price": 149.99, "is_popular": True}
            success, _ = self.run_test(f"Update Pricing {pricing_id}", "PUT", f"/content/pricing/{pricing_id}", 200, update_data)
            
            # Test DELETE pricing
            success, _ = self.run_test(f"Delete Pricing {pricing_id}", "DELETE", f"/content/pricing/{pricing_id}", 200)
            if success:
                self.created_ids['pricing'].remove(pricing_id)
        
        return True

    def test_site_content_testimonials(self):
        """Test Testimonials content management"""
        print("\n" + "="*50)
        print("TESTING TESTIMONIALS")
        print("="*50)
        
        # Test GET testimonials
        success, testimonials = self.run_test("Get Testimonials", "GET", "/content/testimonials", 200)
        if not success:
            return False
        
        # Test CREATE testimonial
        test_testimonial = {
            "name": f"Test Customer {datetime.now().strftime('%H%M%S')}",
            "title": "Test Company CEO",
            "content": "This is a test testimonial content",
            "rating": 5,
            "order": 1,
            "is_active": True
        }
        
        success, created_testimonial = self.run_test("Create Testimonial", "POST", "/content/testimonials", 200, test_testimonial)
        if success and 'id' in created_testimonial:
            testimonial_id = created_testimonial['id']
            self.created_ids['testimonials'].append(testimonial_id)
            print(f"✅ Created testimonial with ID: {testimonial_id}")
            
            # Test UPDATE testimonial
            update_data = {"name": "Updated Test Customer", "rating": 4}
            success, _ = self.run_test(f"Update Testimonial {testimonial_id}", "PUT", f"/content/testimonials/{testimonial_id}", 200, update_data)
            
            # Test DELETE testimonial
            success, _ = self.run_test(f"Delete Testimonial {testimonial_id}", "DELETE", f"/content/testimonials/{testimonial_id}", 200)
            if success:
                self.created_ids['testimonials'].remove(testimonial_id)
        
        return True

    def test_site_content_banners(self):
        """Test Banners content management"""
        print("\n" + "="*50)
        print("TESTING BANNERS")
        print("="*50)
        
        # Test GET banners
        success, banners = self.run_test("Get Banners", "GET", "/content/banners", 200)
        if not success:
            return False
        
        # Test CREATE banner
        test_banner = {
            "title": f"Test Banner {datetime.now().strftime('%H%M%S')}",
            "subtitle": "Test banner subtitle",
            "image": "https://via.placeholder.com/800x400",
            "link": "#test",
            "button_text": "Learn More",
            "order": 1,
            "is_active": True
        }
        
        success, created_banner = self.run_test("Create Banner", "POST", "/content/banners", 200, test_banner)
        if success and 'id' in created_banner:
            banner_id = created_banner['id']
            self.created_ids['banners'].append(banner_id)
            print(f"✅ Created banner with ID: {banner_id}")
            
            # Test UPDATE banner
            update_data = {"title": "Updated Test Banner", "subtitle": "Updated subtitle"}
            success, _ = self.run_test(f"Update Banner {banner_id}", "PUT", f"/content/banners/{banner_id}", 200, update_data)
            
            # Test DELETE banner
            success, _ = self.run_test(f"Delete Banner {banner_id}", "DELETE", f"/content/banners/{banner_id}", 200)
            if success:
                self.created_ids['banners'].remove(banner_id)
        
        return True

    def test_site_content_media(self):
        """Test Media Library content management"""
        print("\n" + "="*50)
        print("TESTING MEDIA LIBRARY")
        print("="*50)
        
        # Test GET media
        success, media = self.run_test("Get Media", "GET", "/content/media", 200)
        if not success:
            return False
        
        # Test CREATE media
        test_media = {
            "name": f"Test Media {datetime.now().strftime('%H%M%S')}",
            "url": "https://via.placeholder.com/400x300",
            "type": "image",
            "alt_text": "Test image",
            "category": "test"
        }
        
        success, created_media = self.run_test("Create Media", "POST", "/content/media", 200, test_media)
        if success and 'id' in created_media:
            media_id = created_media['id']
            self.created_ids['media'].append(media_id)
            print(f"✅ Created media with ID: {media_id}")
            
            # Test DELETE media
            success, _ = self.run_test(f"Delete Media {media_id}", "DELETE", f"/content/media/{media_id}", 200)
            if success:
                self.created_ids['media'].remove(media_id)
        
        return True

    def test_site_content_faqs(self):
        """Test FAQs content management"""
        print("\n" + "="*50)
        print("TESTING FAQS")
        print("="*50)
        
        # Test GET FAQs
        success, faqs = self.run_test("Get FAQs", "GET", "/content/faqs", 200)
        if not success:
            return False
        
        # Test CREATE FAQ
        test_faq = {
            "question": f"Test Question {datetime.now().strftime('%H%M%S')}?",
            "answer": "This is a test answer to the test question.",
            "category": "general",
            "order": 1,
            "is_active": True
        }
        
        success, created_faq = self.run_test("Create FAQ", "POST", "/content/faqs", 200, test_faq)
        if success and 'id' in created_faq:
            faq_id = created_faq['id']
            self.created_ids['faqs'].append(faq_id)
            print(f"✅ Created FAQ with ID: {faq_id}")
            
            # Test UPDATE FAQ
            update_data = {"question": "Updated Test Question?", "answer": "Updated test answer."}
            success, _ = self.run_test(f"Update FAQ {faq_id}", "PUT", f"/content/faqs/{faq_id}", 200, update_data)
            
            # Test DELETE FAQ
            success, _ = self.run_test(f"Delete FAQ {faq_id}", "DELETE", f"/content/faqs/{faq_id}", 200)
            if success:
                self.created_ids['faqs'].remove(faq_id)
        
        return True

    def test_content_all(self):
        """Test get all site content endpoint"""
        print("\n" + "="*50)
        print("TESTING GET ALL CONTENT")
        print("="*50)
        
        success, content = self.run_test("Get All Content", "GET", "/content/all", 200)
        if success:
            print("✅ Successfully retrieved all site content")
        return success
        """Test dashboard statistics endpoint"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD STATS")
        print("="*50)
        
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "/dashboard/stats",
            200
        )
        
        if success:
            required_fields = ['total_users', 'total_products', 'total_orders', 'total_revenue', 'monthly_revenue', 'order_statuses']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"⚠️  Missing fields in response: {missing_fields}")
            else:
                print("✅ All required dashboard fields present")
        
        return success

    def test_users_crud(self):
        """Test Users CRUD operations"""
        print("\n" + "="*50)
        print("TESTING USERS CRUD")
        print("="*50)
        
        # Test GET users
        success, users = self.run_test("Get Users", "GET", "/users", 200)
        if not success:
            return False
        
        # Test CREATE user
        test_user = {
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "testpass123",
            "role": "user",
            "status": "active",
            "phone": "0532 123 4567"
        }
        
        success, created_user = self.run_test("Create User", "POST", "/users", 200, test_user)
        if success and 'id' in created_user:
            user_id = created_user['id']
            self.created_ids['users'].append(user_id)
            print(f"✅ Created user with ID: {user_id}")
            
            # Test GET specific user
            success, _ = self.run_test(f"Get User {user_id}", "GET", f"/users/{user_id}", 200)
            
            # Test UPDATE user
            update_data = {"name": "Updated Test User", "status": "inactive"}
            success, _ = self.run_test(f"Update User {user_id}", "PUT", f"/users/{user_id}", 200, update_data)
            
            # Test DELETE user
            success, _ = self.run_test(f"Delete User {user_id}", "DELETE", f"/users/{user_id}", 200)
            if success:
                self.created_ids['users'].remove(user_id)
        
        return True

    def test_products_crud(self):
        """Test Products CRUD operations"""
        print("\n" + "="*50)
        print("TESTING PRODUCTS CRUD")
        print("="*50)
        
        # Test GET products
        success, products = self.run_test("Get Products", "GET", "/products", 200)
        if not success:
            return False
        
        # Test CREATE product
        test_product = {
            "name": f"Test Product {datetime.now().strftime('%H%M%S')}",
            "description": "Test product description",
            "price": 99.99,
            "category": "Test Category",
            "stock": 10,
            "status": "draft"
        }
        
        success, created_product = self.run_test("Create Product", "POST", "/products", 200, test_product)
        if success and 'id' in created_product:
            product_id = created_product['id']
            self.created_ids['products'].append(product_id)
            print(f"✅ Created product with ID: {product_id}")
            
            # Test GET specific product
            success, _ = self.run_test(f"Get Product {product_id}", "GET", f"/products/{product_id}", 200)
            
            # Test UPDATE product
            update_data = {"name": "Updated Test Product", "price": 149.99, "status": "published"}
            success, _ = self.run_test(f"Update Product {product_id}", "PUT", f"/products/{product_id}", 200, update_data)
            
            # Test DELETE product
            success, _ = self.run_test(f"Delete Product {product_id}", "DELETE", f"/products/{product_id}", 200)
            if success:
                self.created_ids['products'].remove(product_id)
        
        return True

    def test_pages_crud(self):
        """Test Pages CRUD operations"""
        print("\n" + "="*50)
        print("TESTING PAGES CRUD")
        print("="*50)
        
        # Test GET pages
        success, pages = self.run_test("Get Pages", "GET", "/pages", 200)
        if not success:
            return False
        
        # Test CREATE page
        test_page = {
            "title": f"Test Page {datetime.now().strftime('%H%M%S')}",
            "slug": f"test-page-{datetime.now().strftime('%H%M%S')}",
            "content": "This is test page content",
            "meta_title": "Test Page Meta Title",
            "meta_description": "Test page meta description",
            "status": "draft"
        }
        
        success, created_page = self.run_test("Create Page", "POST", "/pages", 200, test_page)
        if success and 'id' in created_page:
            page_id = created_page['id']
            self.created_ids['pages'].append(page_id)
            print(f"✅ Created page with ID: {page_id}")
            
            # Test GET specific page
            success, _ = self.run_test(f"Get Page {page_id}", "GET", f"/pages/{page_id}", 200)
            
            # Test UPDATE page
            update_data = {"title": "Updated Test Page", "status": "published"}
            success, _ = self.run_test(f"Update Page {page_id}", "PUT", f"/pages/{page_id}", 200, update_data)
            
            # Test DELETE page
            success, _ = self.run_test(f"Delete Page {page_id}", "DELETE", f"/pages/{page_id}", 200)
            if success:
                self.created_ids['pages'].remove(page_id)
        
        return True

    def test_orders_crud(self):
        """Test Orders CRUD operations"""
        print("\n" + "="*50)
        print("TESTING ORDERS CRUD")
        print("="*50)
        
        # Test GET orders
        success, orders = self.run_test("Get Orders", "GET", "/orders", 200)
        if not success:
            return False
        
        # Test CREATE order
        test_order = {
            "customer_name": "Test Customer",
            "customer_email": f"customer{datetime.now().strftime('%H%M%S')}@example.com",
            "customer_phone": "0532 987 6543",
            "shipping_address": "Test Address, Test City",
            "items": [
                {
                    "product_id": "test-product-1",
                    "product_name": "Test Product",
                    "quantity": 2,
                    "price": 50.0
                }
            ],
            "total": 100.0,
            "status": "pending"
        }
        
        success, created_order = self.run_test("Create Order", "POST", "/orders", 200, test_order)
        if success and 'id' in created_order:
            order_id = created_order['id']
            self.created_ids['orders'].append(order_id)
            print(f"✅ Created order with ID: {order_id}")
            
            # Test GET specific order
            success, _ = self.run_test(f"Get Order {order_id}", "GET", f"/orders/{order_id}", 200)
            
            # Test UPDATE order (status change)
            update_data = {"status": "processing", "notes": "Order is being processed"}
            success, _ = self.run_test(f"Update Order {order_id}", "PUT", f"/orders/{order_id}", 200, update_data)
            
            # Test DELETE order
            success, _ = self.run_test(f"Delete Order {order_id}", "DELETE", f"/orders/{order_id}", 200)
            if success:
                self.created_ids['orders'].remove(order_id)
        
        return True

    def test_categories_crud(self):
        """Test Categories CRUD operations"""
        print("\n" + "="*50)
        print("TESTING CATEGORIES CRUD")
        print("="*50)
        
        # Test GET categories
        success, categories = self.run_test("Get Categories", "GET", "/categories", 200)
        if not success:
            return False
        
        # Test CREATE category
        test_category = {
            "name": f"Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Test category description"
        }
        
        success, created_category = self.run_test("Create Category", "POST", "/categories", 200, test_category)
        if success and 'id' in created_category:
            category_id = created_category['id']
            self.created_ids['categories'].append(category_id)
            print(f"✅ Created category with ID: {category_id}")
            
            # Test DELETE category
            success, _ = self.run_test(f"Delete Category {category_id}", "DELETE", f"/categories/{category_id}", 200)
            if success:
                self.created_ids['categories'].remove(category_id)
        
        return True

    def test_settings(self):
        """Test Settings operations"""
        print("\n" + "="*50)
        print("TESTING SETTINGS")
        print("="*50)
        
        # Test GET settings
        success, settings = self.run_test("Get Settings", "GET", "/settings", 200)
        if not success:
            return False
        
        # Test UPDATE settings
        update_data = {
            "site_name": "Updated Admin Dashboard",
            "contact_email": "updated@example.com",
            "contact_phone": "0212 999 8888"
        }
        
        success, _ = self.run_test("Update Settings", "PUT", "/settings", 200, update_data)
        return success

    def test_activity_logs(self):
        """Test Activity Logs"""
        print("\n" + "="*50)
        print("TESTING ACTIVITY LOGS")
        print("="*50)
        
        success, logs = self.run_test("Get Activity Logs", "GET", "/activity-logs", 200)
        return success

    def test_seed_data(self):
        """Test Seed Data endpoint"""
        print("\n" + "="*50)
        print("TESTING SEED DATA")
        print("="*50)
        
        success, response = self.run_test("Seed Data", "POST", "/seed-data", 200)
        return success

    def cleanup(self):
        """Clean up any created test data"""
        print("\n" + "="*50)
        print("CLEANUP")
        print("="*50)
        
        # Clean up in reverse order to avoid dependency issues
        for entity_type in ['orders', 'products', 'pages', 'users', 'categories']:
            for item_id in self.created_ids[entity_type]:
                try:
                    endpoint = f"/{entity_type}/{item_id}"
                    self.run_test(f"Cleanup {entity_type} {item_id}", "DELETE", endpoint, 200)
                except:
                    pass

def main():
    print("🚀 Starting Admin Dashboard API Tests")
    print("="*60)
    
    tester = AdminDashboardAPITester()
    
    try:
        # Test all endpoints
        tester.test_dashboard_stats()
        tester.test_users_crud()
        tester.test_products_crud()
        tester.test_pages_crud()
        tester.test_orders_crud()
        tester.test_categories_crud()
        tester.test_settings()
        tester.test_activity_logs()
        tester.test_seed_data()
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    finally:
        # Always try to cleanup
        tester.cleanup()
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())