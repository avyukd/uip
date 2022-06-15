#!/bin/bash
for var in "$@"
do
    cat markdown/$var.md
done > ../../../avyukd.github.io/_posts/new_post.md