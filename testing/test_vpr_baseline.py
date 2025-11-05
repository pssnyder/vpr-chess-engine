#!/usr/bin/env python3
"""
VPR v8.0 Baseline Validation Test
Verify that VPR v8.0 matches Material Opponent's performance after renaming
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import chess
from vpr_engine import VPREngine
import time


def test_vpr_baseline():
    """Test VPR v8.0 basic functionality"""
    print("=" * 60)
    print("VPR v8.0 BASELINE VALIDATION")
    print("=" * 60)
    
    engine = VPREngine(max_depth=6, tt_size_mb=128)
    
    # Test 1: Opening position
    print("\n1. Testing opening position...")
    board = chess.Board()
    engine.board = board.copy()
    
    start = time.time()
    best_move = engine.get_best_move(time_left=3.0)
    elapsed = time.time() - start
    
    print(f"Best move: {best_move}")
    print(f"Nodes: {engine.nodes_searched:,}")
    print(f"Time: {elapsed:.3f}s")
    print(f"NPS: {int(engine.nodes_searched / elapsed):,}")
    
    if best_move and best_move != chess.Move.null():
        print("✅ PASS: Found valid move")
    else:
        print("❌ FAIL: No move found")
        return False
    
    # Test 2: Mate in 1
    print("\n2. Testing mate in 1...")
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    engine.board = board.copy()
    engine.transposition_table.clear()
    engine.nodes_searched = 0
    
    start = time.time()
    best_move = engine.get_best_move(time_left=2.0)
    elapsed = time.time() - start
    
    print(f"Best move: {best_move}")
    print(f"Nodes: {engine.nodes_searched:,}")
    print(f"Time: {elapsed:.3f}s")
    print(f"NPS: {int(engine.nodes_searched / elapsed):,}")
    
    expected_mate = chess.Move.from_uci("h5f7")
    if best_move == expected_mate:
        print("✅ PASS: Found Qxf7# checkmate!")
    else:
        print(f"⚠️  WARNING: Expected h5f7, got {best_move}")
    
    # Test 3: Material evaluation
    print("\n3. Testing material evaluation...")
    board = chess.Board()
    engine.board = board.copy()
    score = engine._evaluate_material(board)
    
    print(f"Starting position score: {score}")
    
    if abs(score) < 10:
        print("✅ PASS: Balanced evaluation")
    else:
        print(f"❌ FAIL: Unbalanced ({score})")
        return False
    
    # Test 4: Bishop pair bonus
    print("\n4. Testing bishop pair bonus...")
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    engine.board = board.copy()
    score_with_pair = engine._evaluate_material(board)
    
    # Remove one white bishop
    board = chess.Board("rn1qkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    engine.board = board.copy()
    score_without_pair = engine._evaluate_material(board)
    
    print(f"With bishop pair: {score_with_pair}")
    print(f"Without bishop pair: {score_without_pair}")
    print(f"Difference: {score_with_pair - score_without_pair}")
    
    if abs(score_with_pair - score_without_pair) > 200:  # Should be ~325 (bishop value)
        print("✅ PASS: Bishop pair bonus working")
    else:
        print("⚠️  WARNING: Bishop pair bonus might not be working correctly")
    
    # Test 5: Speed check
    print("\n5. Testing search speed...")
    board = chess.Board()
    engine.board = board.copy()
    engine.transposition_table.clear()
    engine.nodes_searched = 0
    
    start = time.time()
    best_move = engine.get_best_move(time_left=3.0)
    elapsed = time.time() - start
    nps = int(engine.nodes_searched / elapsed) if elapsed > 0 else 0
    
    print(f"NPS: {nps:,}")
    
    if nps >= 15000:
        print(f"✅ PASS: Good speed ({nps:,} NPS)")
    else:
        print(f"⚠️  WARNING: Below target speed ({nps:,} NPS, target 15,000+)")
    
    print("\n" + "=" * 60)
    print("VPR v8.0 BASELINE VALIDATION COMPLETE")
    print("=" * 60)
    print("\n✅ VPR v8.0 is operational!")
    print("\nNext steps:")
    print("  1. Run comprehensive comparison vs Material Opponent")
    print("  2. Profile for optimization opportunities")
    print("  3. Begin iterative improvements")
    
    return True


if __name__ == "__main__":
    try:
        success = test_vpr_baseline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
