#!/usr/bin/env python3
# Reaching Definitions using df.df_worklist
import os, sys

BRIL = os.environ.get("BRIL", os.path.expanduser("~/bril"))
sys.path.insert(0, os.path.join(BRIL, "examples"))

from df import df_worklist
from utils import parse_bril_to_function, build_cfg, print_sets

def collect_defs(blocks):
    all_defs = set()
    gen = {bname: set() for bname in blocks}
    kill = {bname: set() for bname in blocks}
    defs_by_var = {}

    for bname, instrs in blocks.items():
        for i, ins in enumerate(instrs):
            dest = ins.get("dest")
            if dest:
                d = f"{bname}:{dest}@{i}"
                gen[bname].add(d)
                all_defs.add(d)
                defs_by_var.setdefault(dest, set()).add(d)

    for bname, instrs in blocks.items():
        defined_vars = {ins.get("dest") for ins in instrs if ins.get("dest")}
        k = set()
        for v in defined_vars:
            k |= (defs_by_var.get(v, set()) - gen[bname])
        kill[bname] = k

    return gen, kill, all_defs

class RDAnalysis:
    forward = True
    init = set()
    def __init__(self, gen, kill):
        self.gen = gen
        self.kill = kill
    def merge(self, sets):
        out = set()
        for s in sets:
            out |= s
        return out
    def transfer(self, instrs, inval):
        # find block name by looking up in gen dict
        # assumption: instrs is the same list stored in blocks[bname]
        for bname, g in self.gen.items():
            if any(ins in instrs for ins in blocks[bname]):
                return self.gen[bname] | (inval - self.kill[bname])
        return inval

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 rd.py <file.bril>", file=sys.stderr)
        sys.exit(1)
    bril_text = open(sys.argv[1]).read()
    func = parse_bril_to_function(bril_text)
    global blocks
    blocks = build_cfg(func)

    gen, kill, all_defs = collect_defs(blocks)
    analysis = RDAnalysis(gen, kill)
    IN, OUT = df_worklist(blocks, analysis)

    print_sets("IN sets (Reaching Definitions)", IN)
    print_sets("OUT sets (Reaching Definitions)", OUT)

if __name__ == "__main__":
    main()
