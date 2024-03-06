import sys

import bgk
import bgk.backend.wrapper_h5 as wrapper_h5


do_memory_tracking = len(sys.argv) > 1 and sys.argv[1] in ["-m", "--mem"]


def check_mem():
    if do_memory_tracking:
        print(gc.get_count())


if do_memory_tracking:
    import gc

    gc.collect()
    gc.disable()


# run_manager = bgk.RunManager("/mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/exact/B00.25-n128")
# vm = bgk.VideoMaker(11, run_manager)

# vm.set_param(bgk.run_params.ne)
# vm.set_view_bounds(bgk.Bounds3D.whole())

check_mem()

w = wrapper_h5.load_h5("/mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/exact/B00.25-n128", "prt", 0)
print(w.col("x"))
print(w.col("rho"))

check_mem()


# print(w.head())
