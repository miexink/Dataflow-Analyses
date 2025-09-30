# Data Flow Analyses (Worklist) 

This project implements two classic dataflow analyses for Bril, using the official
generic worklist driver from `examples/df.py` in the Bril repository.

## Implemented Analyses
1. **Reaching Definitions (RD)**  
   - Direction: Forward  
   - Kind: May analysis  
   - Domain: Sets of definition IDs (`block:var@index`)  
   - Init: ∅ (empty set)  
   - Merge: Union of predecessor OUT sets  
   - Transfer: `OUT[B] = GEN[B] ∪ (IN[B] − KILL[B])`

2. **Available Expressions (AE)**  
   - Direction: Forward  
   - Kind: Must analysis  
   - Domain: Sets of binary expressions `(op, (arg1,arg2))`  
   - Init: Universe of all expressions in the function  
   - Merge: Intersection of predecessor OUT sets  
   - Transfer: `OUT[B] = (IN[B] − KILL[B]) ∪ GEN[B]`

## How It Works
- We parse Bril programs with `bril2json` (CLI or `$BRIL/tools/bril2json.py`).
- We build basic blocks with `form_blocks` from the Bril repo.  
- To satisfy `cfg.edges`, each block is guaranteed to end with a terminator
  (`br`, `jmp`, `ret`); if one is missing, we insert an explicit fallthrough `jmp`.
- We then call `df.df_worklist(blocks, analysis)` where `analysis` is a class
  that defines:
  - `forward` (bool),
  - `init` (initial lattice element),
  - `merge(pred_outs)`,
  - `transfer(block_instrs, inval)`.

## Running the Analyses
From this folder:

```bash
export BRIL=$HOME/bril
export PYTHONPATH=$BRIL/examples:$PYTHONPATH

# Reaching Definitions
python3 rd.py test/mini1.bril
python3 rd.py test/mini2.bril

# Available Expressions
python3 ae.py test/mini1.bril
python3 ae.py test/mini2.bril
