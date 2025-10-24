#!/usr/bin/env python
"""
Script to analyze all memories that haven't been analyzed by AI yet.
This includes memories in time capsules.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import Souvenir
from core.ai_services import AIAnalysisService

def analyze_pending_memories():
    """Analyze all memories that haven't been analyzed yet"""
    pending = Souvenir.objects.filter(ai_analyzed=False)

    if not pending.exists():
        print("✅ No memories pending analysis")
        return

    print(f"🤖 Analyzing {pending.count()} memories...")

    success_count = 0
    error_count = 0

    for souvenir in pending:
        try:
            print(f"Analyzing: {souvenir.titre}")
            AIAnalysisService.analyze_memory(souvenir)
            success_count += 1
            print(f"✅ Success: {souvenir.titre}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error analyzing {souvenir.titre}: {str(e)}")

    print(f"\n📊 Results:")
    print(f"✅ Successfully analyzed: {success_count}")
    print(f"❌ Failed: {error_count}")

if __name__ == '__main__':
    analyze_pending_memories()