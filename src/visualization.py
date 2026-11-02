
import matplotlib.pyplot as plt
from pathlib import Path

from src.log_parser import parse_all_logs


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "benchmark_01"


def plot_metric(df, metric_name, title, ylabel, filename,
                output_dir, divisor=1):
    """
    Generate a performance trend chart.
    """

    time_seconds = df["time_ms"] / 1000
    values = df[metric_name] / divisor

    plt.figure(figsize=(10, 5))

    plt.plot(
        time_seconds,
        values,
        marker="o",
        label=title
    )

    plt.title(title)
    plt.xlabel("Time (seconds)")
    plt.ylabel(ylabel)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / filename

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"Chart saved: {output_file}")


def generate_all_charts(log_data, output_dir=DEFAULT_REPORT_DIR):
    """
    Generate all performance trend charts.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # IOPS trend
    plot_metric(
        log_data["iops"],
        "iops",
        "IOPS Performance Over Time",
        "IOPS",
        "iops_trend.png",
        output_dir
    )

    # Bandwidth trend
    plot_metric(
        log_data["bw_kib_s"],
        "bw_kib_s",
        "Bandwidth Performance Over Time",
        "Bandwidth (KiB/s)",
        "bw_trend.png",
        output_dir
    )

    # Completion latency trend
    plot_metric(
        log_data["clat_ns"],
        "clat_ns",
        "Completion Latency Over Time",
        "Latency (us)",
        "clat_trend.png",
        output_dir,
        divisor=1000
    )


if __name__ == "__main__":

    # Read benchmark data
    log_data = parse_all_logs(DEFAULT_DATA_DIR)

    # Generate charts
    generate_all_charts(log_data, DEFAULT_REPORT_DIR)

    print("\nVisualization completed successfully!")
