import sys
import os
import time
from datetime import datetime

# Ensure the parent directory is in sys.path so that `skExSTraCS` can be imported
# when running this script directly.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, PROJECT_ROOT)


from skExSTraCS import ExSTraCS, StringEnumerator

# Set your dataset root here (cross-platform friendly path join will be used later)
# data_path = os.path.join(os.getcwd(), "datasets", "mpr")
data_path = r"/mnt/d/datasets/mpr"

DEFAULTS = {
    "index": 0,
    "dataset": "mpr11",
    "learning_iterations": 10000,
    "N": 1000,
    "p_spec": 0.66,
    "level": 2,
    "use_tl": 1,
}


def parse_args_all_or_nothing(argv):
    """
    All-or-nothing argument parsing:

    - If no extra CLI args are provided, use DEFAULTS.
      Example: python test_ExSTraCS_CMD.py

    - If any CLI args are provided, require exactly 6 parameters:
      index dataset learning_iterations N p_spec level
      Example: python test_ExSTraCS_CMD.py 0 mpr6 100000 500 0.66 1

    This avoids mixing defaults with partial user-provided args.
    """
    if len(argv) == 1:
        return (
            DEFAULTS["index"],
            DEFAULTS["dataset"],
            DEFAULTS["learning_iterations"],
            DEFAULTS["N"],
            DEFAULTS["p_spec"],
            DEFAULTS["level"],
            DEFAULTS["use_tl"],
        )

    # script name + 7 args = 8 items in argv
    if len(argv) != 8:
        raise ValueError(
            "Invalid arguments.\n"
            "Use either:\n"
            "  python test_ExSTraCS_CMD.py\n"
            "or:\n"
            "  python test_ExSTraCS_CMD.py index dataset learning_iterations N p_spec level use_tl\n"
            "Example:\n"
            "  python test_ExSTraCS_CMD.py 0 mpr6 100000 500 0.66 1 0"
        )

    index = int(argv[1])
    dataset = argv[2]
    learning_iterations = int(argv[3])
    N = int(argv[4])
    p_spec = float(argv[5])
    level = int(argv[6])
    use_tl = int(argv[7])

    return index, dataset, learning_iterations, N, p_spec, level, use_tl


def main():
    start_ts = time.time()

    index, dataset, learning_iterations, N, p_spec, level, use_tl = parse_args_all_or_nothing(sys.argv)

    print("index:", index)
    print("dataset:", dataset)
    print("learning_iterations:", learning_iterations)
    print("N:", N)
    print("p_spec:", p_spec)
    print("level:", level)
    print("use_tl:", use_tl)

    file_name = dataset + ".csv"
    train_file = os.path.join(data_path, "train", file_name)
    test_file = os.path.join(data_path, "test", file_name)

    # Early checks for clearer errors
    if not os.path.exists(train_file):
        raise FileNotFoundError(f"Train file not found: {train_file}")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")

    # Cross-platform log directory: MetaData/ExpRes/<index>/
    log_dir = "../MetaData/ExpRes/"+str(index)+"/"
    os.makedirs(log_dir, exist_ok=True)

    log_trainingfile_name = (
        f"log_training_-test_{index}_{dataset}_{learning_iterations}_{N}_{p_spec}_L{level}_{use_tl}.txt"
    )

    # Load training data
    train_converter = StringEnumerator(train_file, 'Class')
    _, _, train_dataFeatures, train_dataPhenotypes = train_converter.get_params()

    # Train
    model = ExSTraCS(
        learning_iterations=learning_iterations,
        N=N,
        p_spec=p_spec,
        level=level,
        use_tl=0,
        index = index,
        log_dir=log_dir,
        log_trainingfile_name=log_trainingfile_name
    )

    print("Model training in progress ...")
    train_start = datetime.now()
    print("Training start:", train_start.strftime("%Y-%m-%d %H:%M:%S"))

    model.fit(train_dataFeatures, train_dataPhenotypes)

    train_end = datetime.now()
    print("Model training Ends")
    print("Training end:", train_end.strftime("%Y-%m-%d %H:%M:%S"))
    print("Training duration:", str(train_end - train_start))

    # Load test data
    test_converter = StringEnumerator(test_file, 'Class')
    _, _, test_dataFeatures, test_dataPhenotypes = test_converter.get_params()

    # Evaluate
    accuracy = model.score(test_dataFeatures, test_dataPhenotypes)
    elapsed = time.time() - start_ts
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"Elapsed time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    print("End time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if use_tl == 1:
        os.makedirs("../MetaData/"+str(index), exist_ok=True)
        filename = "../MetaData/"+str(index)+"/"+dataset +  "_export.csv"
        model.export_final_rule_population(filename=filename)


if __name__ == "__main__":
    main()
