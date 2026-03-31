ASSETS = [
    "SPY",
    "IVV",
    "VOO",
    "QQQ",
    "DIA",
    "IWM",
    "EFA",
    "EEM",
    "VTI",
    "VEA",
    "VWO",
    "AGG",
    "LQD",
    "TLT",
    "GLD",
    "SLV",
    "USO",
    "XLF",
    "XLK",
    "XLV",
]

COMPLEXITIES = {
    "TimSort": "O(n log n)",
    "Comb Sort": "O(n^2)",
    "Selection Sort": "O(n^2)",
    "Tree Sort": "O(n log n) promedio / O(n^2) peor",
    "Pigeonhole Sort": "O(n + R)",
    "Bucket Sort": "O(n + k) promedio",
    "QuickSort": "O(n log n) promedio / O(n^2) peor",
    "HeapSort": "O(n log n)",
    "Bitonic Sort": "O(n log^2 n)",
    "Gnome Sort": "O(n^2)",
    "Binary Insertion Sort": "O(n^2)",
    "RadixSort": "O(d*(n+b))",
}

DEFAULT_YEARS = 5
DEFAULT_BENCHMARK_SIZE = 1200
