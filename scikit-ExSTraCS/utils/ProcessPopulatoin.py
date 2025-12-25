import re
import pandas as pd

# ====== 1) Load your population CSV ======
csv_path = r"../test/mpr6_export6.csv"
df = pd.read_csv(csv_path)

# ====== 2) Auto-detect key column names (compatible with different export formats) ======
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
    cond_col = cols[0]  # Fallback to the first column if nothing matches

# Force numeric conversion (avoid mean() failure due to strings)
for c in [fitness_col, acc_col, match_col]:
    if c is not None:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ====== 3) Select "good classifiers"
# Criteria (as requested):
#   fitness > population average fitness
#   accurate & experienced: Accuracy > average Accuracy AND MatchCount > average MatchCount
# ======
avg_fit = df[fitness_col].mean(skipna=True)
avg_acc = df[acc_col].mean(skipna=True)
avg_mc  = df[match_col].mean(skipna=True)

good = df[
    (df[fitness_col] > avg_fit) &
    (df[acc_col] > avg_acc) &
    (df[match_col] > avg_mc)
].copy()

# ====== 4) Extract CFs: remove dc, deduplicate, remove single-node fragments (e.g., "D16") ======
bracket_pat = re.compile(r"\[(.*?)\]")
single_node_pat = re.compile(r"^D\d+$", re.IGNORECASE)  # Single-node: D + number

seen = set()
cf_list = []

for cell in good[cond_col].astype(str):
    # Condition is usually like [cf][dc][cf]...
    frags = bracket_pat.findall(cell)
    if not frags:
        # If not in bracketed format, treat the whole cell as one fragment (optional)
        frags = [cell]

    for frag in frags:
        frag = frag.strip()
        if not frag:
            continue
        if frag.lower() == "dc":
            continue
        if single_node_pat.fullmatch(frag):  # Remove single-node CF
            continue
        if frag not in seen:
            seen.add(frag)
            cf_list.append(frag)

# ====== 5) Output: single column, no header ======
out_path = r"../MetaData/CF_L1.csv"  # .csv is fine
pd.Series(cf_list).to_csv(out_path, index=False, header=False, encoding="utf-8")

print("selected classifiers:", len(good))
print("final CF count:", len(cf_list))
print("saved to:", out_path)
