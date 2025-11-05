# VPR v8.0 Launch Plan

**Date:** November 5, 2025  
**Status:** ✅ Operational  
**Purpose:** Document the transition from V7P3R v15 development to VPR v8.0 experimentation

---

## 🎯 Mission Statement

VPR v8.0 provides a clean experimental space to explore chess engine architecture without the accumulated complexity of V7P3R v0-v15. Starting from Material Opponent's proven foundation, VPR will iterate rapidly to discover optimal performance patterns before potentially becoming V7P3R v16.

---

## ✅ Phase 1: Foundation (COMPLETE)

### What We Did
- [x] Copied Material Opponent code → `vpr_engine.py`
- [x] Renamed all classes and references to VPR
- [x] Verified code compiles and runs
- [x] Created comprehensive README documenting the vision
- [x] Established baseline test suite
- [x] Validated performance: 17,000+ NPS ✅

### Key Results
```
Opening Position: 17,081 NPS, 4,506 nodes in 0.264s
Mate in 1: Found h5f7# correctly (20,780 NPS)
Material Eval: Balanced (0 centipawns in starting position)
Bishop Pair: Working correctly (+50 bonus detected)
```

### Files Created
- `src/vpr_engine.py` - Main engine (Material Opponent architecture)
- `testing/test_vpr_baseline.py` - Validation test
- `README.md` - Comprehensive project documentation
- `docs/VPR_v8_0_LAUNCH_PLAN.md` - This file

---

## 📋 Phase 2: Performance Validation (NEXT)

### Objectives
1. **Direct comparison with Material Opponent**
   - Run identical test positions
   - Verify NPS matches (~26,000 target)
   - Confirm node counts are similar
   - Validate move quality agreement

2. **Establish regression test suite**
   - Tactical positions (mate in 1, 2, 3)
   - Strategic positions (opening, middlegame, endgame)
   - Performance benchmarks (speed, depth, nodes)
   - Create automated test harness

3. **Profile for optimization opportunities**
   - Identify hot paths (most time spent)
   - Measure function call overhead
   - Check TT efficiency
   - Analyze move ordering effectiveness

### Expected Timeline
- **Week 1:** Complete performance validation
- **Week 2:** Establish regression suite
- **Week 3:** Initial profiling and optimization plan

---

## 🚀 Phase 3: Iterative Optimization (v8.1 - v8.3)

### Target Improvements
1. **Speed Optimization**
   - Goal: 30,000+ NPS (from current ~17,000)
   - Optimize TT probe/store operations
   - Streamline move ordering
   - Reduce function call overhead

2. **Search Efficiency**
   - Reduce nodes explored (currently on par with Material Opponent)
   - Tune quiescence depth (8 → 6 ply?)
   - Optimize LMR parameters
   - Improve null move pruning effectiveness

3. **Time Management**
   - Validate adaptive time allocation
   - Test various time controls
   - Ensure no time pressure issues

### Success Criteria
- [ ] 30,000+ NPS achieved
- [ ] Node count ≤ Material Opponent
- [ ] Depth 8 reached in 3s on standard positions
- [ ] No regression in move quality

---

## 🧠 Phase 4: Tactical Intelligence (v8.4 - v8.6)

### Features to Add
1. **Static Exchange Evaluation (SEE)**
   - Evaluate capture sequences
   - Avoid examining losing captures
   - Improve move ordering efficiency

2. **Enhanced Quiescence**
   - Add checks to forcing moves
   - Include pawn promotions
   - Consider threatened piece escapes (when behind)

3. **King Safety Awareness**
   - Detect exposed king positions
   - Penalize reckless attacks
   - Reward defensive moves when appropriate

### Success Criteria
- [ ] Tactical puzzle accuracy > 90%
- [ ] Speed maintained > 25,000 NPS
- [ ] Depth maintained or improved
- [ ] Clear improvement in tactical positions

---

## 🏰 Phase 5: Positional Understanding (v8.7 - v8.9)

### Features to Add
1. **Piece-Square Tables**
   - Center control bonuses (pawns, knights)
   - Piece activity rewards
   - Endgame king centralization

2. **Pawn Structure**
   - Passed pawn detection
   - Doubled pawn penalty
   - Isolated pawn penalty
   - Pawn chains evaluation

3. **Simple King Safety**
   - Castling bonus
   - Pawn shield evaluation
   - Open file danger

### Success Criteria
- [ ] Positional play improved
- [ ] Opening moves more principled
- [ ] Endgame technique enhanced
- [ ] Speed maintained > 20,000 NPS

---

## 🎓 Phase 6: Integration Decision (v9.0 or V7P3R v16)

### Decision Criteria

**Option A: VPR Becomes V7P3R v16**
- VPR surpasses V7P3R v15 in all metrics
- Clean architecture proven sustainable
- Community ready for V7P3R "reboot"
- Timeline: Rename VPR v9.0 → V7P3R v16.0

**Option B: VPR Lessons Applied to V7P3R v16**
- VPR experiments reveal key insights
- V7P3R v16 built with VPR lessons but fresh code
- Both engines maintained temporarily
- Timeline: VPR informs new V7P3R v16 architecture

**Option C: Parallel Development Continues**
- VPR and V7P3R serve different purposes
- VPR = performance/tournament engine
- V7P3R = experimental/learning platform
- Timeline: Indefinite parallel development

### Evaluation Metrics
| Metric | VPR v9.0 Target | V7P3R v15.0 Current |
|--------|-----------------|---------------------|
| NPS | 30,000+ | 15,900 |
| Depth (3s) | 8-10 ply | 6-8 ply |
| Tactical Accuracy | 90%+ | Unknown |
| Tournament ELO | 1400+ | ~1200 (estimated) |
| Code Maintainability | Clean | Complex |

---

## 📊 Comparison: VPR v8.0 vs V7P3R v15.0

### Current Status (November 5, 2025)

| Aspect | VPR v8.0 | V7P3R v15.0 | Winner |
|--------|----------|-------------|--------|
| **Architecture** | Material Opponent | V12.6 rebuild | VPR ✅ |
| **Code Base** | 550 lines | 500 lines | Similar |
| **NPS** | ~17,000 | ~15,900 | VPR ✅ |
| **Node Efficiency** | Baseline | 2.83x worse | VPR ✅ |
| **Move Quality** | Proven | Proven | Tie |
| **Development Velocity** | Fast (clean) | Slow (baggage) | VPR ✅ |
| **Tactical Puzzles** | Mate-in-1 ✅ | Mate-in-1 ✅ | Tie |
| **Code Clarity** | Excellent | Good | VPR ✅ |

**Verdict:** VPR v8.0 already shows advantages even before optimization

---

## 🎯 Success Metrics

### Must Achieve (Critical)
- [ ] 25,000+ NPS sustained
- [ ] Depth 8 in typical 3s search
- [ ] 90%+ tactical accuracy
- [ ] No time management issues
- [ ] Tournament ready (1400+ ELO)

### Should Achieve (Important)
- [ ] 30,000+ NPS
- [ ] Depth 10 possible in 5s search
- [ ] Positional understanding demonstrated
- [ ] Beats V7P3R v15 head-to-head
- [ ] Clean code maintained throughout

### Could Achieve (Nice to Have)
- [ ] 35,000+ NPS
- [ ] Advanced heuristics integrated
- [ ] Multiple evaluation modes
- [ ] Opening book support
- [ ] Endgame tablebase integration

---

## 🧭 Guiding Principles

1. **Speed First:** Never sacrifice search speed for complex heuristics
2. **Test Everything:** Every change validated with benchmarks
3. **Iterate Quickly:** Small, measurable improvements over big rewrites
4. **Learn Constantly:** Document what works and what doesn't
5. **Stay Clean:** Resist complexity creep that plagued V7P3R
6. **Be Patient:** VPR is a journey, not a sprint
7. **Have Fun:** This is an experiment - enjoy the process

---

## 📝 Development Log

### November 5, 2025 - VPR v8.0 Launch
- ✅ Copied Material Opponent architecture
- ✅ Renamed to VPR v8.0
- ✅ Validated baseline functionality
- ✅ Performance: 17,000 NPS (below Material Opponent's 26,000 but functional)
- ✅ Created comprehensive documentation
- 🎯 Next: Direct comparison with Material Opponent to understand NPS difference

### Pending Items
- [ ] Compare VPR v8.0 vs Material Opponent side-by-side
- [ ] Identify why VPR is slower (17k vs 26k NPS)
- [ ] Create regression test suite
- [ ] Begin optimization planning

---

## 🤝 Acknowledgments

VPR v8.0 is built on the foundation of:
- **Material Opponent:** Original architecture and proven performance
- **V7P3R v0-v15:** Lessons learned from extensive development
- **V12.6:** Best V7P3R performer, inspiration for time management
- **The Chess Programming Community:** Collective wisdom on engine design

---

**Status:** ✅ VPR v8.0 Operational  
**Next Milestone:** Performance parity with Material Opponent  
**Long-term Goal:** Become V7P3R v16 foundation or inform its design
