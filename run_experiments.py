"""
Sorting algorithm experiments: timing on random and nearly-sorted arrays.
Command-line interface as required for Data Structures Python Assignment 1.
"""

from __future__ import annotations

import argparse
import random
import statistics
import time
from typing import Callable, List, Sequence, Tuple

import matplotlib.pyplot as plt

# Selected algorithms for this assignment: 1 Bubble, 3 Insertion, 4 Merge.
DEFAULT_ALGORITHM_IDS: List[int] = [1, 3, 4]

# Default array sizes for plots: 0 through 5000 (step 500).
DEFAULT_SIZES: List[int] = list(range(0, 5001, 500))
# X-axis: always show from 0 up to at least this n (and wider if -s goes beyond).
X_AXIS_MIN = 0
X_AXIS_MAX = 5000

# --- Sorting algorithms (IDs 1–5) -----------------------------------------

SortFn = Callable[[List[int]], None]


def bubble_sort(arr: List[int]) -> None:
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break


def selection_sort(arr: List[int]) -> None:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]


def insertion_sort(arr: List[int]) -> None:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def _merge(arr: List[int], left: int, mid: int, right: int) -> None:
    L = arr[left : mid + 1]
    R = arr[mid + 1 : right + 1]
    i = j = 0
    k = left
    while i < len(L) and j < len(R):
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
    while i < len(L):
        arr[k] = L[i]
        i += 1
        k += 1
    while j < len(R):
        arr[k] = R[j]
        j += 1
        k += 1


def _merge_sort_range(arr: List[int], left: int, right: int) -> None:
    if left < right:
        mid = (left + right) // 2
        _merge_sort_range(arr, left, mid)
        _merge_sort_range(arr, mid + 1, right)
        _merge(arr, left, mid, right)


def merge_sort(arr: List[int]) -> None:
    if len(arr) > 1:
        _merge_sort_range(arr, 0, len(arr) - 1)


def _partition(arr: List[int], low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quick_sort_range(arr: List[int], low: int, high: int) -> None:
    if low < high:
        p = _partition(arr, low, high)
        _quick_sort_range(arr, low, p - 1)
        _quick_sort_range(arr, p + 1, high)


def quick_sort(arr: List[int]) -> None:
    if len(arr) > 1:
        _quick_sort_range(arr, 0, len(arr) - 1)


ALGORITHMS: dict[int, Tuple[str, SortFn]] = {
    1: ("Bubble Sort", bubble_sort),
    2: ("Selection Sort", selection_sort),
    3: ("Insertion Sort", insertion_sort),
    4: ("Merge Sort", merge_sort),
    5: ("Quick Sort", quick_sort),
}


# --- Data generation ----------------------------------------------------------

def random_array(n: int, seed: int | None = None) -> List[int]:
    rng = random.Random(seed)
    return [rng.randint(-(10**9), 10**9) for _ in range(n)]


def nearly_sorted_array(n: int, noise_fraction: float, base_seed: int | None) -> List[int]:
    """Sorted 0..n-1, then apply roughly (noise_fraction * n) random swaps."""
    if n <= 0:
        return []
    arr = list(range(n))
    rng = random.Random(base_seed)
    num_swaps = max(0, int(n * noise_fraction))
    if n >= 2 and num_swaps < 1:
        num_swaps = 1
    for _ in range(num_swaps):
        i = rng.randrange(n)
        j = rng.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


# --- Timing -------------------------------------------------------------------

def time_sort_once(sort_fn: SortFn, data: List[int]) -> float:
    work = list(data)
    t0 = time.perf_counter()
    sort_fn(work)
    return time.perf_counter() - t0


def run_trials(
    sort_fn: SortFn,
    build_data: Callable[[int, int], List[int]],
    size: int,
    repetitions: int,
) -> Tuple[float, float]:
    """Return (mean_seconds, stdev_seconds)."""
    times: List[float] = []
    for rep in range(repetitions):
        data = build_data(size, rep)
        times.append(time_sort_once(sort_fn, data))
    mean_t = statistics.mean(times)
    std_t = statistics.stdev(times) if len(times) > 1 else 0.0
    return mean_t, std_t


# --- Plotting -----------------------------------------------------------------

def _xlim_right(sizes: Sequence[int]) -> float:
    return float(max(X_AXIS_MAX, max(sizes, default=0)))


def plot_random_comparison(
    algo_ids: Sequence[int],
    sizes: Sequence[int],
    means: dict[int, List[float]],
    repetitions: int,
    out_path: str,
) -> None:
    plt.figure(figsize=(10, 6))
    for aid in algo_ids:
        name, _ = ALGORITHMS[aid]
        y = means[aid]
        plt.plot(sizes, y, label=name, marker="o")
    plt.xlabel("Array size (n)")
    plt.ylabel("Time (seconds)")
    plt.title(f"Random integers — mean time over {repetitions} runs")
    plt.xlim(X_AXIS_MIN, _xlim_right(sizes))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_nearly_sorted_comparison(
    algo_ids: Sequence[int],
    sizes: Sequence[int],
    means_5: dict[int, List[float]],
    means_20: dict[int, List[float]],
    repetitions: int,
    out_path: str,
) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for aid in algo_ids:
        name, _ = ALGORITHMS[aid]
        ax1.plot(sizes, means_5[aid], label=name, marker="o")
        ax2.plot(sizes, means_20[aid], label=name, marker="o")
    ax1.set_xlabel("Array size (n)")
    ax2.set_xlabel("Array size (n)")
    ax1.set_ylabel("Time (seconds)")
    ax1.set_title("Nearly sorted — ~5% random swaps")
    ax2.set_title("Nearly sorted — ~20% random swaps")
    xr = _xlim_right(sizes)
    ax1.set_xlim(X_AXIS_MIN, xr)
    ax2.set_xlim(X_AXIS_MIN, xr)
    ax1.legend(fontsize=8)
    ax2.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    fig.suptitle(f"Mean time over {repetitions} runs")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_single_noise(
    algo_ids: Sequence[int],
    sizes: Sequence[int],
    means: dict[int, List[float]],
    repetitions: int,
    noise_label: str,
    out_path: str,
) -> None:
    plt.figure(figsize=(10, 6))
    for aid in algo_ids:
        name, _ = ALGORITHMS[aid]
        plt.plot(sizes, means[aid], label=name, marker="o")
    plt.xlabel("Array size (n)")
    plt.ylabel("Time (seconds)")
    plt.title(f"Nearly sorted ({noise_label}) — mean time over {repetitions} runs")
    plt.xlim(X_AXIS_MIN, _xlim_right(sizes))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# --- CLI ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Compare sorting algorithms (Assignment 1). "
        "Use -e 0 (or omit -e) for random arrays → result1.png; "
        "-e 1 or -e 2 for nearly sorted → result2.png."
    )
    p.add_argument(
        "-a",
        "--algorithms",
        type=int,
        nargs="*",
        default=DEFAULT_ALGORITHM_IDS,
        choices=sorted(ALGORITHMS.keys()),
        metavar="ID",
        help="Algorithm IDs (default: 1 3 4). 1 Bubble, 2 Selection, 3 Insertion, "
        "4 Merge, 5 Quick",
    )
    p.add_argument(
        "-s",
        "--sizes",
        type=int,
        nargs="*",
        default=DEFAULT_SIZES,
        help=f"Array sizes (default: 0..{X_AXIS_MAX} step 500). Example: -s 0 1000 5000",
    )
    p.add_argument(
        "-e",
        "--experiment",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="0 = random arrays (result1.png); 1 = ~5%% noise (result2.png); "
        "2 = ~20%% noise (result2.png). For result2 with both panels, use --both-noise.",
    )
    p.add_argument(
        "--both-noise",
        action="store_true",
        help="With -e 1 or -e 2 ignored for layout: build result2.png with 5%% and 20%% side by side.",
    )
    p.add_argument(
        "-r",
        "--repetitions",
        type=int,
        default=10,
        help="Number of timed runs per (algorithm, size)",
    )
    p.add_argument(
        "--out1",
        default="result1.png",
        help="Output path for random-array experiment",
    )
    p.add_argument(
        "--out2",
        default="result2.png",
        help="Output path for nearly-sorted experiment",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    algo_ids = args.algorithms if args.algorithms else list(DEFAULT_ALGORITHM_IDS)
    sizes = sorted(args.sizes) if args.sizes else list(DEFAULT_SIZES)
    reps = max(1, args.repetitions)

    if args.experiment == 0 and not args.both_noise:
        means: dict[int, List[float]] = {a: [] for a in algo_ids}

        def build_random(n: int, rep: int) -> List[int]:
            return random_array(n, seed=rep * 10007 + n)

        for aid in algo_ids:
            _, fn = ALGORITHMS[aid]
            for n in sizes:
                m, _ = run_trials(fn, build_random, n, reps)
                means[aid].append(m)

        plot_random_comparison(algo_ids, sizes, means, reps, args.out1)
        print(f"Wrote {args.out1} (random arrays).")
        return

    if args.both_noise:
        means_5 = {a: [] for a in algo_ids}
        means_20 = {a: [] for a in algo_ids}

        def build_noisy(n: int, rep: int, frac: float) -> List[int]:
            return nearly_sorted_array(n, frac, base_seed=rep * 30011 + n + int(frac * 1000))

        for aid in algo_ids:
            _, fn = ALGORITHMS[aid]
            for n in sizes:
                m5, _ = run_trials(
                    fn,
                    lambda n_, r_, f=0.05: build_noisy(n_, r_, f),
                    n,
                    reps,
                )
                means_5[aid].append(m5)
                m20, _ = run_trials(
                    fn,
                    lambda n_, r_, f=0.20: build_noisy(n_, r_, f),
                    n,
                    reps,
                )
                means_20[aid].append(m20)

        plot_nearly_sorted_comparison(
            algo_ids, sizes, means_5, means_20, reps, args.out2
        )
        print(f"Wrote {args.out2} (nearly sorted, 5%% and 20%% noise).")
        return

    frac = 0.05 if args.experiment == 1 else 0.20
    label = "~5% swaps" if args.experiment == 1 else "~20% swaps"
    means: dict[int, List[float]] = {a: [] for a in algo_ids}

    def build(n: int, rep: int) -> List[int]:
        return nearly_sorted_array(n, frac, base_seed=rep * 50021 + n)

    for aid in algo_ids:
        _, fn = ALGORITHMS[aid]
        for n in sizes:
            m, _ = run_trials(fn, build, n, reps)
            means[aid].append(m)

    plot_single_noise(algo_ids, sizes, means, reps, label, args.out2)
    print(f"Wrote {args.out2} (nearly sorted, {label}).")


if __name__ == "__main__":
    main()
