#!/usr/bin/env python3
"""
Simple test to check if we can communicate with V7P3R engine
"""

import chess
import chess.engine
import sys
import os

def test_v7p3r_communication():
    """Test basic communication with V7P3R"""
    v7p3r_path = "V7P3R_v12.6.exe"
    
    if not os.path.exists(v7p3r_path):
        print(f"❌ Could not find {v7p3r_path}")
        print("Please make sure V7P3R_v12.6.exe is in the current directory")
        return False
    
    try:
        print(f"Testing communication with {v7p3r_path}...")
        
        with chess.engine.SimpleEngine.popen_uci(v7p3r_path) as engine:
            print(f"✅ Engine connected: {engine.id}")
            
            # Test a simple position
            board = chess.Board()
            print(f"Testing position: {board.fen()}")
            
            # Get a move
            result = engine.play(board, chess.engine.Limit(time=1.0))
            print(f"✅ Engine move: {result.move}")
            
            # Test analysis
            info = engine.analyse(board, chess.engine.Limit(time=1.0))
            score = info.get('score')
            depth = info.get('depth', 0)
            nodes = info.get('nodes', 0)
            pv = info.get('pv', [])
            
            print(f"✅ Analysis complete:")
            print(f"  Score: {score}")
            print(f"  Depth: {depth}")
            print(f"  Nodes: {nodes}")
            print(f"  PV: {' '.join(str(move) for move in pv[:5])}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error communicating with engine: {e}")
        return False

if __name__ == "__main__":
    test_v7p3r_communication()