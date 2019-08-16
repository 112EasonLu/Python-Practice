# Note

1. Index Sort Practice_using lambda
sorted( source, key = lambda k : x[k] )

k is every elements in source.
" : x[k] " is  an assignment.
lambda k is scanning every elements in source.

Therefore,  "lambda k : x[k]" means every k can be assigned an  assignment x[k], and then they will form a group and type is similar to "link-list" . The function "sorted" work to sort list according to x[k], and the group k-x[k] will move together. Finally, we can print out the result.
