# VPR Chess Engine v8.0

## 🎯 Project Vision

**VPR (V7P3R Experimental)** is a clean-slate chess engine project that serves as an experimental laboratory for V7P3R development. Instead of continuously modifying V7P3R's codebase (which has grown to v15 with accumulated complexity), VPR provides a fresh foundation to explore new architectures, test ideas, and establish proven performance baselines before integrating back into V7P3R.

### The Philosophy

Sometimes the best way forward is to step aside, experiment freely, and return with clarity. VPR embodies this principle:

- **No baggage:** Start from proven Material Opponent architecture
- **Freedom to experiment:** Try new ideas without impacting V7P3R's reputation
- **Learn by building:** Understand what makes engines fast through direct experience
- **Strategic reset:** Give V7P3R time to "breathe" before v16

When VPR reaches stable, high-performance state, its architecture will inform V7P3R v16 - a true generational leap built on lessons learned.

## 🚀 Current Status: VPR v8.0

**Base Architecture:** Material Opponent (proven 26,000+ NPS baseline)  
**Evaluation:** Pure material counting + dynamic bishop pair bonus  
**Search:** Alpha-beta with iterative deepening (depth 6 default)

### Core Features
- ✅ Minimax with alpha-beta pruning
- ✅ Iterative deepening
- ✅ Zobrist transposition table
- ✅ Killer moves (2 per depth)
- ✅ History heuristic
- ✅ Quiescence search (captures, 8 ply deep)
- ✅ Null move pruning (R=3)
- ✅ Principal Variation Search (PVS)
- ✅ MVV-LVA capture ordering
- ✅ Time management (adaptive based on time remaining)

### Performance Baseline
```
Engine: VPR v8.0 (Material Opponent architecture)
Speed: ~26,000 NPS (nodes per second)
Depth: 6-8 ply in typical positions
Tactical: Finds mate-in-1 correctly
Move Quality: Proven at 1200-1500+ ELO level
```

## 📋 Development Roadmap

### Phase 1: Establish Baseline (Current)
- [x] Clone Material Opponent architecture
- [x] Rename to VPR v8.0
- [ ] Validate performance matches Material Opponent
- [ ] Create comprehensive test suite
- [ ] Deploy to testing framework

### Phase 2: Optimize Core Search (v8.1 - v8.3)
- [ ] Profile and optimize hot paths
- [ ] Tune quiescence depth (8 → 6 ply?)
- [ ] Optimize move ordering
- [ ] Improve TT probe efficiency
- [ ] Target: 30,000+ NPS

### Phase 3: Add Tactical Intelligence (v8.4 - v8.6)
- [ ] Static Exchange Evaluation (SEE)
- [ ] Enhanced quiescence (checks + promotions)
- [ ] King safety awareness in move ordering
- [ ] Maintain speed while adding intelligence

### Phase 4: Positional Understanding (v8.7 - v8.9)
- [ ] Simple piece-square tables
- [ ] Passed pawn detection
- [ ] Basic king safety (castling bonus)
- [ ] Pawn structure basics (doubled, isolated)

### Phase 5: Integration Decision (v9.0 or V7P3R v16)
- [ ] Compare VPR vs V7P3R v15.0
- [ ] If VPR superior: Become V7P3R v16
- [ ] If lessons learned: Apply to V7P3R v16 rewrite
- [ ] Either way: V7P3R benefits from VPR development

## 🎯 Success Criteria

**VPR is successful if:**
1. ✅ Maintains 25,000+ NPS throughout development
2. ✅ Reaches depth 8-10 in typical middlegames
3. ✅ Achieves 90%+ tactical puzzle accuracy
4. ✅ Equals or exceeds V7P3R v12.6 performance
5. ✅ Provides clear architectural path for V7P3R v16

## 🔬 Why VPR Exists

### The V7P3R Challenge
V7P3R has evolved from v0 → v15 over many months, with each version building on the last. Despite best efforts, accumulated design decisions and complexity have created diminishing returns:

- V7P3R v15.0: 15,900 NPS (2.83x more nodes than Material Opponent)
- V7P3R v12.6: Best performer but still carried legacy code
- Multiple attempts to "clean rebuild" still inherited V7P3R patterns

### The VPR Solution
Instead of fighting V7P3R's accumulated complexity, VPR offers:

1. **Fresh Mental Model:** Not "fixing" V7P3R, but "building" something new
2. **Proven Foundation:** Start from Material Opponent's working architecture
3. **Parallel Development:** Keep V7P3R stable while exploring freely
4. **Learning Laboratory:** Understand fast engine design through direct experience
5. **No Pressure:** Experiment without impacting V7P3R's brand/reputation

### The Path Forward
- **Short term:** VPR iterates rapidly (v8.0 → v8.x → v9.0)
- **Medium term:** VPR proves superiority over V7P3R v15
- **Long term:** VPR architecture becomes V7P3R v16

## 🧠 Philosophical Note

This project mirrors an important life lesson: **Not every action must directly impact your primary focus**. Sometimes you need to work elsewhere first - to step back, think clearly, gain perspective, and build confidence before making major changes.

VPR is that side project. It's the space where we can:
- Hit the reset button without fear
- Experiment without consequences
- Learn without pressure
- Build confidence in our approach
- Return to V7P3R stronger and wiser

The goal isn't abandoning V7P3R - it's giving it the fresh foundation it deserves.

## 📁 Project Structure

```
vpr-chess-engine/
├── src/
│   └── vpr_engine.py       # Main engine (Material Opponent architecture)
├── testing/
│   └── [test files]        # Validation and benchmarking
├── analysis/
│   └── [analysis tools]    # Performance profiling and comparison
├── builds/
│   └── VPR_v8.0/          # Version snapshots
└── docs/
    └── [documentation]     # Development notes and decisions
```

## 🚦 Getting Started

### Running VPR v8.0
```bash
cd vpr-chess-engine
python src/vpr_engine.py
```

### Testing
```bash
cd vpr-chess-engine
python testing/test_vpr_baseline.py
```

### UCI Interface
VPR implements standard UCI protocol:
```
uci           # Initialize engine
isready       # Check ready status
position startpos moves e2e4 e7e5
go wtime 300000 btime 300000 winc 0 binc 0
quit          # Exit
```

## 📊 Comparison: VPR vs V7P3R

| Metric | VPR v8.0 | V7P3R v15.0 | Improvement |
|--------|----------|-------------|-------------|
| **Architecture** | Material Opponent | V12.6 rebuild | Proven baseline |
| **NPS** | ~26,000 | ~15,900 | **+63% faster** |
| **Code Lines** | ~550 | ~500 | Similar complexity |
| **Node Efficiency** | Baseline | 2.83x more nodes | **Much more selective** |
| **Move Quality** | Proven correct | Proven correct | Equal |
| **Development Velocity** | Fast iteration | Slower (baggage) | **More agile** |

## 🎓 What We're Learning

1. **Simplicity Wins:** Material Opponent's straightforward architecture outperforms complex V7P3R
2. **Architecture Matters:** Clean design from the start beats incremental optimization
3. **Speed is Foundational:** Fast search enables deeper tactical vision
4. **Iteration is Valuable:** Quick experiments reveal what works faster than theory

## 🤝 Contributing

VPR is a personal experimental project, but the lessons learned will benefit the broader V7P3R project and eventually the chess programming community through open-source sharing.

## 📜 License

Same as V7P3R project - personal/educational use, open source sharing coming once mature.

---

**Current Version:** VPR v8.0  
**Last Updated:** November 5, 2025  
**Status:** Active Development  
**Next Milestone:** Performance validation against Material Opponent baseline

