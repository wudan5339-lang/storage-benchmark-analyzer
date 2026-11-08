
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_BENCHMARK = "random_read"

DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

DEFAULT_DATA_DIR = DATA_DIR / DEFAULT_BENCHMARK
DEFAULT_REPORT_DIR = REPORTS_DIR / DEFAULT_BENCHMARK


def prepare_eda_data(log_data):
    """
    Prepare performance data for exploratory data analysis.
    """

    eda_data = pd.DataFrame({
        "IOPS": log_data["iops"]["iops"],
        "Bandwidth": log_data["bw_kib_s"]["bw_kib_s"],
        "Completion Latency": (
            log_data["clat_ns"]["clat_ns"] / 1000
        )
    })

    return eda_data


def generate_histograms(eda_data, output_dir):
    """
    Generate histograms for performance metrics.
    """

    columns = [
        "IOPS",
        "Bandwidth",
        "Completion Latency"
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, column in zip(axes, columns):
        values = eda_data[column].dropna()

        ax.hist(
            values,
            bins=10,
            edgecolor="black",
            alpha=0.75
        )

        ax.set_title(f"{column} Distribution")
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = output_dir / "eda_histograms.png"

    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Histogram saved: {output_path}")


def generate_boxplots(eda_data, output_dir):
    """
    Generate box plots for performance metrics.
    """

    columns = [
        "IOPS",
        "Bandwidth",
        "Completion Latency"
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, column in zip(axes, columns):
        values = eda_data[column].dropna()

        ax.boxplot(
            values,
            patch_artist=True
        )

        ax.set_title(f"{column} Box Plot")
        ax.set_ylabel(column)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = output_dir / "eda_boxplots.png"

    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Box plots saved: {output_path}")


def generate_eda(log_data, output_dir=DEFAULT_REPORT_DIR):
    """
    Run the complete exploratory data analysis.

    Parameters:
        log_data: Parsed fio log data.
        output_dir: Directory for saving EDA charts.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nStarting Exploratory Data Analysis...")

    # Prepare data using the existing parsed logs
    eda_data = prepare_eda_data(log_data)

    # Generate EDA charts
    generate_histograms(eda_data, output_dir)
    generate_boxplots(eda_data, output_dir)

    # Calculate descriptive statistics
    descriptive_statistics = eda_data.describe().round(2)

    print("\nEDA Summary:")
    print(descriptive_statistics)

    print("\nEDA completed successfully!")

    return {
        "sample_count": len(eda_data),
        "statistics": descriptive_statistics.to_dict()
    }


if __name__ == "__main__":

    from src.log_parser import parse_all_logs

    log_data = parse_all_logs(DEFAULT_DATA_DIR)

    generate_eda(log_data, DEFAULT_REPORT_DIR)
