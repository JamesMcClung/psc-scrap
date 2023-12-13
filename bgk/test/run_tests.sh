#!/bin/bash

path_to_test=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")

$path_to_test/../../autofigs.py "$path_to_test/autofigs_validation.yml"

for ref_fig_path in $path_to_test/figs-reference/*; do
    fig_name="$(basename "$ref_fig_path")"
    sum_output=$(sha1sum "$path_to_test/figs-output/$fig_name" | sed -e 's/\s.*$//')
    sum_ref=$(sha1sum "$path_to_test/figs-reference/$fig_name" | sed -e 's/\s.*$//')
    if [[ $sum_output != $sum_ref ]]; then
        echo "MISMATCH: $ref_fig_path"
        echo "      vs. $path_to_test/figs-output/$fig_name"
    else
        echo "match:    $ref_fig_path"
    fi
done
