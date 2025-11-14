"""
Test RabbitMQ với credentials tùy chỉnh
"""
import os
import sys

# Set environment variables cho RabbitMQ
os.environ['RABBITMQ_USERNAME'] = 'rabbitmq'
os.environ['RABBITMQ_PASSWORD'] = 'rabbitmq'

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rabbitmq import get_rabbitmq_service

def test_with_custom_credentials():
    """Test RabbitMQ với username và password rabbitmq"""
    print("🐰 Testing RabbitMQ với credentials: rabbitmq/rabbitmq")
    print("=" * 50)
    
    # Show current config
    print("Current RabbitMQ Configuration:")
    print(f"  Host: {os.getenv('RABBITMQ_HOST', 'localhost')}")
    print(f"  Port: {os.getenv('RABBITMQ_PORT', '5672')}")
    print(f"  Username: {os.getenv('RABBITMQ_USERNAME', 'guest')}")
    print(f"  Password: {os.getenv('RABBITMQ_PASSWORD', 'guest')}")
    print()
    
    rabbitmq_service = get_rabbitmq_service()
    
    # Test connection
    print("1. Testing connection...")
    if rabbitmq_service.connect():
        print("   ✅ Connected successfully!")
        
        # Test message publishing
        print("2. Testing message publishing...")
        test_upload_paths = [
            "/storage/uploads/document1.xlsx",
            "/storage/uploads/document2.pdf"
        ]
        test_template_path = "/storage/uploads/template.xlsx"
        
        success = rabbitmq_service.publish_file_upload_message(
            upload_paths=test_upload_paths,
            template_path=test_template_path,
            user_id=123
        )
        
        if success:
            print("   ✅ Message published successfully!")
            print("   📧 Message content:")
            print("   {")
            print('     "event_type": "file_uploaded",')
            print(f'     "upload_path_files": {test_upload_paths},')
            print(f'     "template_path_file": "{test_template_path}",')
            print('     "user_id": 123,')
            print('     "timestamp": "2024-08-19T..."')
            print("   }")
        else:
            print("   ❌ Failed to publish message")
        
        rabbitmq_service.close()
        print("3. Connection closed")
        
        if success:
            print("\n🎉 RabbitMQ integration is working perfectly!")
            return True
    else:
        print("   ❌ Connection failed")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify docker-compose is running:")
        print("      docker-compose ps")
        print("   2. Check RabbitMQ logs:")
        print("      docker-compose logs rabbitmq")
        print("   3. Verify credentials in docker-compose.yml")
        return False
    
    return False

if __name__ == "__main__":
    success = test_with_custom_credentials()
    if success:
        print("\n✅ Test completed successfully!")
        print("\n📝 To use these credentials in your app, set:")
        print("   RABBITMQ_USERNAME=rabbitmq")
        print("   RABBITMQ_PASSWORD=rabbitmq")
    else:
        print("\n❌ Test failed. Please check your RabbitMQ configuration.")
        sys.exit(1)
