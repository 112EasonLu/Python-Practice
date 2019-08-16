# Note

1. Index Sort Practice_using lambda
     
     Algorithm : sorted( source, key = lambda k : x[k] )

     k is every elements in source.
     " : x[k] " is  an assignment.
     "lambda k" suggest  scanning every elements in source (list).

     Therefore,  "lambda k : x[k]" means every k can be assigned an value x[k], and then they 
     form a group whose type is similar to "link-list" . 

     The function "sorted" is able to sort list according to x[k] value, and the group k-x[k] will move 
     together. Finally, we can print out the result.
