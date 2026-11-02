
import json
from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "benchmark_01"


def parse_fio_json(file_path):
    """
    Parse a fio JSON output file.

    Automatically selects read or write performance data
    according to the workload configuration.

    Latency values are converted from nanoseconds to microseconds.
    """

    # Load JSON file
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Get the first job
    job = data["jobs"][0]

    # Get workload configuration
    job_options = job.get("job options", {})
    workload = job_options.get("rw", "unknown")

    # Select read or write results
    if "write" in workload and "readwrite" not in workload:
        direction = "write"
    else:
        direction = "read"

    performance_data = job.get(direction, {})

    # Get completion latency statistics
    clat = performance_data.get("clat_ns", {})
    percentiles = clat.get("percentile", {})

    # Extract selected performance metrics
    result = {
        # Test information
        "fio_version": data.get("fio version"),
        "test_name": job.get("jobname"),
        "workload": workload,
        "direction": direction,
        "block_size": job_options.get("bs"),
        "runtime_ms": job.get("job_runtime"),

        # Overall performance
        "iops": performance_data.get("iops"),
        "bw_kib_s": performance_data.get("bw"),

        # Latency statistics (microseconds)
        "clat_mean_us": clat.get("mean", 0) / 1000,
        "clat_stddev_us": clat.get("stddev", 0) / 1000,
        "clat_p95_us": percentiles.get("95.000000", 0) / 1000,
        "clat_p99_us": percentiles.get("99.000000", 0) / 1000,
        "clat_p999_us": percentiles.get("99.900000", 0) / 1000,

        # Minimum and maximum performance
        "bw_min_kib_s": performance_data.get("bw_min"),
        "bw_max_kib_s": performance_data.get("bw_max"),
        "iops_min": performance_data.get("iops_min"),
        "iops_max": performance_data.get("iops_max"),
    }

    # Keep direction-specific fields for compatibility
    result[f"{direction}_iops"] = result["iops"]
    result[f"{direction}_bw_kib_s"] = result["bw_kib_s"]
    result[f"{direction}_bw_min_kib_s"] = result["bw_min_kib_s"]
    result[f"{direction}_bw_max_kib_s"] = result["bw_max_kib_s"]

    return result


if __name__ == "__main__":

    json_file = DATA_DIR / "sample_fio.json"

    benchmark_result = parse_fio_json(json_file)

    print("=" * 50)
    print("FIO BENCHMARK SUMMARY")
    print("=" * 50)

    for key, value in benchmark_result.items():
        print(f"{key}: {value}")

    print("=" * 50)
