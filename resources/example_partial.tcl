proc gen_test_cell_a {} {
    set netPriorityList [list]
    for {set ctr 0} {$ctr < 9} {incr ctr} {
        lappend netPriorityList net_${ctr}
    }

    genConstrainNet $netPriorityList

    genOpt
}
