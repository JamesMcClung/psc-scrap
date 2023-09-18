import bgk

loader = bgk.Loader("/mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/exact/B01.00-n256")
vm = bgk.VideoMaker(10, loader)

# ne

vm.loadData(bgk.run_params.ne)
vm.setSlice(bgk.DataSlice(slice(None, None), ""))
originmeans_ne = vm._getMeansAtOrigin()

originmeans_reference_ne = [0.2173656067285213, 0.23256763654478374, 0.21581908279156323, 0.2140063321121481, 0.21773397608914793, 0.19281835710968376, 0.19731853646981545, 0.20171676607789518, 0.2300779146065553, 0.18489895776523724]


for om, omr in zip(originmeans_ne, originmeans_reference_ne):
    if om != omr:
        print("Test failed for ne.")
        print("New: [" + ", ".join(str(a) for a in originmeans_ne) + "]")
        print("Ref: [" + ", ".join(str(a) for a in originmeans_reference_ne) + "]")
        exit(1)

# e_phi

vm.loadData(bgk.run_params.e_phi)
vm.setSlice(bgk.DataSlice(slice(None, None), ""))
originmeans_ephi = vm._getMeansAtOrigin()

originmeans_reference_ephi = [0.0, -5.821362447078282e-07, 1.2809847005002514e-06, 6.283653225057536e-07, 1.6482102010082626e-07, 1.7435539236190487e-06, -1.1990810999445028e-06, -1.7719621779482903e-06, 8.292421902932186e-07, 3.468365213003126e-08]


for om, omr in zip(originmeans_ephi, originmeans_reference_ephi):
    if om != omr:
        print("Test failed for e_phi.")
        print("New: [" + ", ".join(str(a) for a in originmeans_ephi) + "]")
        print("Ref: [" + ", ".join(str(a) for a in originmeans_reference_ephi) + "]")
        exit(1)


print("Test passed.")
