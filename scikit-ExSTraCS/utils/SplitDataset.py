import csv
import os
import random
from typing import List, Tuple

INPUT_FILES = [
    "mpr6.csv",
    "mpr11.csv",
    "mpr20.csv",
    "mpr37.csv",
    "mpr70.csv",
    "mpr135.csv",
]

TRAIN_DIR = "train"
TEST_DIR = "test"

TRAIN_RATIO = 0.8

# Set to an int for reproducible split, or None for random each run
RANDOM_SEED = 42


def split_csv_8_2(input_path: str, train_dir: str, test_dir: str, train_ratio: float = 0.8) -> Tuple[int, int]:
    """
    Read a CSV file, shuffle rows, split into train/test by ratio,
    and save to train/<same_name> and test/<same_name>.
    """
    with open(input_path, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)  # keep header
        rows = [row for row in reader]  # data rows only

    # Shuffle before splitting
    random.shuffle(rows)

    n_total = len(rows)
    n_train = int(n_total * train_ratio)
    n_test = n_total - n_train

    base_name = os.path.basename(input_path)
    train_path = os.path.join(train_dir, base_name)
    test_path = os.path.join(test_dir, base_name)

    # Write train
    with open(train_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows[:n_train])

    # Write test
    with open(test_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows[n_train:])

    return n_train, n_test


def main():
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    os.makedirs(TRAIN_DIR, exist_ok=True)
    os.makedirs(TEST_DIR, exist_ok=True)

    for path in INPUT_FILES:
        if not os.path.exists(path):
            print(f"skip (not found): {path}")
            continue

        n_train, n_test = split_csv_8_2(path, TRAIN_DIR, TEST_DIR, TRAIN_RATIO)
        print(f"done: {path} -> {TRAIN_DIR}/{os.path.basename(path)} ({n_train}), "
              f"{TEST_DIR}/{os.path.basename(path)} ({n_test})")


if __name__ == "__main__":
    main()
