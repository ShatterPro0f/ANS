"""
Integration test script for the refactored ANS application.

Tests all phases of the refactoring to ensure modules work together.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    tests = []
    
    # Test signals module
    try:
        from ans.signals import SignalBroker
        print("✓ ans.signals.SignalBroker")
        tests.append(True)
    except Exception as e:
        print(f"✗ ans.signals.SignalBroker: {e}")
        tests.append(False)
    
    # Test utils modules
    for module in ['constants', 'config', 'export']:
        try:
            exec(f"from ans.utils import {module}")
            print(f"✓ ans.utils.{module}")
            tests.append(True)
        except Exception as e:
            print(f"✗ ans.utils.{module}: {e}")
            tests.append(False)
    
    # Test backend modules
    for module in ['project', 'llm', 'thread']:
        try:
            exec(f"from ans.backend import {module}")
            print(f"✓ ans.backend.{module}")
            tests.append(True)
        except Exception as e:
            print(f"✗ ans.backend.{module}: {e}")
            tests.append(False)
    
    # Test UI modules
    try:
        from ans.ui import title_bar
        print("✓ ans.ui.title_bar")
        tests.append(True)
    except Exception as e:
        print(f"✗ ans.ui.title_bar: {e}")
        tests.append(False)
    
    # Test tab modules
    tabs = ['initialization', 'novel_idea', 'planning', 'writing', 'logs', 'dashboard', 'settings']
    for tab in tabs:
        try:
            exec(f"from ans.ui.tabs import {tab}")
            print(f"✓ ans.ui.tabs.{tab}")
            tests.append(True)
        except Exception as e:
            print(f"✗ ans.ui.tabs.{tab}: {e}")
            tests.append(False)
    
    # Test main window
    try:
        from ans.ui import main_window
        print("✓ ans.ui.main_window")
        tests.append(True)
    except Exception as e:
        print(f"✗ ans.ui.main_window: {e}")
        tests.append(False)
    
    print(f"\nResult: {sum(tests)}/{len(tests)} modules imported successfully")
    return all(tests)


def test_signal_broker():
    """Test SignalBroker creation and signals."""
    print("\n" + "=" * 60)
    print("TEST 2: SignalBroker Functionality")
    print("=" * 60)
    
    try:
        from ans.signals import SignalBroker
        from PyQt5 import QtCore, QtWidgets
        
        # Create app instance (required for Qt)
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        
        broker = SignalBroker()
        
        # Check signals exist
        signals_to_check = [
            'start_signal', 'approve_signal', 'adjust_signal',
            'log_update', 'error_signal', 'new_synopsis', 'new_outline'
        ]
        
        all_found = True
        for sig_name in signals_to_check:
            if hasattr(broker, sig_name):
                print(f"✓ SignalBroker.{sig_name}")
            else:
                print(f"✗ SignalBroker.{sig_name} missing")
                all_found = False
        
        print(f"\nResult: SignalBroker has all required signals: {all_found}")
        return all_found
    except Exception as e:
        print(f"✗ Error testing SignalBroker: {e}")
        return False


def test_project_manager():
    """Test ProjectManager singleton."""
    print("\n" + "=" * 60)
    print("TEST 3: ProjectManager Functionality")
    print("=" * 60)
    
    try:
        from ans.backend.project import get_project_manager
        
        pm = get_project_manager()
        print(f"✓ ProjectManager created: {pm}")
        
        # Test singleton
        pm2 = get_project_manager()
        if pm is pm2:
            print("✓ ProjectManager is singleton")
            return True
        else:
            print("✗ ProjectManager singleton failed")
            return False
    except Exception as e:
        print(f"✗ Error testing ProjectManager: {e}")
        return False


def test_tab_creation():
    """Test tab creation functions."""
    print("\n" + "=" * 60)
    print("TEST 4: Tab Creation Functions")
    print("=" * 60)
    
    try:
        from PyQt5 import QtWidgets, QtCore
        from ans.signals import SignalBroker
        from ans.ui.tabs import (
            create_initialization_tab, create_novel_idea_tab,
            create_planning_tab, create_writing_tab,
            create_logs_tab, create_dashboard_tab, create_settings_tab
        )
        
        # Create app instance
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        
        broker = SignalBroker()
        
        # Create a mock main window
        class MockMainWindow:
            pass
        
        main_window = MockMainWindow()
        
        tabs = [
            ('initialization', create_initialization_tab),
            ('novel_idea', create_novel_idea_tab),
            ('planning', create_planning_tab),
            ('writing', create_writing_tab),
            ('logs', create_logs_tab),
            ('dashboard', create_dashboard_tab),
            ('settings', create_settings_tab),
        ]
        
        results = []
        for tab_name, create_func in tabs:
            try:
                tab, refs = create_func(main_window, broker)
                if isinstance(tab, QtWidgets.QWidget):
                    print(f"✓ {tab_name} tab created")
                    results.append(True)
                else:
                    print(f"✗ {tab_name} tab not a QWidget")
                    results.append(False)
            except Exception as e:
                print(f"✗ {tab_name} tab failed: {e}")
                results.append(False)
        
        print(f"\nResult: {sum(results)}/{len(results)} tabs created successfully")
        return all(results)
    except Exception as e:
        print(f"✗ Error testing tab creation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_constants():
    """Test constants module."""
    print("\n" + "=" * 60)
    print("TEST 5: Constants Module")
    print("=" * 60)
    
    try:
        from ans.utils.constants import (
            PROJECTS_DIR, CONFIG_DIR, ASSETS_DIR,
            DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE
        )
        
        constants_found = []
        for const_name in ['PROJECTS_DIR', 'CONFIG_DIR', 'ASSETS_DIR', 
                          'DEFAULT_LLM_MODEL', 'DEFAULT_TEMPERATURE']:
            print(f"✓ {const_name} defined")
            constants_found.append(True)
        
        print(f"\nResult: {len(constants_found)} constants available")
        return True
    except Exception as e:
        print(f"✗ Error testing constants: {e}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("ANS REFACTORING INTEGRATION TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("SignalBroker", test_signal_broker()))
    results.append(("ProjectManager", test_project_manager()))
    results.append(("Tab Creation", test_tab_creation()))
    results.append(("Constants", test_constants()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The refactoring is working.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
