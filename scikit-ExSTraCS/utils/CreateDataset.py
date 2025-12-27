import csv
import os
import random
import tempfile
from typing import Dict, List, Tuple, Set

# For large n (37/70/135), generate this many UNIQUE samples
NUM_SAMPLES_RANDOM: Dict[int, int] = {
    37: 1000000,
    70: 2000000,
    135: 3000000,
}

# Output files for each dataset
OUTPUT_FILES: Dict[int, str] = {
    6: "mpr6.csv",
    11: "mpr11.csv",
    20: "mpr20.csv",
    37: "mpr37.csv",
    70: "mpr70.csv",
    135: "mpr135.csv",
}

# Optional: set to an int for reproducibility, or None for true randomness
RANDOM_SEED = 42

# Batch size for faster CSV writing
BATCH_SIZE = 20000

# Shuffling parameters for FULL datasets (external shuffle)
# More buckets => better mixing, more temp files.
SHUFFLE_BUCKETS = {
    6: 8,
    11: 32,
    20: 256,
}


def infer_address_bits(n_bits: int) -> int:
    """
    Infer the number of address bits 'a' for an n-bit multiplexer:
        n = a + 2^a
    Returns a if valid, otherwise raises ValueError.
    """
    for a in range(1, 32):
        if a + (1 << a) == n_bits:
            return a
    raise ValueError(f"Invalid multiplexer length: {n_bits}. Expect n = a + 2^a.")


def compute_class_from_int(i: int, n_bits: int, a: int) -> int:
    """
    Compute the multiplexer class bit from an integer bit-pattern i (0..2^n-1),
    where bits are interpreted as MSB-first for X0..X(n-1).

    Address bits: X0..X(a-1) (X0 is MSB)
    Data bits   : X(a)..X(n-1)
    Class = data_bits[address]
    """
    addr = 0
    for j in range(a):
        bit = (i >> (n_bits - 1 - j)) & 1
        addr = (addr << 1) | bit

    pos = a + addr
    y = (i >> (n_bits - 1 - pos)) & 1
    return y


def int_to_bits_msb_first(i: int, n_bits: int) -> List[int]:
    """Convert integer i to a list of n_bits bits (MSB-first)."""
    return [(i >> (n_bits - 1 - j)) & 1 for j in range(n_bits)]


def write_header(writer: csv.writer, n_bits: int) -> None:
    """Write CSV header: X0..X(n-1),Class"""
    header = [f"X{i}" for i in range(n_bits)] + ["Class"]
    writer.writerow(header)


def external_shuffle_full_dataset(n_bits: int, out_file: str, buckets: int) -> None:
    """
    Generate FULL dataset (2^n rows) and shuffle it using a bucket-based external shuffle:
      1) Stream-generate rows and randomly dispatch them into bucket temp files.
      2) Randomize bucket order.
      3) Load each bucket into memory, shuffle, and write to final CSV.

    This keeps memory usage bounded and works well for n=20 (1,048,576 rows).
    """
    a = infer_address_bits(n_bits)
    total = 1 << n_bits

    # Create temp directory and bucket files
    tmp_dir = tempfile.mkdtemp(prefix=f"mux{n_bits}_shuffle_")
    bucket_paths = [os.path.join(tmp_dir, f"bucket_{k}.csv") for k in range(buckets)]
    bucket_files = [open(p, "w", newline="") for p in bucket_paths]
    bucket_writers = [csv.writer(f) for f in bucket_files]

    try:
        # 1) Dispatch rows into buckets
        batch = []
        for i in range(total):
            x_bits = int_to_bits_msb_first(i, n_bits)
            y = compute_class_from_int(i, n_bits, a)
            row = x_bits + [y]

            b = random.randrange(buckets)
            batch.append((b, row))

            if len(batch) >= BATCH_SIZE:
                for b_idx, r in batch:
                    bucket_writers[b_idx].writerow(r)
                batch.clear()

        if batch:
            for b_idx, r in batch:
                bucket_writers[b_idx].writerow(r)
            batch.clear()

        # Close bucket files so we can read them
        for f in bucket_files:
            f.close()

        # 2) Write final output, shuffling bucket order and rows inside each bucket
        bucket_order = list(range(buckets))
        random.shuffle(bucket_order)

        with open(out_file, "w", newline="") as out_f:
            out_writer = csv.writer(out_f)
            write_header(out_writer, n_bits)

            written = 0
            for b_idx in bucket_order:
                path = bucket_paths[b_idx]
                if not os.path.exists(path) or os.path.getsize(path) == 0:
                    continue

                with open(path, "r", newline="") as in_f:
                    reader = csv.reader(in_f)
                    rows = [row for row in reader]  # bucket-sized in memory
                random.shuffle(rows)
                out_writer.writerows(rows)
                written += len(rows)

        print(f"done (FULL SHUFFLED): {out_file} | n_bits={n_bits} | rows={written}")

    finally:
        # Cleanup temp files/dir
        for f in bucket_files:
            try:
                f.close()
            except Exception:
                pass
        for p in bucket_paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass


def generate_mux_sample_random(n_bits: int) -> Tuple[List[int], int]:
    """
    Generate one random sample for n-bit multiplexer.
    Layout:
      X0..X(a-1) are address bits (X0 is MSB), X(a)..X(n-1) are data bits.
    """
    a = infer_address_bits(n_bits)
    bits = [random.randint(0, 1) for _ in range(n_bits)]

    addr = 0
    for j in range(a):
        addr = (addr << 1) | bits[j]

    y = bits[a + addr]
    return bits, y


def generate_unique_random_dataset(n_bits: int, n_samples: int, max_attempt_factor: int = 50) -> List[Tuple[List[int], int]]:
    """Generate a UNIQUE random dataset (rows unique by X + Class)."""
    max_unique = 1 << n_bits
    target = min(n_samples, max_unique)

    seen: Set[Tuple[int, ...]] = set()
    rows: List[Tuple[List[int], int]] = []

    max_attempts = target * max_attempt_factor
    attempts = 0

    while len(rows) < target and attempts < max_attempts:
        attempts += 1
        x_bits, y = generate_mux_sample_random(n_bits)
        key = tuple(x_bits + [y])
        if key not in seen:
            seen.add(key)
            rows.append((x_bits, y))

    if len(rows) < target:
        raise RuntimeError(
            f"Could not generate enough unique samples for n={n_bits}. "
            f"Requested {target}, got {len(rows)} after {attempts} attempts."
        )

    return rows


def save_random_dataset(n_bits: int, out_file: str, rows: List[Tuple[List[int], int]]) -> None:
    """Save random rows to CSV."""
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        write_header(writer, n_bits)
        for x_bits, y in rows:
            writer.writerow(x_bits + [y])
    print(f"done (RANDOM UNIQUE): {out_file} | n_bits={n_bits} | rows={len(rows)}")


def main():
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    # FULL + SHUFFLED datasets for 6/11/20
    for n_bits in (6, 11, 20):
        external_shuffle_full_dataset(n_bits, OUTPUT_FILES[n_bits], SHUFFLE_BUCKETS[n_bits])

    # Random unique datasets for 37/70/135
    for n_bits in (37, 70, 135):
        rows = generate_unique_random_dataset(n_bits, NUM_SAMPLES_RANDOM[n_bits])
        save_random_dataset(n_bits, OUTPUT_FILES[n_bits], rows)


if __name__ == "__main__":
    main()
