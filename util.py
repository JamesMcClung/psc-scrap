import xarray as xr
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm

_lengths = {1:(1., .03, .03), 10:(1., .02, .02), .1:(1., .18, .18)}
_centerSlices = {10:slice(-.001, .001), 1:slice(-.003, .003), 0.1:slice(-.03, .03)}
_engine = "pscadios2"
_species_names = ['e', 'i']

def subtract(list1, list2):
    return [a1 - a2 for a1, a2 in zip(list1, list2)]

def norm(x):
    return xr.apply_ufunc(np.linalg.norm, x, input_core_dims=[['y', 'z']])

# fuzz: once a lmin is found, explore a radius of <fuzz> for potentially lower points, and keep going if any are found
def get_bounding_lmins_idxs(data, idx, fuzz=1):
    ilower = idx+1 # if idx is an lmin, it will count as the lower lmin
    i = 1
    foundDownhill = False
    while i <= fuzz:
        if ilower < i:
            ilower = ilower if foundDownhill else None
            break
        if ilower == len(data) or data[ilower - i] < data[ilower]:
            foundDownhill = True
            ilower -= i
            i = 1
        elif foundDownhill:
            i += 1
        else:
            ilower -= 1
        
    iupper = idx
    i = 1
    foundDownhill = False
    while i <= fuzz:
        if iupper + i >= len(data):
            iupper = iupper if foundDownhill else None
            break
        if data[iupper + i] < data[iupper]:
            foundDownhill = True
            iupper += i
            i = 1
        elif foundDownhill:
            i += 1
        else:
            iupper += 1

    return ilower, iupper

def get_lmin_idxs(data, fuzz=1):
    lmis = [0]
    while not lmis[-1] is None and lmis[-1] < len(data):
        lmis.append(get_bounding_lmins_idxs(data, lmis[-1], fuzz)[1])
    return [lm for lm in lmis if not lm is None]

        
class DataParams:
    def __init__(self, title, vmin, vmax, colors, fileName, varName, coef=1, skipFirst=False, combine="magnitude"):
        self.title = title
        self.vmin = vmin
        self.vmax = vmax
        self.colors = colors
        self.fileName = fileName
        self.varName = varName
        self.coef = coef
        self.skipFirst = skipFirst
        self.combine = combine

class Run:
    def __init__(self, case, B, resolution, modifier=''):
        self.case = case
        self.B = B
        self.res = resolution
        self.mod = modifier
        
        self.initPLWC()
    
    #### Selecting Run
    def initPLWC(self):
        '''initialize path, length, wholeSlice, centerSlice'''
        self.path = f"/mnt/lustre/IAM851/jm1667/psc-runs/{self.case}/trials/B{self.B}_n{self.res}{self.mod}/"
        self.length = _lengths[self.B]
        self.wholeSlice = slice(-self.length[1]/2, self.length[1]/2)
        self.centerSlice = _centerSlices[self.B]

    #### Determining Run Metaparameters
    def initFMNS(self, nframes):
        '''initialize fields_every, moments_every, nsteps, stepsPerFrame'''
        self.nframes = nframes
        self.fields_every = 200 # old/default value
        self.moments_every = 200 # old/default value
        with open(self.path + "params_record.txt") as records:
            for line in records:
                if line.startswith("nmax"):
                    self.nsteps = int(line.split()[1])
                elif line.startswith("fields_every"):
                    self.fields_every = int(line.split()[1])
                elif line.startswith("moments_every"):
                    self.moments_every = int(line.split()[1])
        self.stepsPerFrame = self.nsteps // nframes
    
    def printMetadata(self):
        print(f"nsteps in sim: {self.nsteps}")
        print(f"nframes in animation = {self.nframes}")
        print(f"steps per frame: {self.stepsPerFrame}")
        print(f"directory to save in: {self.case}/B{self.B}_n{self.res}{self.mod}_{self.nframes}x{self.stepsPerFrame}")
        

    #### Loading Run Data

    def _openFile(self, fileName, step):
        return xr.open_dataset(self.path + f"{fileName}.{str(step).rjust(9,'0')}.bp", length=self.length, engine=_engine, species_names=_species_names)

    def _prepData(_, data):
        return data[0,:,:].transpose()
    
    def _getDataAndTime(self, frameIdx, params):
        if frameIdx == 0 and params.skipFirst:
            file = self._openFile(params.fileName, {'pfd':self.fields_every, 'pfd_moments':self.moments_every}[params.fileName])
        else:
            file = self._openFile(params.fileName, frameIdx*self.stepsPerFrame)

        if isinstance(params.varName, list):
            if params.combine == "magnitude":
                rawData = sum(self._prepData(file.__getattr__(var)) ** 2 for var in params.varName) ** .5
            elif params.combine == "sum":
                rawData = sum(self._prepData(file.__getattr__(var)) for var in params.varName)
            else:
                rawHor = self._prepData(file.__getattr__(params.varName[0]))
                rawVer = self._prepData(file.__getattr__(params.varName[1]))
                rGrid = (rawHor.y **2 + rawHor.z**2)**.5
                horGrid = rawHor.y
                verGrid = rawHor.z
                if params.combine == 'radial':
                    rawData = (rawHor * horGrid + rawVer * verGrid) / rGrid
                elif params.combine == 'azimuthal':
                    rawData = (-rawHor * verGrid + rawVer * horGrid) / rGrid
                rawData = rawData.fillna(0)
        else:
            rawData = self._prepData(file.__getattr__(params.varName))
        return params.coef * rawData, file._attrs['time']
    
    def loadData(self, params):
        self.params = params
        self.datas, self.times = [list(x) for x in zip(*[self._getDataAndTime(frameIdx, params) for frameIdx in range(self.nframes)])]
        
    def sliceData(self, sliceID):
        '''sliceID: 0 for wholeSlice, 1 for centerSlice'''
        self.activeSlice = [self.wholeSlice, self.centerSlice][sliceID]
        self.viewAdj = ['', 'Central '][sliceID]

        self.slicedDatas = [data.sel(y=self.activeSlice, z=self.activeSlice) for data in self.datas]
        self.rGrid = (self.slicedDatas[0].y **2 + self.slicedDatas[0].z**2)**.5
        self._preppedForView = False
        
    def printViewInfo(self):
        print(f"view: {self.viewAdj}= {self.activeSlice}")

    #### Set up color scale
    def _prepForView(self):
        if not self._preppedForView:
            self.vmax = self.params.vmax if not self.params.vmax is None else max(np.nanquantile(data.values, 1) for data in self.slicedDatas)
            self.vmin = self.params.vmin if not self.params.vmin is None else min(np.nanquantile(data.values, 0) for data in self.slicedDatas)
            if self.params.vmax is None and self.params.vmin is None:
                self.vmax = max(self.vmax, -self.vmin)
                self.vmin = -self.vmax
        self._preppedForView = True
    
    #### View a particular frame
    def viewFrame(self, frameIdx):
        self._prepForView()
        fig, ax = plt.subplots()

        im = ax.imshow(self.slicedDatas[frameIdx], cmap=self.params.colors, vmin=self.vmin, vmax=self.vmax, origin='lower', extent=(self.activeSlice.start, self.activeSlice.stop, self.activeSlice.start, self.activeSlice.stop))
        ax.set_xlabel('y')
        ax.set_ylabel('z')
        ax.set_title(self.viewAdj + self.params.title + " (t={:.3f})".format(self.times[frameIdx]))
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
        fig.colorbar(im, ax=ax)

    #### Stability Stuff
    def viewStability(self):
        normsOfDiffs = [norm(data - self.slicedDatas[0]) for data in self.slicedDatas]
        self.lmis = get_lmin_idxs(normsOfDiffs, 2)

        plt.xlabel("Time")
        plt.ylabel("2-Norm of Difference")
        plt.title("Stability of " + self.viewAdj + self.params.title)

        plt.plot(self.times, normsOfDiffs)
        plt.plot([self.times[i] for i in self.lmis], [normsOfDiffs[i] for i in self.lmis], 'go')
        plt.show()
    
    def printLmis(self):
        print("local min indices: " + str(self.lmis))
        
    def prepRadial(self):
        maxR = max(abs(self.activeSlice.start), abs(self.activeSlice.stop)) * 2**.5
        self.rStep = maxR / 100
        self.rs = np.arange(0, maxR, self.rStep)
        
    def getMeansVsRadius(self, frameIdx):
        return np.array([self.slicedDatas[frameIdx].where((r <= self.rGrid) & (self.rGrid < r + self.rStep)).mean().item() for r in self.rs])

    def getStdsVsRadius(self, frameIdx):
        return np.array([self.slicedDatas[frameIdx].where((r <= self.rGrid) & (self.rGrid < r + self.rStep)).std().item() for r in self.rs])
    
    def getMeansVsRadiusesAndTimes(self, indices):
        return [self.getMeansVsRadius(i) for i in indices], [self.times[i] for i in indices]
    
#     untested
    def compareTimes(self, indices, showError=False):
        plt.xlabel("Distance from Axis")
        plt.ylabel(self.params.title)
        plt.title("Mean " + self.params.title + " vs Radius")
        
        if showError:
            for i in indices:
                plt.errorbar(self.rs, self.getMeansVsRadius(i), yerr=self.getStdsVsRadius[i], color=cm.Wistia(1-i/len(indices)), errorevery=(i,len(indices)), elinewidth=1, capsize=1.5, label="t={:.2f}".format(self.times[i]))
        else:
            for i in indices:
                plt.plot(self.rs, self.getMeansVsRadius(i), color=cm.Wistia(1-i/len(indices)), label="t={:.2f}".format(self.times[i]))
        plt.show()
            


