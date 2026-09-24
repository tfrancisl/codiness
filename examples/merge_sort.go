package sorting

func MergeSort(xs []int) []int {
	if len(xs) <= 1 {
		return xs
	}
	mid := len(xs) / 2
	left, right := MergeSort(xs[:mid]), MergeSort(xs[mid:])

	merged := make([]int, 0, len(xs))
	i, j := 0, 0
	for i < len(left) && j < len(right) {
		if left[i] <= right[j] {
			merged = append(merged, left[i])
			i++
		} else {
			merged = append(merged, right[j])
			j++
		}
	}
	merged = append(merged, left[i:]...)
	return append(merged, right[j:]...)
}
