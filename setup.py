#!/usr/bin/env python3
"""
Setup script for LiveKit Salon AI Agent

This script helps set up the project dependencies and configuration.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip3 install -r requirements.txt", "Installing dependencies")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if not os.path.exists('env.example'):
        print("❌ env.example file not found")
        return False
    
    try:
        with open('env.example', 'r') as example_file:
            example_content = example_file.read()
        
        with open('.env', 'w') as env_file:
            env_file.write(example_content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your LiveKit credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_demo():
    """Run the demo to verify setup"""
    print("\n🎭 Running demo to verify setup...")
    return run_command("python3 src/demo.py", "Running demo")

def main():
    """Main setup function"""
    print("🚀 LiveKit Salon AI Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("❌ Setup failed during environment file creation")
        sys.exit(1)
    
    # Run demo
    if not run_demo():
        print("❌ Setup failed during demo execution")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your LiveKit credentials:")
    print("   - LIVEKIT_URL")
    print("   - LIVEKIT_API_KEY") 
    print("   - LIVEKIT_API_SECRET")
    print("\n2. Run the agent:")
    print("   python3 src/main.py")
    print("\n3. Test with client (in another terminal):")
    print("   python3 src/test_client.py")
    print("\n4. View demo anytime:")
    print("   python3 src/demo.py")

if __name__ == "__main__":
    main() 