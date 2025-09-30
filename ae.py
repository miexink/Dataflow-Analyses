#!/usr/bin/env python3
# Available Expressions using df.df_worklist
import os, sys

BRIL = os.environ.get("BRIL", os.path.expanduser("~/bril"))
sys.path.insert(0, os.path.join(BRIL, "examples"))

from df import df_worklist
from utils import parse_bril_to_function, build_cfg, expressions_in_block, print_sets

def collect_expr_gen_kill(blocks):
    universe = set()
    gen = {}
    kill = {}

    for bname, instrs in blocks.items():
        g = expressions_in_block(instrs)
        gen[bname] = g
        universe |= g

    for bname, instrs in blocks.items():
        defined = {ins["dest"] for ins in instrs if ins.get("dest")}
        k = set()
        for (op, args) in universe:
            if any(v in defined for v in args):
                k.add((op, args))
        kill[bname] = k

    return gen, kill, universe

class AEAnalysis:
    forward = True
    def __init__(self, gen, kill, universe):
        self.gen = gen
        self.kill = kill
        self.universe = universe
        self.init = set(universe)
    def merge(self, sets):
        it = iter(sets)
        try:
            acc = set(next(it))
        except StopIteration:
            return set(self.universe)
        for s in it:
            acc &= s
        return acc
    def transfer(self, instrs, inval):
        for bname, g in self.gen.items():
            if any(ins in instrs for ins in blocks[bname]):
                return (inval - self.kill[bname]) | self.gen[bname]
        return inval

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ae.py <file.bril>", file=sys.stderr)
        sys.exit(1)
    bril_text = open(sys.argv[1]).read()
    func = parse_bril_to_function(bril_text)
    global blocks
    blocks = build_cfg(func)

    gen, kill, universe = collect_expr_gen_kill(blocks)
    analysis = AEAnalysis(gen, kill, universe)
    IN, OUT = df_worklist(blocks, analysis)

    def fmt(m):
        return {b: set(f"{op}({a1},{a2})" for (op,(a1,a2)) in s) for b,s in m.items()}

    print_sets("IN sets (Available Expressions)", fmt(IN))
    print_sets("OUT sets (Available Expressions)", fmt(OUT))

if __name__ == "__main__":
    main()
