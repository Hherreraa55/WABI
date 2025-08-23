import requests
import sys
import json
from datetime import datetime

class WABIBackendTester:
    def __init__(self, base_url="https://wabi-onboarding.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Response Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response Text: {response.text}")
                response_data = {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")

            return success, response_data

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_departments_endpoint(self):
        """Test departments endpoint"""
        success, response = self.run_test("Get Guatemala Departments", "GET", "departments", 200)
        if success and 'departments' in response:
            departments = response['departments']
            expected_departments = [
                "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula", "El Progreso",
                "Escuintla", "Guatemala", "Huehuetenango", "Izabal", "Jalapa", "Jutiapa",
                "Petén", "Quetzaltenango", "Quiché", "Retalhuleu", "Sacatepéquez",
                "San Marcos", "Santa Rosa", "Sololá", "Suchitepéquez", "Totonicapán", "Zacapa"
            ]
            if set(departments) == set(expected_departments):
                print("✅ All Guatemala departments present")
                return True
            else:
                print("❌ Department list mismatch")
                return False
        return success

    def test_valid_registration(self):
        """Test valid user registration"""
        test_data = {
            "nombre": "María González Test",
            "username": f"maria_test_{datetime.now().strftime('%H%M%S')}",
            "celular": "50255557777",
            "nombre_negocio": "Boutique María Test",
            "departamento": "Quetzaltenango",
            "municipio": "Quetzaltenango",
            "numero_celular_negocio": "50244448888"
        }
        
        success, response = self.run_test("Valid User Registration", "POST", "register", 200, test_data)
        if success and response.get('success') and response.get('message') == "¡Bienvenido a WABI! Tu negocio ya está en movimiento 🚀":
            print("✅ Registration successful with correct message")
            return True, response.get('user_id')
        return False, None

    def test_duplicate_username(self):
        """Test duplicate username validation"""
        # First registration
        test_data = {
            "nombre": "Test User 1",
            "username": f"duplicate_test_{datetime.now().strftime('%H%M%S')}",
            "celular": "50255551111",
            "nombre_negocio": "Test Business 1",
            "departamento": "Guatemala",
            "municipio": "Guatemala",
            "numero_celular_negocio": "50244441111"
        }
        
        success1, _ = self.run_test("First Registration (for duplicate test)", "POST", "register", 200, test_data)
        
        if success1:
            # Try duplicate username with different phone
            test_data["celular"] = "50255552222"
            test_data["numero_celular_negocio"] = "50244442222"
            test_data["nombre"] = "Test User 2"
            
            success2, response = self.run_test("Duplicate Username Test", "POST", "register", 400, test_data)
            if success2 and "nombre de usuario ya está en uso" in response.get('detail', ''):
                print("✅ Duplicate username correctly rejected")
                return True
        
        return False

    def test_duplicate_phone(self):
        """Test duplicate phone number validation"""
        unique_phone = f"5025555{datetime.now().strftime('%H%M')}"
        
        test_data = {
            "nombre": "Test User Phone 1",
            "username": f"phone_test1_{datetime.now().strftime('%H%M%S')}",
            "celular": unique_phone,
            "nombre_negocio": "Test Business Phone 1",
            "departamento": "Guatemala",
            "municipio": "Guatemala",
            "numero_celular_negocio": "50244443333"
        }
        
        success1, _ = self.run_test("First Registration (for phone duplicate test)", "POST", "register", 200, test_data)
        
        if success1:
            # Try duplicate phone with different username
            test_data["username"] = f"phone_test2_{datetime.now().strftime('%H%M%S')}"
            test_data["nombre"] = "Test User Phone 2"
            
            success2, response = self.run_test("Duplicate Phone Test", "POST", "register", 400, test_data)
            if success2 and "número de celular ya está registrado" in response.get('detail', ''):
                print("✅ Duplicate phone correctly rejected")
                return True
        
        return False

    def test_invalid_phone_format(self):
        """Test invalid phone number format"""
        test_data = {
            "nombre": "Test Invalid Phone",
            "username": f"invalid_phone_{datetime.now().strftime('%H%M%S')}",
            "celular": "12345678",  # Invalid format
            "nombre_negocio": "Test Business",
            "departamento": "Guatemala",
            "municipio": "Guatemala",
            "numero_celular_negocio": "50244444444"
        }
        
        success, response = self.run_test("Invalid Phone Format", "POST", "register", 400, test_data)
        if success and "formato internacional válido" in response.get('detail', ''):
            print("✅ Invalid phone format correctly rejected")
            return True
        return False

    def test_invalid_username_format(self):
        """Test invalid username format"""
        test_data = {
            "nombre": "Test Invalid Username",
            "username": "invalid-username!",  # Contains invalid characters
            "celular": "50255554444",
            "nombre_negocio": "Test Business",
            "departamento": "Guatemala",
            "municipio": "Guatemala",
            "numero_celular_negocio": "50244445555"
        }
        
        success, response = self.run_test("Invalid Username Format", "POST", "register", 400, test_data)
        if success and ("letras, números y guiones bajos" in response.get('detail', '') or 
                       "Username solo puede contener" in response.get('detail', '')):
            print("✅ Invalid username format correctly rejected")
            return True
        return False

    def test_invalid_department(self):
        """Test invalid department"""
        test_data = {
            "nombre": "Test Invalid Department",
            "username": f"invalid_dept_{datetime.now().strftime('%H%M%S')}",
            "celular": "50255556666",
            "nombre_negocio": "Test Business",
            "departamento": "Invalid Department",
            "municipio": "Test Municipality",
            "numero_celular_negocio": "50244446666"
        }
        
        success, response = self.run_test("Invalid Department", "POST", "register", 400, test_data)
        if success and "Departamento debe ser uno de" in response.get('detail', ''):
            print("✅ Invalid department correctly rejected")
            return True
        return False

    def test_missing_required_fields(self):
        """Test missing required fields"""
        test_data = {
            "nombre": "",  # Missing required field
            "username": f"missing_field_{datetime.now().strftime('%H%M%S')}",
            "celular": "50255557777",
            "nombre_negocio": "Test Business",
            "departamento": "Guatemala",
            "municipio": "Guatemala",
            "numero_celular_negocio": "50244447777"
        }
        
        success, response = self.run_test("Missing Required Fields", "POST", "register", 422, test_data)
        if success:
            print("✅ Missing required fields correctly rejected")
            return True
        return False

def main():
    print("🚀 Starting WABI Backend API Tests")
    print("=" * 50)
    
    tester = WABIBackendTester()
    
    # Test basic endpoints
    print("\n📡 Testing Basic Endpoints")
    print("-" * 30)
    tester.test_root_endpoint()
    tester.test_departments_endpoint()
    
    # Test valid registration
    print("\n✅ Testing Valid Registration")
    print("-" * 30)
    success, user_id = tester.test_valid_registration()
    
    # Test validation errors
    print("\n❌ Testing Validation Errors")
    print("-" * 30)
    tester.test_duplicate_username()
    tester.test_duplicate_phone()
    tester.test_invalid_phone_format()
    tester.test_invalid_username_format()
    tester.test_invalid_department()
    tester.test_missing_required_fields()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())