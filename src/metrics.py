
import pandas as pd

from src.log_parser import parse_all_logs


def calculate_metrics(df, metric_name):
    """
    Calculate descriptive statistical metrics for a given
    performance metric.

    Parameters:
        df: DataFrame containing time-series data.
        metric_name: Name of the metric column.

    Returns:
        Dictionary containing descriptive statistics.
    """

    if metric_name not in df.columns:
        raise ValueError(
            f"Column '{metric_name}' not found in DataFrame."
        )

    # Convert values to numeric and remove invalid entries
    values = pd.to_numeric(
        df[metric_name],
        errors="coerce"
    ).dropna()

    if values.empty:
        return {
            "sample_count": 0,
            "average": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "stddev": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "p999": None,
            "cv": None
        }

    # Basic descriptive statistics
    average = values.mean()
    median = values.median()
    minimum = values.min()
    maximum = values.max()
    stddev = values.std()

    # Percentile analysis
    p50 = values.quantile(0.50)
    p95 = values.quantile(0.95)
    p99 = values.quantile(0.99)
    p999 = values.quantile(0.999)

    # Coefficient of Variation (CV)
    # CV = Standard Deviation / Mean * 100%
    if average != 0:
        cv = (stddev / abs(average)) * 100
    else:
        cv = None

    return {
        "sample_count": len(values),
        "average": average,
        "median": median,
        "minimum": minimum,
        "maximum": maximum,
        "stddev": stddev,
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "p999": p999,
        "cv": cv
    }


def analyze_all_metrics(log_data):
    """
    Analyze all three main fio performance metrics.

    Metrics:
        1. IOPS
        2. Bandwidth
        3. Completion Latency

    Returns:
        Dictionary containing statistical results.
    """

    results = {}

    metric_columns = {
        "iops": "iops",
        "bw_kib_s": "bw_kib_s",
        "clat_ns": "clat_ns"
    }

    for metric_name, column_name in metric_columns.items():

        results[metric_name] = calculate_metrics(
            log_data[metric_name],
            column_name
        )

    return results
