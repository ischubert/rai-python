"""
Script containing tests for automated testing with pytest
"""
import sys
import os
import numpy as np
sys.path.append(os.getenv("HOME") + '/git/rai-python/rai/rai/ry')


def test_libry():
    """
    Test whether
    - libry can be imported from the expected $PATH
    - a config can be created
    - a KOMO problem can be solved
    - a physx simulation can be created
    """
    import libry as ry

    var_conf = ry.Config()
    var_conf.addFile("pytest_tests/z.push.g")
    x_start = var_conf.getFrameState()
    var_conf.makeObjectsFree(['finger'])
    var_conf.setFrameState(x_start)

    var_skel = [
        # makes the finger free
        [.1, 1.], ry.SY.magic, ['finger'],
        [.1, 1.], ry.SY.dampMotion, ['finger'],
        # the following skeleton symbols introduce POAs and force vectors as
        # decision variables. For more information, see
        # https://ipvs.informatik.uni-stuttgart.de/mlr/papers/20-toussaint-RAL.pdf
        [.5, 1.], ry.SY.quasiStaticOn, ["box"],
        [.5, 1.], ry.SY.contact, ["finger", "box"]
    ]

    var_komo = var_conf.komo_path(
        phases=1.,
        stepsPerPhase=80,
        timePerPhase=1.,
        # k_order=2,
        useSwift=False  # useSwift=True ()=calling collision detection)
    )
    print(f'sparseOptimization = {var_komo.getSparseOptimization()}')
    print(f'denseOptimization = {var_komo.getDenseOptimization()}')
    var_komo.addSquaredQuaternionNorms()
    var_komo.addSkeleton(var_skel)

    # first objective: box should be at target at the end
    var_komo.addObjective(
        time=[1.],  # at time 1,
        feature=ry.FS.poseDiff,  # Feature is the 7D pose diff...
        frames=["box", "target"],  # ...between the box and the target
        type=ry.OT.eq,  # sums-of-squares error
        scale=[1e2],  # scale
        order=0  # 0-th order (i.e. positions, not velocities)
    )

    # second objective: velocity of everything should be 0 at the end
    var_komo.addObjective(
        time=[1.],  # at time 1,
        feature=ry.FS.qItself,  # Feature: The joint coordinates
        # (but 1st order, therefore its velocities)
        frames=[],  # ...all frames
        type=ry.OT.sos,  # sums-of-squares error
        scale=[1e0],  # scale
        order=1
    )

    var_komo.setupConfigurations()
    var_komo.optimize()

    var_sim = var_conf.simulation(ry.SimulatorEngine.physx, False)
    for _ in range(10):
        var_conf.setFrameState(x_start)
        var_sim.setState(frameState=x_start, frameVelocities=np.array([]))
        tau = .01
        for __ in range(0, 100):
            var_sim.step(np.array([1., 1., 1., 0., 0., 0., 0.]), tau)

    assert False
