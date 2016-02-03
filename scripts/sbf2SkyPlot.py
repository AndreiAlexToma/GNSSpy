#!/usr/bin/env python

import sys
import os
import numpy as np
import argparse
from matplotlib.pyplot import show

from SSN import sbf2stf
from GNSS import gpstime
from Plot import plotElevAzim

__author__ = 'amuls'


# exit codes
E_SUCCESS = 0
E_FILE_NOT_EXIST = 1
E_NOT_IN_PATH = 2
E_UNKNOWN_OPTION = 3
E_TIME_PASSED = 4
E_WRONG_OPTION = 5
E_SIGNALTYPE_MISMATCH = 6
E_DIR_NOT_EXIST = 7
E_FAILURE = 99

# # get startup path
# ospath = sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "subfolder"))
# print sys.argv[0], ospath


def treatCmdOpts(argv):
    """
    Treats the command line options

    Parameters:
      argv          the options (without argv[0]

    Sets the global variables according to the CLI args
    """
    helpTxt = os.path.basename(__file__) + ' plots the SkyView from PRS data'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-f','--file', help='Name of SBF file',required=True)
    parser.add_argument('-d', '--dir', help='Directory of SBF file (defaults to .)', required=False, default='.')
    parser.add_argument('-o','--overwrite', help='overwrite intermediate files (default False)', action='store_true', required=False)
    parser.add_argument('-v', '--verbose', help='displays interactive graphs and increase output verbosity (default False)', action='store_true', required=False)
    args = parser.parse_args()

    # # show values
    # print('SBFFile: %s' % args.file)
    # print('dir = %s' % args.dir)
    # print('verbose: %s' % args.verbose)
    # print('overwrite: %s' % args.overwrite)

    return args.file, args.dir, args.overwrite, args.verbose


if __name__ == "__main__":
    # treat command line options
    nameSBF, dirSBF, overwrite, verbose = treatCmdOpts(sys.argv)

    # change to the directory dirSBF if it exists
    workDir = os.getcwd()
    if dirSBF is not '.':
        workDir = os.path.normpath(os.path.join(workDir, dirSBF))

    # print('workDir = %s' % workDir)
    if not os.path.exists(workDir):
        sys.stderr.write('Directory %s does not exists. Exiting.\n' % workDir)
        sys.exit(E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)

    # print('curDir = %s' % os.getcwd())
    # print('SBF = %s' % os.path.isfile(nameSBF))

    # check whether the SBF datafile exists
    if not os.path.isfile(nameSBF):
        sys.stderr.write('SBF datafile %s does not exists. Exiting.\n' % nameSBF)
        sys.exit(E_FILE_NOT_EXIST)

    # execute the conversion sbf2stf needed
    SBF2STFOPTS = ['ChannelStatus_1']     # options for conversion, ORDER IMPORTANT!!
    sbf2stfConverted = sbf2stf.runSBF2STF(nameSBF, SBF2STFOPTS, overwrite, verbose)

    for option in SBF2STFOPTS:
        # print('option = %s - %d' % (option, SBF2STFOPTS.index(option)))
        if option == 'ChannelStatus_1':
            # read the MeasEpoch data into a numpy array
            dataChanSt = sbf2stf.readChannelStatus(sbf2stfConverted[SBF2STFOPTS.index(option)], verbose)
        else:
            print('  wrong option %s given.' % option)
            sys.exit(E_WRONG_OPTION)

    print('dataChanSt = %s' % dataChanSt)
    print('dataChanSt[0] = %s' % dataChanSt[0])

    # determine current weeknumber and subsequent date from SBF data
    WkNr = int(dataChanSt['CHST_WNC'][0])
    dateString = gpstime.UTCFromWT(WkNr, float(dataChanSt['CHST_TOW'][0])).strftime("%d/%m/%Y")
    if verbose:
        print('WkNr = %d - dateString = %s' % (WkNr, dateString))

    # create subset with only valid elevation angles
    indexValid = sbf2stf.findValidElevation(dataChanSt['CHST_Elevation'], verbose)
    dataChanStValid = dataChanSt[indexValid]

    # find the list of SVIDs with valid elev/azim data
    SVIDs = sbf2stf.observedSatellites(dataChanStValid['CHST_SVID'], verbose)

    # extract for each satellite the elevation and azimuth angles
    prnElev = []
    prnAzim = []
    prnHour = []
    prnHourElev = []
    prnHourAzim = []
    for i, PRN in enumerate(SVIDs):
        print('PRN = %d' % PRN)
        indexPRN = sbf2stf.indicesSatellite(PRN, dataChanStValid['CHST_SVID'], verbose)
        prnElev.append(dataChanStValid[indexPRN]['CHST_Elevation'])
        prnAzim.append(dataChanStValid[indexPRN]['CHST_Azimuth'])

        # retain only multiples of hours to display
        prnTime = dataChanStValid[indexPRN]['CHST_TOW']
        indexHour = np.where(np.fmod(prnTime, 3600.) == 0)
        # print('indexHour = %s' % indexHour)
        prnHour.append(prnTime[indexHour])
        prnHourElev.append(dataChanStValid[indexPRN]['CHST_Elevation'][indexHour])
        prnHourAzim.append(dataChanStValid[indexPRN]['CHST_Azimuth'][indexHour])

        # print('PRN = %d - prnElev = %s' % (PRN, prnElev[-1]))
        # print('PRN = %d - prnAzim = %s' % (PRN, prnAzim[-1]))
        # print('PRN = %d - prnHour = %s' % (PRN, prnHour[-1]))
        # print('PRN = %d - prnHourElev = %s' % (PRN, prnHourElev[-1]))
        # print('PRN = %d - prnHourAzim = %s' % (PRN, prnHourAzim[-1]))

    fig = plotElevAzim.skyview(SVIDs, prnAzim, prnElev, dateString, prnHour, prnHourAzim, prnHourElev)
    pTime = gpstime.UTCFromWT(WkNr, float(dataChanSt['CHST_TOW'][0]))
    print('pTime Y = %s' % pTime.strftime('%Y'))
    print('pTime m = %s' % pTime.strftime('%m'))
    print('pTime d = %s' % pTime.strftime('%d'))

    dateString = gpstime.UTCFromWT(WkNr, float(dataChanSt['CHST_TOW'][0])).strftime("%Y-%m-%d")
    print('dateString = %s' % dateString)
    fig.savefig('%s-skyview.png' % dateString, dpi=90)
    print('dpi = %d' % fig.dpi)

    # show the plot
    show()
