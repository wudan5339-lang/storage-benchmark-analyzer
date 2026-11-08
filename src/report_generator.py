
from pathlib import Path
from datetime import datetime
from html import escape


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"


def format_number(value, decimals=2):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def generate_report(
    benchmark_results,
    output_dir=DEFAULT_REPORT_DIR
):
    """
    Generate one combined HTML report for all workloads.

    benchmark_results contains the results of multiple benchmarks.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "benchmark_dashboard.html"

    # --------------------------------------------------
    # 1. Build overall comparison table
    # --------------------------------------------------

    comparison_rows = ""

    for item in benchmark_results:

        name = item["name"]
        benchmark = item["benchmark"]

        title = name.replace("_", " ").title()

        comparison_rows += f"""
        <tr>
            <td>{escape(title)}</td>
            <td>{format_number(benchmark.get("iops"))}</td>
            <td>{format_number(benchmark.get("bw_kib_s"))}</td>
            <td>{format_number(benchmark.get("clat_mean_us"))}</td>
            <td>{format_number(benchmark.get("clat_p95_us"))}</td>
            <td>{format_number(benchmark.get("clat_p99_us"))}</td>
        </tr>
        """

    # --------------------------------------------------
    # 2. Build detailed workload sections
    # --------------------------------------------------

    workload_sections = ""

    for index, item in enumerate(benchmark_results, start=1):

        name = item["name"]
        benchmark = item["benchmark"]
        analysis = item["analysis"]
        eda = item["eda"]

        title = name.replace("_", " ").title()

        # Performance configuration
        config_html = f"""
        <div class="config">
            <span>Workload: {escape(str(benchmark.get("workload", "N/A")))}</span>
            <span>Direction: {escape(str(benchmark.get("direction", "N/A")))}</span>
            <span>Block Size: {escape(str(benchmark.get("block_size", "N/A")))}</span>
            <span>Runtime: {format_number(benchmark.get("runtime_ms"), 0)} ms</span>
            <span>fio Version: {escape(str(benchmark.get("fio_version", "N/A")))}</span>
        </div>
        """

        # Overall performance
        performance_html = f"""
        <table>
            <tr>
                <th>IOPS</th>
                <th>Bandwidth (KiB/s)</th>
                <th>Mean Latency (µs)</th>
                <th>P95 (µs)</th>
                <th>P99 (µs)</th>
                <th>P99.9 (µs)</th>
            </tr>
            <tr>
                <td>{format_number(benchmark.get("iops"))}</td>
                <td>{format_number(benchmark.get("bw_kib_s"))}</td>
                <td>{format_number(benchmark.get("clat_mean_us"))}</td>
                <td>{format_number(benchmark.get("clat_p95_us"))}</td>
                <td>{format_number(benchmark.get("clat_p99_us"))}</td>
                <td>{format_number(benchmark.get("clat_p999_us"))}</td>
            </tr>
        </table>
        """

        # Time-series descriptive statistics
        statistics_rows = ""

        metric_names = [
            ("iops", "IOPS", 1),
            ("bw_kib_s", "Bandwidth (KiB/s)", 1),
            ("clat_ns", "Completion Latency (µs)", 1000)
        ]

        for key, label, divisor in metric_names:

            stats = analysis.get(key, {})

            def convert(value):

                if value is None:
                    return None

                return value / divisor

            statistics_rows += f"""
            <tr>
                <td>{label}</td>
                <td>{format_number(convert(stats.get("average")))}</td>
                <td>{format_number(convert(stats.get("median")))}</td>
                <td>{format_number(convert(stats.get("minimum")))}</td>
                <td>{format_number(convert(stats.get("maximum")))}</td>
                <td>{format_number(convert(stats.get("stddev")))}</td>
                <td>{format_number(convert(stats.get("p95")))}</td>
                <td>{format_number(convert(stats.get("p99")))}</td>
            </tr>
            """

        # EDA sample information
        sample_count = eda.get("sample_count", 0)

        # Images
        image_names = [
            ("IOPS Performance Trend", "iops_trend.png"),
            ("Bandwidth Performance Trend", "bw_trend.png"),
            ("Completion Latency Trend", "clat_trend.png"),
            ("Histograms", "eda_histograms.png"),
            ("Box Plots", "eda_boxplots.png")
        ]

        images_html = ""

        for image_title, filename in image_names:

            image_path = f"{name}/{filename}"

            images_html += f"""
            <div class="chart">
                <h3>{image_title}</h3>
                <img src="{image_path}" alt="{image_title}">
            </div>
            """

        workload_sections += f"""
        <section id="{name}">

            <h2>{index}. {escape(title)}</h2>

            {config_html}

            <h3>Overall Performance</h3>

            {performance_html}

            <h3>Time-Series Descriptive Statistics</h3>

            <p>
                Number of samples: {sample_count}
            </p>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Mean</th>
                    <th>Median</th>
                    <th>Minimum</th>
                    <th>Maximum</th>
                    <th>Std Dev</th>
                    <th>P95</th>
                    <th>P99</th>
                </tr>

                {statistics_rows}

            </table>

            <h3>Exploratory Data Analysis</h3>

            <div class="charts">
                {images_html}
            </div>

        </section>
        """

    # --------------------------------------------------
    # 3. Build navigation links
    # --------------------------------------------------

    navigation_links = ""

    for item in benchmark_results:

        name = item["name"]
        title = name.replace("_", " ").title()

        navigation_links += f"""
        <a href="#{name}">{escape(title)}</a>
        """

    # --------------------------------------------------
    # 4. Complete HTML document
    # --------------------------------------------------

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Storage Benchmark Dashboard</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                background: #f4f6f9;
                color: #263238;
                line-height: 1.6;
            }}

            header {{
                background: #172b4d;
                color: white;
                padding: 35px 7%;
            }}

            header h1 {{
                margin: 0;
                font-size: 30px;
            }}

            header p {{
                color: #d4dce8;
            }}

            nav {{
                background: white;
                padding: 15px 7%;
                position: sticky;
                top: 0;
                z-index: 10;
                border-bottom: 1px solid #ddd;
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }}

            nav a {{
                text-decoration: none;
                color: #2457a7;
                font-weight: bold;
            }}

            main {{
                max-width: 1250px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            section {{
                background: white;
                padding: 28px;
                margin-bottom: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}

            h2 {{
                border-bottom: 2px solid #e6eaf0;
                padding-bottom: 12px;
            }}

            h3 {{
                margin-top: 28px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0 25px;
                font-size: 14px;
            }}

            th, td {{
                padding: 12px;
                border: 1px solid #e1e5eb;
                text-align: center;
            }}

            th {{
                background: #edf2f8;
            }}

            .config {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin: 18px 0;
            }}

            .config span {{
                background: #edf2f8;
                padding: 8px 13px;
                border-radius: 6px;
                font-size: 13px;
            }}

            .charts {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 22px;
            }}

            .chart {{
                border: 1px solid #e5e8ed;
                border-radius: 8px;
                padding: 12px;
                min-width: 0;
            }}

            .chart h3 {{
                margin-top: 5px;
                font-size: 16px;
            }}

            .chart img {{
                width: 100%;
                height: auto;
            }}

            .note {{
                background: #fff8e6;
                padding: 18px;
                border-left: 4px solid #e6a23c;
                border-radius: 5px;
            }}

            footer {{
                text-align: center;
                padding: 25px;
                color: #777;
            }}

            @media (max-width: 750px) {{

                .charts {{
                    grid-template-columns: 1fr;
                }}

                table {{
                    display: block;
                    overflow-x: auto;
                }}

                nav {{
                    position: static;
                }}

            }}

        </style>

    </head>

    <body>

        <header>

            <h1>Storage Benchmark Analyzer</h1>

            <p>
                Performance Analysis of Sequential and Random I/O Workloads
            </p>

            <p>
                Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>

        </header>

        <nav>

            <a href="#overview">Overview</a>

            {navigation_links}

            <a href="#limitations">Limitations</a>

        </nav>

        <main>

            <section id="overview">

                <h2>Benchmark Overview</h2>

                <p>
                    Comparison of storage performance across
                    different I/O workloads.
                </p>

                <table>

                    <tr>
                        <th>Workload</th>
                        <th>IOPS</th>
                        <th>Bandwidth (KiB/s)</th>
                        <th>Mean Latency (µs)</th>
                        <th>P95 (µs)</th>
                        <th>P99 (µs)</th>
                    </tr>

                    {comparison_rows}

                </table>

            </section>

            {workload_sections}

            <section id="limitations">

                <h2>Test Configuration and Limitations</h2>

                <ul>

                    <li>
                        Benchmark data was collected using fio.
                    </li>

                    <li>
                        Sequential workloads use 128 KiB block sizes.
                    </li>

                    <li>
                        Random workloads use 4 KiB block sizes.
                    </li>

                    <li>
                        Time-series logs represent aggregated measurement
                        intervals, not individual I/O operations.
                    </li>

                    <li>
                        The current configuration uses direct=0.
                        Operating system caching may influence results.
                    </li>

                    <li>
                        IOPS and bandwidth are mathematically related
                        through block size.
                    </li>

                </ul>

                <div class="note">

                    These results demonstrate a benchmark data analysis
                    workflow. They should not be treated as definitive
                    measurements of physical SSD performance.

                </div>

            </section>

        </main>

        <footer>

            Storage Benchmark Analyzer |
            Python, Pandas, Matplotlib and fio

        </footer>

    </body>

    </html>
    """

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"\nCombined HTML report generated: {report_path}")

    return report_path


if __name__ == "__main__":

    print(
        "Please run main.py to generate the combined benchmark report."
    )
