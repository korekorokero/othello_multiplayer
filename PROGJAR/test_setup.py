#!/usr/bin/env python3
"""
Test environment setup and validation
Creates necessary directories and validates the project structure
"""

import os
import sys

def create_init_files():
    """Create __init__.py files for all packages"""
    packages = [
        'shared',
        'game', 
        'tests'
    ]
    
    for package in packages:
        if os.path.exists(package):
            init_file = os.path.join(package, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'# {package} package\n')
                print(f"Created {init_file}")
            else:
                print(f"✓ {init_file} exists")

def validate_project_structure():
    """Validate the expected project structure"""
    print("Validating project structure...")
    
    required_files = [
        'shared/constants.py',
        'shared/messages.py', 
        'shared/utils.py',
        'game/othello_board.py',
        'game/othello_rules.py',
        'game/player.py',
        'game/game_state.py',
        'tests/test_game_logic.py',
        'tests/test_network.py',
        'tests/test_integration.py',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("\n✅ All required files present")
    return True

def test_basic_imports():
    """Test that all modules can be imported"""
    print("\nTesting basic imports...")
    
    imports_to_test = [
        ("shared.constants", "BLACK, WHITE, EMPTY"),
        ("shared.messages", "Message, create_login_message"),
        ("shared.utils", "generate_room_code, validate_username"),
        ("game.othello_board", "OthelloBoard"),
        ("game.othello_rules", "OthelloRules"),
        ("game.player", "Player"),
        ("game.game_state", "GameState"),
    ]
    
    failed_imports = []
    
    for module_name, items in imports_to_test:
        try:
            exec(f"from {module_name} import {items}")
            print(f"✓ {module_name}")
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"❌ {module_name}: {e}")
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} modules:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    
    print("\n✅ All imports successful")
    return True

def create_test_directories():
    """Create test directories if they don't exist"""
    directories = ['shared', 'game', 'tests']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def main():
    """Main setup function"""
    print("🔧 OTHELLO MULTIPLAYER - TEST ENVIRONMENT SETUP")
    print("="*60)
    
    # Create directories
    create_test_directories()
    
    # Create __init__.py files
    print("\nCreating __init__.py files...")
    create_init_files()
    
    # Validate structure
    print("\n" + "="*60)
    if not validate_project_structure():
        print("\n❌ Project structure validation failed")
        print("Please ensure all required files are present")
        return False
    
    # Test imports
    print("\n" + "="*60)
    if not test_basic_imports():
        print("\n❌ Import validation failed")
        print("Please check for syntax errors in your modules")
        return False
    
    # Success
    print("\n" + "="*60)
    print("✅ TEST ENVIRONMENT SETUP COMPLETE")
    print("="*60)
    print("🚀 You can now run the tests:")
    print("   python run_tests.py")
    print("   python run_tests.py --smoke")
    print("   python tests/test_game_logic.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)