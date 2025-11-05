#!/usr/bin/env python3
"""
VPR v8.1 Performance Benchmark
Compare v8.1 enhancements against v8.0 baseline (17,081 NPS)
Target: <5% performance impact from new features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import chess
import time
from vpr_engine import VPREngine

def benchmark_engine(positions, time_per_move=3.0):
    """Benchmark engine on test positions"""
    engine = VPREngine()
    total_nodes = 0
    total_time = 0
    
    print(f"\nTesting {len(positions)} positions with {time_per_move}s per move...")
    
    for i, fen in enumerate(positions, 1):
        engine.board = chess.Board(fen)
        
        start = time.time()
        move = engine.get_best_move(time_per_move, 0)
        elapsed = time.time() - start
        
        nodes = engine.nodes_searched
        nps = nodes / elapsed if elapsed > 0 else 0
        
        print(f"Position {i}: {nodes:,} nodes in {elapsed:.2f}s = {nps:,.0f} NPS")
        
        total_nodes += nodes
        total_time += elapsed
    
    avg_nps = total_nodes / total_time if total_time > 0 else 0
    return total_nodes, total_time, avg_nps

def main():
    print("="*60)
    print("VPR v8.1 PERFORMANCE BENCHMARK")
    print("="*60)
    print("Testing phase awareness and trade evaluation impact")
    print("Baseline: VPR v8.0 = 17,081 NPS")
    print("Target: < 5% performance degradation (16,227+ NPS)")
    
    # Test positions covering different game phases
    test_positions = [
        chess.STARTING_FEN,  # Opening
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",  # Early opening
        "r1bq1rk1/ppp2ppp/2n2n2/3p4/3P4/2N2N2/PPP2PPP/R1BQ1RK1 w - - 0 10",  # Middlegame
        "r2q1rk1/ppp2ppp/2n5/3p4/3P4/2N5/PPP2PPP/R2Q1RK1 w - - 0 15",  # Late middlegame
        "8/5k2/8/3K4/8/8/3R4/8 w - - 0 40",  # Endgame
    ]
    
    nodes, time_taken, nps = benchmark_engine(test_positions, time_per_move=2.0)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Total nodes: {nodes:,}")
    print(f"Total time: {time_taken:.2f}s")
    print(f"Average NPS: {nps:,.0f}")
    
    baseline_nps = 17081
    diff = nps - baseline_nps
    percent = (diff / baseline_nps) * 100
    
    print(f"\nVPR v8.0 Baseline: {baseline_nps:,} NPS")
    print(f"VPR v8.1 Result: {nps:,.0f} NPS")
    print(f"Difference: {diff:+,.0f} NPS ({percent:+.2f}%)")
    
    target_nps = baseline_nps * 0.95
    if nps >= target_nps:
        print(f"\n✅ PASS: Performance within 5% target ({target_nps:,.0f}+ NPS)")
    else:
        print(f"\n❌ FAIL: Performance below 5% target ({target_nps:,.0f}+ NPS)")
    
    print("\nFeatures tested:")
    print("  - Game phase detection (opening/middlegame/endgame)")
    print("  - Static Exchange Evaluation (SEE)")
    print("  - Phase-aware time management")
    print("  - Phase-aware trade evaluation")
    print("  - Enhanced move ordering (good/bad captures)")
    
    return nps >= target_nps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
