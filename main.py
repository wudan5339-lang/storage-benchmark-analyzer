
from pathlib import Path

from src.json_parser import parse_fio_json
from src.log_parser import parse_all_logs
from src.metrics import analyze_all_metrics
from src.visualization import generate_all_charts
from src.eda import generate_eda
from src.report_generator import generate_report


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"

BENCHMARKS = [
    "sequential_read",
    "sequential_write",
    "random_read",
    "random_write"
]


def main():

    benchmark_results = []
    failed_benchmarks = []

    for index, benchmark_name in enumerate(BENCHMARKS, start=1):

        print("\n" + "=" * 60)
        print(
            f"BENCHMARK {index}/{len(BENCHMARKS)}: "
            f"{benchmark_name.upper()}"
        )
        print("=" * 60)

        benchmark_dir = DATA_DIR / benchmark_name
        json_file = benchmark_dir / "sample_fio.json"

        report_dir = REPORTS_DIR / benchmark_name
        report_dir.mkdir(parents=True, exist_ok=True)

        required_files = [
            json_file,
            benchmark_dir / "sample_iops.1.log",
            benchmark_dir / "sample_bw.1.log",
            benchmark_dir / "sample_clat.1.log"
        ]

        missing_files = [
            file for file in required_files
            if not file.exists()
        ]

        if missing_files:

            print("\nMissing required files:")

            for file in missing_files:
                print(f"  - {file}")

            failed_benchmarks.append(benchmark_name)
            continue

        try:

            print("\n[1/5] Parsing fio JSON...")

            benchmark_result = parse_fio_json(json_file)

            print("\n[2/5] Parsing fio LOG files...")

            log_data = parse_all_logs(benchmark_dir)

            print("\n[3/5] Analyzing performance metrics...")

            analysis_results = analyze_all_metrics(log_data)

            print("\n[4/5] Generating performance charts...")

            generate_all_charts(
                log_data,
                report_dir
            )

            print("\n[5/5] Running EDA...")

            eda_results = generate_eda(
                log_data,
                report_dir
            )

            benchmark_results.append({
                "name": benchmark_name,
                "benchmark": benchmark_result,
                "analysis": analysis_results,
                "eda": eda_results
            })

            print(f"\nCompleted: {benchmark_name}")

        except Exception as error:

            print(f"\nERROR while processing {benchmark_name}:")
            print(error)

            failed_benchmarks.append(benchmark_name)

    print("\n" + "=" * 60)
    print("BENCHMARK ANALYSIS SUMMARY")
    print("=" * 60)

    print(f"\nSuccessful: {len(benchmark_results)}")

    for item in benchmark_results:
        print(f"  - {item['name']}")

    print(f"\nFailed: {len(failed_benchmarks)}")

    for name in failed_benchmarks:
        print(f"  - {name}")

    if benchmark_results:

        print("\nGenerating combined HTML report...")

        generate_report(
            benchmark_results,
            REPORTS_DIR
        )

    if failed_benchmarks:
        print("\nSome benchmarks failed. Please check the errors.")
    else:
        print("\nALL BENCHMARKS ANALYZED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
