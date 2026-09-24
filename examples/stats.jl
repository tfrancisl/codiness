"""Mean and sample standard deviation of a vector."""
function summarize(xs::AbstractVector{<:Real})
    n = length(xs)
    μ = sum(xs) / n
    σ = sqrt(sum(x -> (x - μ)^2, xs) / (n - 1))
    return (mean = μ, std = σ)
end
