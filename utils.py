# utils.py — helpers for dataflow analyses
from typing import Dict, Set, Tuple, List, Any
import json, subprocess, os, shutil, sys

BRIL = os.environ.get("BRIL", os.path.expanduser("~/bril"))
if os.path.isdir(os.path.join(BRIL, "examples")):
    sys.path.insert(0, os.path.join(BRIL, "examples"))

from form_blocks import form_blocks

def _run(cmd: list, stdin: bytes = None) -> bytes:
    return subprocess.check_output(cmd, input=stdin)

def _find_bril2json() -> list:
    cli = shutil.which("bril2json")
    if cli:
        return [cli]
    candidate = os.path.join(BRIL, "tools", "bril2json.py")
    if os.path.exists(candidate):
        return ["python3", candidate]
    raise RuntimeError("Can't find bril2json. Install it or set $BRIL to the repo root.")

def parse_bril_to_function(bril_text: str) -> Dict[str, Any]:
    br2json = _find_bril2json()
    prog = json.loads(_run(br2json, stdin=bril_text.encode()))
    if not prog.get("functions"):
        raise RuntimeError("No functions found in input.")
    return prog["functions"][0]

def build_cfg(func_json: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Return blocks dict expected by df_worklist/cfg.edges:
    {blockname: [instrs...]} including label instrs,
    and ensure each block ends in a terminator.
    """
    raw_blocks = form_blocks(func_json["instrs"])
    blocks = {}
    names = []

    # assign names
    for i, block in enumerate(raw_blocks):
        if block and "label" in block[0]:
            name = block[0]["label"]
        else:
            name = "entry" if i == 0 else f".B{i}"
        blocks[name] = block
        names.append(name)

    # patch missing terminators with fallthrough jmp
    for i, name in enumerate(names):
        instrs = blocks[name]
        if not instrs:
            continue
        last = instrs[-1]
        if last.get("op") not in ("br", "jmp", "ret"):
            if i + 1 < len(names):
                succ = names[i + 1]
                instrs.append({"op": "jmp", "labels": [succ]})
                blocks[name] = instrs

    return blocks


def expressions_in_block(instrs: List[Dict[str, Any]]) -> Set[Tuple[str, Tuple[str, ...]]]:
    exprs = set()
    for ins in instrs:
        if "op" not in ins:
            continue
        op = ins["op"]
        args = ins.get("args", [])
        dest = ins.get("dest")
        if op in {"add","sub","mul","div","eq","lt","gt","le","ge"} and len(args) == 2 and dest:
            exprs.add((op, tuple(args)))
    return exprs

def print_sets(header: str, mapping):
    print(header)
    for b, s in mapping.items():
        pretty = ", ".join(sorted(map(str, s)))
        print(f"  {b}: {{{pretty}}}")
    print()
