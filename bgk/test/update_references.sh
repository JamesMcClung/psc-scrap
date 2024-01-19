#!/bin/bash

path_to_test=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")

cp $path_to_test/figs-output/* $path_to_test/figs-reference