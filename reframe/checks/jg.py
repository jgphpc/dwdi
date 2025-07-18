import os

import reframe as rfm
import reframe.utility.sanity as sn

xname_ln = {
        "daint-ln001": "x1104c0s0b0n0",
        "daint-ln002": "x1200c0s0b0n0",
        "daint-ln003": "x1201c0s0b0n0",
        "eiger-ln001": "x1002c0s7b0n0",
        "eiger-ln002": "x1002c1s7b0n0",
        "eiger-ln003": "x1003c0s7b0n0",
        "eiger-ln004": "x1003c1s7b0n0",
        "santis-ln001": "x1101c0s0b0n0",
        "santis-ln002": "x1102c0s0b0n0",
        "clariden-ln001": "x1301c0s0b0n0",
        "clariden-ln002": "x1302c0s0b0n0",
        "beverin-ln001": "x1006c0s3b1n0",
}


@rfm.simple_test
class FreeDevShm(rfm.RunOnlyRegressionTest):
    """
    Grafana / Dashboards / DWDI / Alps Login nodes

    ./reframe.git/bin/reframe --keep-stage-files \
            -C ./common_elastic.py -c checks/jg.py \
            -r --report-file=latest.json \
            --performance-report \
            --failure-stats 
    """
    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    host = parameter([
        "daint-ln001",
        "daint-ln002",
        "daint-ln003",
        "eiger-ln001",
        "eiger-ln002",
        "eiger-ln003",
        "eiger-ln004",
        "santis-ln001",
        "santis-ln002",
        "clariden-ln001",
        "clariden-ln002",
        "beverin-ln001",
    ])
    # host = parameter(['daint-ln001', 'daint-ln002'])
    # host = parameter(['daint-ln001'])
    descr = 'Check /dev/shm capacity'

    @run_before('run')
    def set_runtime_args(self):
        # self.executable = f'ssh -x -J piccinal@ela.cscs.ch piccinal@{self.host}.cscs.ch'
        self.executable = f'ssh -x {xname_ln[self.host]}'
        self.executable_opts = ['/bin/df /dev/shm']
        # self.prerun_cmds = [f'echo -n hostname: ; {self.executable} hostname |sha1 |tr -d [a-z]']

    @sanity_function
    def set_sanity(self):
        return sn.all([sn.assert_found(r'^tmpfs.*/dev/shm', self.stdout)])

    @performance_function('%')
    def dev_shm_used(self):
        regex = r'^tmpfs\s+\S+\s+\S+\s+\S+\s+(?P<pct>\d+)% /dev/shm'
        return sn.extractsingle(regex, self.stdout, 'pct', int)
