#!/usr/bin/env python
"""
Debug script to check time capsules and their AI analysis status
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import CapsuleTemporelle, Souvenir

def debug_capsules():
    """Debug time capsules and their analysis status"""
    capsules = CapsuleTemporelle.objects.all()

    if not capsules.exists():
        print("❌ No time capsules found")
        return

    print(f"📦 Found {capsules.count()} time capsules:")

    for capsule in capsules:
        print(f"\n🕰️ Capsule: {capsule.souvenir.titre}")
        print(f"   Opened: {capsule.is_opened}")
        print(f"   Memory AI analyzed: {capsule.souvenir.ai_analyzed}")

        if hasattr(capsule.souvenir, 'analyse_ia'):
            analyse = capsule.souvenir.analyse_ia
            print(f"   Has AI analysis object: ✅")
            print(f"   Emotion (text): {analyse.emotion_texte}")
            print(f"   Emotion (image): {analyse.emotion_image}")
            print(f"   Confidence (text): {analyse.score_emotion_texte}")
            print(f"   Global confidence: {analyse.confiance_globale}")
            print(f"   Keywords: {analyse.mots_cles}")
            print(f"   Summary: {analyse.resume_genere[:100] if analyse.resume_genere else 'None'}...")
        else:
            print(f"   Has AI analysis object: ❌")

if __name__ == '__main__':
    debug_capsules()