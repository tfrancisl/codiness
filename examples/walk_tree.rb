def tree_depth(node)
  return 0 if node.nil?

  1 + [tree_depth(node.left), tree_depth(node.right)].max
end
