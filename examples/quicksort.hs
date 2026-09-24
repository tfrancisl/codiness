quicksort :: Ord a => [a] -> [a]
quicksort [] = []
quicksort (p:xs) = quicksort smaller ++ [p] ++ quicksort larger
  where
    smaller = [x | x <- xs, x < p]
    larger  = [x | x <- xs, x >= p]
