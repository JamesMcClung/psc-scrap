import bgk

loader = bgk.Loader("/mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/exact/B01.00-n256", engine="pscadios2", species_names=["e", "i"])
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


print("Test passed.")
