#!/usr/bin/env python3

import sys
import os
import argparse

# Parsuj argumenty wiersza poleceń
parser = argparse.ArgumentParser(description="CosmicAnalyzer - Aplikacja do przeglądania i analizy danych naukowych")
parser.add_argument('--headless', action='store_true', help='Uruchom w trybie bez graficznego interfejsu (np. dla środowiska Replit)')
parser.add_argument('--gui', action='store_true', help='Wymuś uruchomienie w trybie GUI, nawet w środowiskach bez wyświetlania')

args = parser.parse_args()

# Określ tryb wyświetlania
is_replit = os.environ.get('REPL_ID') is not None
use_gui = args.gui or (not is_replit and not args.headless)

# Ustaw zmienne środowiskowe dla backendu PyQt przed importem
if not use_gui:
    print("Uruchamianie w trybie offscreen (bez GUI)...")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
else:
    print("Uruchamianie w trybie GUI...")

from app import CosmicAnalyzerApp

if __name__ == "__main__":
    app = CosmicAnalyzerApp(sys.argv)
    sys.exit(app.exec_())
