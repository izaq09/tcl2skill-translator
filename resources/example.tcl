proc gen_test_cell_a {} {
    set netPriorityList [list]
    for {set ctr 0} {$ctr < 9} {incr ctr} {
        lappend netPriorityList net_${ctr}
    }

    genConstrainNet $netPriorityList

    genConstrainAspectRatio 1.4 1.6

    genConstrainBlockage {1.0 1.0} {2.0 2.0}

    genOpt
}
