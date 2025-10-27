#!/usr/bin/env python3
"""
Quick UCI test to verify the engine works with chess GUIs
"""

import chess
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vpr_uci import main as uci_main

def test_uci_commands():
    """Test basic UCI commands"""
    print("Testing UCI interface...")
    print("You can test these commands:")
    print("  uci")
    print("  isready") 
    print("  position startpos")
    print("  go depth 4")
    print("  quit")
    print()
    print("Starting UCI engine...")
    
if __name__ == "__main__":
    test_uci_commands()
    # Run the actual UCI interface
    try:
        uci_main()
    except KeyboardInterrupt:
        print("\nUCI engine stopped.")