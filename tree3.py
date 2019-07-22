class Node:
  def __init__(self, val):
    self.l_child = None
    self.r_child = None
    self.data = val
*插入node
r = Node(55)
binary_insert(r, Node(70))
binary_insert(r, Node(30))
binary_insert(r, Node(65))
binary_insert(r, Node(20))
binary_insert(r, Node(25))
binary_insert(r, Node(35))
binary_insert(r, Node(85))

def binary_insert(root, node):
  if root is None:
    root = node
  else:
      if root.data > node.data:
        if root.l_child is None:
          root.l_child = node
        else:
          binary_insert(root.l_child, node)
      else:
        if root.r_child is None:
          root.r_child = node
        else:
          binary_insert(root.r_child, node)

def in_order_print(root):
  if not root:
    return
  in_order_print(root.l_child)
  print(root.data)
  in_order_print(root.r_child)

def pre_order_print(root):
  if not root:
    return
  print(root.data)
  pre_order_print(root.l_child)
  pre_order_print(root.r_child) 

in_order_print(r)