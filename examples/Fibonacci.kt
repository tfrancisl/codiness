/** The n-th Fibonacci number, computed iteratively. */
fun fibonacci(n: Int): Long {
    require(n >= 0) { "n must be non-negative" }
    var a = 0L
    var b = 1L
    repeat(n) {
        val next = a + b
        a = b
        b = next
    }
    return a
}
