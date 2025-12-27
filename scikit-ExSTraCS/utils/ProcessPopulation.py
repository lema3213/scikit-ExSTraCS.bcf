import re
import pandas as pd
import os
import sys

# ====== 0) Dataset parameter ======
# Usage: python script.py mpr6
import sys
if len(sys.argv) < 3:
    raise ValueError("Usage: python script.py <index> <dataset>")

INDEX = int(sys.argv[1])   # index
DATASET = sys.argv[2]      # dataset
BASE_DIR = r"../MetaData/"+sys.argv[1]
os.makedirs(BASE_DIR, exist_ok=True)

# mpr* -> level
LEVEL_MAP = {"mpr6":1,"mpr11":2,"mpr20":3,"mpr37":4,"mpr70":5,"mpr135":6}
if DATASET not in LEVEL_MAP:
    raise ValueError(f"Unknown dataset: {DATASET}")
LEVEL = LEVEL_MAP[DATASET]

# ====== 1) Load your population CSV ======
csv_path = os.path.join(BASE_DIR, f"{DATASET}_export.csv")
df = pd.read_csv(csv_path)

cols = list(df.columns)

def pick_col(prefer_names=(), contains_all=()):
    for n in prefer_names:
        if n in df.columns:
            return n
    for c in cols:
        cl = c.lower()
        if all(k.lower() in cl for k in contains_all):
            return c
    return None

cond_col    = pick_col(prefer_names=("Specified Values", "Code Fragments", "Condition"))
fitness_col = pick_col(prefer_names=("Fitness",), contains_all=("fitness",))
acc_col     = pick_col(prefer_names=("Accuracy",), contains_all=("accuracy",))
match_col   = pick_col(prefer_names=("Match Count",), contains_all=("match", "count"))

if cond_col is None:
    cond_col = cols[0]

for c in [fitness_col, acc_col, match_col]:
    if c is not None:
        df[c] = pd.to_numeric(df[c], errors="coerce")

avg_fit = df[fitness_col].mean(skipna=True)
avg_acc = df[acc_col].mean(skipna=True)
avg_mc  = df[match_col].mean(skipna=True)

good = df[
    (df[fitness_col] > avg_fit) &
    (df[acc_col] > avg_acc) &
    (df[match_col] > avg_mc)
].copy()

bracket_pat = re.compile(r"\[(.*?)\]")
single_node_pat = re.compile(r"^D\d+$", re.IGNORECASE)

seen = set()
cf_list = []

for cell in good[cond_col].astype(str):
    frags = bracket_pat.findall(cell) or [cell]
    for frag in frags:
        frag = frag.strip()
        if not frag:
            continue
        if frag.lower() == "dc":
            continue
        if single_node_pat.fullmatch(frag):
            continue
        if frag not in seen:
            seen.add(frag)
            cf_list.append(frag)

# ====== 5) Output: CF_L{LEVEL}.csv ======
out_path = os.path.join(BASE_DIR, f"CF_L{LEVEL}.csv")
pd.Series(cf_list).to_csv(out_path, index=False, header=False, encoding="utf-8")

print("dataset:", DATASET, "level:", LEVEL)
print("input:", csv_path)
print("selected classifiers:", len(good))
print("final CF count:", len(cf_list))
print("saved to:", out_path)
