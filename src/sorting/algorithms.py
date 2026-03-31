from __future__ import annotations
"""Implementaciones explicitas de los 12 algoritmos de ordenamiento solicitados."""


def timsort_algo(arr: list[int]) -> list[int]:
    """Usa TimSort de Python como referencia base de alto rendimiento."""
    data = arr.copy()
    data.sort()
    return data


def comb_sort(arr: list[int]) -> list[int]:
    """Comb Sort: mejora de Bubble Sort con gaps decrecientes."""
    data = arr.copy()
    gap = len(data)
    shrink = 1.3
    sorted_flag = False

    while not sorted_flag:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_flag = True

        i = 0
        while i + gap < len(data):
            if data[i] > data[i + gap]:
                data[i], data[i + gap] = data[i + gap], data[i]
                sorted_flag = False
            i += 1

    return data


def selection_sort(arr: list[int]) -> list[int]:
    """Selection Sort clasico: selecciona el minimo de la sublista restante."""
    data = arr.copy()
    n = len(data)

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if data[j] < data[min_idx]:
                min_idx = j
        data[i], data[min_idx] = data[min_idx], data[i]

    return data


class _Node:
    def __init__(self, key: int):
        self.key = key
        self.left: _Node | None = None
        self.right: _Node | None = None


def _bst_insert(root: _Node | None, key: int) -> _Node:
    """Inserta en BST de manera iterativa para evitar recursion profunda."""
    if root is None:
        return _Node(key)

    current = root
    while True:
        if key < current.key:
            if current.left is None:
                current.left = _Node(key)
                break
            current = current.left
        else:
            if current.right is None:
                current.right = _Node(key)
                break
            current = current.right

    return root


def _bst_inorder(root: _Node | None, out: list[int]) -> None:
    """Recorrido inorder iterativo del BST."""
    stack: list[_Node] = []
    current = root

    while stack or current is not None:
        while current is not None:
            stack.append(current)
            current = current.left

        current = stack.pop()
        out.append(current.key)
        current = current.right


def tree_sort(arr: list[int]) -> list[int]:
    """Tree Sort: insercion en BST + recorrido inorder."""
    root: _Node | None = None
    for value in arr:
        root = _bst_insert(root, value)

    out: list[int] = []
    _bst_inorder(root, out)
    return out


def pigeonhole_sort(arr: list[int]) -> list[int]:
    """Pigeonhole Sort para rangos acotados de enteros."""
    if not arr:
        return []

    min_val = min(arr)
    max_val = max(arr)
    size = max_val - min_val + 1
    holes = [0] * size

    for value in arr:
        holes[value - min_val] += 1

    out: list[int] = []
    for i, count in enumerate(holes):
        if count:
            out.extend([i + min_val] * count)

    return out


def _insertion_sort(data: list[int]) -> list[int]:
    """Ordenamiento por insercion usado internamente por Bucket Sort."""
    arr = data.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def bucket_sort(arr: list[int], bucket_count: int = 10) -> list[int]:
    """Bucket Sort con ordenamiento explicito dentro de cada bucket."""
    if not arr:
        return []

    min_val = min(arr)
    max_val = max(arr)
    if min_val == max_val:
        return arr.copy()

    span = max_val - min_val + 1
    buckets: list[list[int]] = [[] for _ in range(bucket_count)]

    for value in arr:
        idx = (value - min_val) * bucket_count // span
        if idx == bucket_count:
            idx -= 1
        buckets[idx].append(value)

    out: list[int] = []
    for bucket in buckets:
        out.extend(_insertion_sort(bucket))

    return out


def quick_sort(arr: list[int]) -> list[int]:
    """QuickSort in-place sobre copia de la entrada."""
    data = arr.copy()

    def partition(low: int, high: int) -> int:
        pivot = data[high]
        i = low - 1

        for j in range(low, high):
            if data[j] <= pivot:
                i += 1
                data[i], data[j] = data[j], data[i]

        data[i + 1], data[high] = data[high], data[i + 1]
        return i + 1

    def quick(low: int, high: int) -> None:
        if low < high:
            pi = partition(low, high)
            quick(low, pi - 1)
            quick(pi + 1, high)

    quick(0, len(data) - 1)
    return data


def heap_sort(arr: list[int]) -> list[int]:
    """HeapSort con max-heap construido manualmente."""
    data = arr.copy()
    n = len(data)

    def heapify(size: int, root: int) -> None:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < size and data[left] > data[largest]:
            largest = left
        if right < size and data[right] > data[largest]:
            largest = right
        if largest != root:
            data[root], data[largest] = data[largest], data[root]
            heapify(size, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    for i in range(n - 1, 0, -1):
        data[0], data[i] = data[i], data[0]
        heapify(i, 0)

    return data


def bitonic_sort(arr: list[int]) -> list[int]:
    """Bitonic Sort; rellena a potencia de 2 con un centinela."""
    if not arr:
        return []

    def compare_and_swap(data: list[int], i: int, j: int, asc: bool) -> None:
        if (asc and data[i] > data[j]) or (not asc and data[i] < data[j]):
            data[i], data[j] = data[j], data[i]

    def bitonic_merge(data: list[int], low: int, count: int, asc: bool) -> None:
        if count > 1:
            k = count // 2
            for i in range(low, low + k):
                compare_and_swap(data, i, i + k, asc)
            bitonic_merge(data, low, k, asc)
            bitonic_merge(data, low + k, k, asc)

    def bitonic_sort_recursive(data: list[int], low: int, count: int, asc: bool) -> None:
        if count > 1:
            k = count // 2
            bitonic_sort_recursive(data, low, k, True)
            bitonic_sort_recursive(data, low + k, k, False)
            bitonic_merge(data, low, count, asc)

    n = len(arr)
    p2 = 1
    while p2 < n:
        p2 *= 2

    sentinel = max(arr) + 1
    data = arr.copy() + [sentinel] * (p2 - n)

    bitonic_sort_recursive(data, 0, len(data), True)
    return data[:n]


def gnome_sort(arr: list[int]) -> list[int]:
    """Gnome Sort: intercambios locales retrocediendo cuando hay desorden."""
    data = arr.copy()
    idx = 0

    while idx < len(data):
        if idx == 0 or data[idx] >= data[idx - 1]:
            idx += 1
        else:
            data[idx], data[idx - 1] = data[idx - 1], data[idx]
            idx -= 1

    return data


def binary_insertion_sort(arr: list[int]) -> list[int]:
    """Insertion Sort con busqueda binaria del punto de insercion."""
    data = arr.copy()

    def loc(value: int, left: int, right: int) -> int:
        while left <= right:
            mid = (left + right) // 2
            if data[mid] <= value:
                left = mid + 1
            else:
                right = mid - 1
        return left

    for i in range(1, len(data)):
        value = data[i]
        j = loc(value, 0, i - 1)
        data = data[:j] + [value] + data[j:i] + data[i + 1 :]

    return data


def radix_sort(arr: list[int]) -> list[int]:
    """Radix Sort LSD base 10 para enteros no negativos."""
    if not arr:
        return []

    if min(arr) < 0:
        raise ValueError("RadixSort implementado solo para enteros no negativos")

    data = arr.copy()
    exp = 1
    max_val = max(data)

    while max_val // exp > 0:
        count = [0] * 10
        output = [0] * len(data)

        for value in data:
            index = (value // exp) % 10
            count[index] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]

        for i in range(len(data) - 1, -1, -1):
            index = (data[i] // exp) % 10
            output[count[index] - 1] = data[i]
            count[index] -= 1

        data = output
        exp *= 10

    return data
