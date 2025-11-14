"""
Script to set up RabbitMQ with proper user credentials for Lengkeng API
"""
import subprocess
import time
import sys

def run_command(command, description):
    """Run a command and print the result"""
    print(f"📋 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def setup_rabbitmq():
    """Set up RabbitMQ with proper user credentials"""
    print("🐰 Setting up RabbitMQ for Lengkeng API")
    print("=" * 50)
    
    # Check if RabbitMQ container is running
    print("1. Checking RabbitMQ status...")
    result = subprocess.run("docker ps --filter name=rabbitmq --format '{{.Names}}'", 
                           shell=True, capture_output=True, text=True)
    
    if "rabbitmq" not in result.stdout:
        print("   RabbitMQ container not found. Starting new container...")
        
        # Stop any existing rabbitmq container
        run_command("docker stop rabbitmq 2>/dev/null || true", "Stopping existing container")
        run_command("docker rm rabbitmq 2>/dev/null || true", "Removing existing container")
        
        # Start new RabbitMQ container
        success = run_command(
            "docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 "
            "-e RABBITMQ_DEFAULT_USER=guest -e RABBITMQ_DEFAULT_PASS=guest "
            "rabbitmq:3-management",
            "Starting RabbitMQ container"
        )
        
        if not success:
            print("❌ Failed to start RabbitMQ container")
            return False
            
        print("   ⏳ Waiting for RabbitMQ to start (30 seconds)...")
        time.sleep(30)
    else:
        print("   ✅ RabbitMQ container is already running")
    
    # Create lengkeng user
    print("\n2. Creating lengkeng user...")
    commands = [
        ("docker exec rabbitmq rabbitmqctl add_user lengkeng lengkeng123", 
         "Adding user 'lengkeng'"),
        ("docker exec rabbitmq rabbitmqctl set_user_tags lengkeng administrator", 
         "Setting administrator tag"),
        ("docker exec rabbitmq rabbitmqctl set_permissions -p / lengkeng '.*' '.*' '.*'", 
         "Setting permissions")
    ]
    
    all_success = True
    for command, description in commands:
        success = run_command(command, description)
        if not success:
            all_success = False
    
    # Test connection
    print("\n3. Testing connection...")
    test_result = subprocess.run(
        [sys.executable, "scripts/test_rabbitmq.py"],
        capture_output=True, text=True
    )
    
    if test_result.returncode == 0:
        print("   ✅ Connection test passed!")
    else:
        print("   ❌ Connection test failed")
        print(f"   Output: {test_result.stdout}")
        print(f"   Error: {test_result.stderr}")
    
    print("\n" + "=" * 50)
    if all_success:
        print("🎉 RabbitMQ setup completed successfully!")
        print("\n📝 Environment variables to set:")
        print("   RABBITMQ_USERNAME=lengkeng")
        print("   RABBITMQ_PASSWORD=lengkeng123")
        print("\n🌐 Access RabbitMQ Management UI:")
        print("   URL: http://localhost:15672")
        print("   Username: lengkeng")
        print("   Password: lengkeng123")
        print("\n   Or use guest/guest for management UI only")
    else:
        print("❌ RabbitMQ setup encountered some issues")
        print("   You may need to manually configure the user credentials")
    
    return all_success

if __name__ == "__main__":
    setup_rabbitmq()
