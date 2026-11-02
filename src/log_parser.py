
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_fio_log(file_path, metric_name):
    """
    Parse a fio time-series log file.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Log file not found: {file_path}"
        )

    df = pd.read_csv(
        file_path,
        header=None
    )

    df.columns = [
        "time_ms",
        metric_name,
        "direction",
        "block_size",
        "offset"
    ]

    return df


def parse_all_logs(data_dir):
    """
    Parse IOPS, bandwidth and completion latency logs
    from a specified benchmark directory.
    """

    data_dir = Path(data_dir)

    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir

    log_files = {
        "iops": data_dir / "sample_iops.1.log",
        "bw_kib_s": data_dir / "sample_bw.1.log",
        "clat_ns": data_dir / "sample_clat.1.log"
    }

    log_data = {}

    for key, file_path in log_files.items():
        metric_name = {
            "iops": "iops",
            "bw_kib_s": "bw_kib_s",
            "clat_ns": "clat_ns"
        }[key]

        log_data[key] = parse_fio_log(
            file_path,
            metric_name
        )

    return log_data
