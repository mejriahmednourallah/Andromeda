#!/usr/bin/env python
"""
Simple test runner for Andromeda
Run specific tests or all tests
"""

import os
import sys
import subprocess

def run_smoke_test():
    """Run the basic smoke test"""
    print("🧪 Running smoke test...")
    result = subprocess.run([sys.executable, 'smoke_test.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_ai_tests():
    """Run AI service tests"""
    print("🤖 Running AI service tests...")
    result = subprocess.run([sys.executable, 'test_suite.py', 'AIAnalysisServiceTest'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_view_tests():
    """Run view tests"""
    print("🌐 Running view tests...")
    result = subprocess.run([sys.executable, 'test_suite.py', 'ViewTest'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_model_tests():
    """Run model tests"""
    print("📊 Running model tests...")
    result = subprocess.run([sys.executable, 'test_suite.py', 'ModelTest'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_all_tests():
    """Run all tests"""
    print("🚀 Running complete test suite...")
    result = subprocess.run([sys.executable, 'test_suite.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_specific_ai_test(test_name):
    """Run a specific AI test"""
    print(f"🎯 Running AI test: {test_name}")
    result = subprocess.run([sys.executable, 'test_suite.py', 'AIAnalysisServiceTest', test_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def show_menu():
    """Show test menu"""
    print("\n" + "="*50)
    print("🧪 ANDROMEDA TEST MENU")
    print("="*50)
    print("1. Run smoke test (basic functionality)")
    print("2. Run all AI service tests")
    print("3. Run all view tests")
    print("4. Run all model tests")
    print("5. Run complete test suite")
    print("6. Run specific AI test")
    print("7. Test AI analysis manually")
    print("8. Test souvenir creation")
    print("9. Test time capsule functionality")
    print("0. Exit")
    print("="*50)

def test_ai_analysis_manually():
    """Manual test for AI analysis"""
    print("🧠 Manual AI Analysis Test")
    print("-" * 30)

    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
    django.setup()

    from core.models import User, Souvenir
    from core.ai_services import AIAnalysisService

    # Create test user if doesn't exist
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass')
        user.save()
        print("✓ Created test user")

    # Create test souvenir
    souvenir = Souvenir.objects.create(
        utilisateur=user,
        titre="Manual Test Memory",
        description="This is a beautiful memory of walking in the park on a sunny day with colorful flowers and happy people around.",
        emotion='joy',
        theme='nature',
        date_evenement='2024-01-01'
    )
    print(f"✓ Created test memory: {souvenir.titre}")

    # Run AI analysis
    try:
        analysis = AIAnalysisService.analyze_memory(souvenir)
        print("✓ AI Analysis completed!")
        print(f"  Summary: {analysis.resume_genere}")
        print(f"  Keywords: {analysis.mots_cles}")
        print(f"  Emotion: {analysis.emotion_texte}")
        print(f"  Model: {analysis.modele_utilise}")
    except Exception as e:
        print(f"✗ AI Analysis failed: {e}")

def test_souvenir_creation():
    """Manual test for souvenir creation"""
    print("📝 Manual Souvenir Creation Test")
    print("-" * 35)

    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
    django.setup()

    from core.models import User, Souvenir

    # Create test user
    user, created = User.objects.get_or_create(
        username='souvenirtest',
        defaults={'email': 'souvenir@example.com'}
    )
    if created:
        user.set_password('testpass')
        user.save()

    # Create souvenir
    souvenir = Souvenir.objects.create(
        utilisateur=user,
        titre="Test Souvenir Creation",
        description="Testing souvenir creation functionality",
        emotion='joy',
        theme='personal',
        date_evenement='2024-01-01',
        lieu='Test Location',
        personnes_presentes='Test Person'
    )

    print(f"✓ Souvenir created: {souvenir.titre}")
    print(f"  ID: {souvenir.id}")
    print(f"  User: {souvenir.utilisateur.username}")
    print(f"  Date: {souvenir.date_evenement}")
    print(f"  Has media: {souvenir.has_media()}")
    print(f"  Needs AI: {souvenir.needs_ai_analysis()}")

def test_time_capsule():
    """Manual test for time capsule functionality"""
    print("⏰ Manual Time Capsule Test")
    print("-" * 28)

    import django
    from datetime import timedelta
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
    django.setup()

    from core.models import User, CapsuleTemporelle, Souvenir

    # Create test user
    user, created = User.objects.get_or_create(
        username='capsuletest',
        defaults={'email': 'capsule@example.com'}
    )
    if created:
        user.set_password('testpass')
        user.save()

    # Create time capsule
    future_date = timezone.now().date() + timedelta(days=30)
    capsule = CapsuleTemporelle.objects.create(
        utilisateur=user,
        titre="Test Time Capsule",
        description="A message to my future self",
        date_ouverture=future_date
    )

    # Add a souvenir to the capsule
    souvenir = Souvenir.objects.create(
        utilisateur=user,
        titre="Memory for Future",
        description="This memory will be revealed in the future",
        emotion='nostalgia',
        theme='personal',
        date_evenement=timezone.now().date()
    )
    capsule.souvenirs.add(souvenir)

    print(f"✓ Time capsule created: {capsule.titre}")
    print(f"  Open date: {capsule.date_ouverture}")
    print(f"  Days remaining: {capsule.jours_restants()}")
    print(f"  Progress: {capsule.pourcentage_progression()}%")
    print(f"  Is expired: {capsule.is_expired()}")
    print(f"  Souvenirs in capsule: {capsule.souvenirs.count()}")

def main():
    """Main test runner"""
    while True:
        show_menu()
        choice = input("Choose a test option (0-9): ").strip()

        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            success = run_smoke_test()
        elif choice == '2':
            success = run_ai_tests()
        elif choice == '3':
            success = run_view_tests()
        elif choice == '4':
            success = run_model_tests()
        elif choice == '5':
            success = run_all_tests()
        elif choice == '6':
            test_name = input("Enter AI test name (e.g., test_analyze_memory): ").strip()
            if test_name:
                success = run_specific_ai_test(test_name)
            else:
                continue
        elif choice == '7':
            test_ai_analysis_manually()
            success = True
        elif choice == '8':
            test_souvenir_creation()
            success = True
        elif choice == '9':
            test_time_capsule()
            success = True
        else:
            print("❌ Invalid choice. Please try again.")
            continue

        if choice in ['1', '2', '3', '4', '5', '6']:
            if success:
                print("✅ Test completed successfully!")
            else:
                print("❌ Test failed!")

        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()