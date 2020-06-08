"""
Loading system ID datasets from mat files
"""
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
import torch

import plot
import emulators


def min_max_norm(M):
    """
    :param M:
    :return:
    """
    M_norm = (M - M.min(axis=0).reshape(1, -1)) / (M.max(axis=0) - M.min(axis=0)).reshape(1, -1)
    return np.nan_to_num(M_norm)


#  TODO: save trained benchmark models from Matlab's System ID
#  TODO: write function to load csv files pre defined format as well
#  frame= load_data_sysID(file_path, type='csv') AT note: better to check file extension than add argument
#  make data generation based on pandas df as inputs
#  Data_sysID(identifier='pandas', data_file='frame', norm)
def load_data_from_matlab(file_path='./datasets/NLIN_SISO_two_tank/NLIN_two_tank_SISO.mat'):
    """
    :param file_path: path to .mat file with dataset: y,u,d,Ts
    :return:
    """
    file = loadmat(file_path)
    Y = file.get("y", None)  # outputs
    U = file.get("u", None)  # inputs
    D = file.get("d", None)  # disturbances

    # Ts = file.get("Ts", None)  # sampling time
    print(Y.shape)
    return Y, U, D


def load_data_from_emulator(system='building_small', nsim=1000, ninit=0):
    #  dataset creation from the emulator
    systems = {'building_small': emulators.Building_hf_Small,
               'building_ROM': emulators.Building_hf_ROM,
               'building_large': emulators.Building_hf}
    building = systems[system]()  # instantiate building class
    building.parameters()  # load model parameters
    M_flow = emulators.Periodic(nx=building.n_mf, nsim=nsim, numPeriods=6, xmax=building.mf_max, xmin=building.mf_min,
                                form='sin')
    DT = emulators.Periodic(nx=building.n_dT, nsim=nsim, numPeriods=9, xmax=building.dT_max, xmin=building.dT_min,
                            form='cos')
    D = building.D[ninit:nsim, :]
    U, X, Y = building.simulate(ninit, nsim, M_flow, DT, D)
    plot.pltOL(Y, U=U, D=D, X=X)
    plt.savefig('test.png')
    return Y, U, D


def batch_data(data, nsteps):
    """

    :param data: np.array shape=(total_time_steps, dim)
    :param nsteps: (int) n-step prediction horizon
    :return: torch.tensor shape=(nbatches, nsteps, dim)
    """
    nsplits = (data.shape[0]) // nsteps
    leftover = (data.shape[0]) % nsteps
    data = np.stack(np.split(data[:data.shape[0] - leftover], nsplits))  # nchunks X nsteps X 14
    return torch.tensor(data, dtype=torch.float32).transpose(0, 1)  # nsteps X nsamples X nfeatures


def unbatch_data(data):
    return data.transpose(0, 1).reshape(-1, 1, data.shape[-1])


def split_train_test_dev(data):
    """
    exemplary use:
    # Yp_train, Yp_dev, Yp_test = split_train_test_dev(Yp)
    # Yf_train, Yf_dev, Yf_test = split_train_test_dev(Yf)
    """
    if data is not None:
        train_idx = (data.shape[1] // 3)
        dev_idx = train_idx * 2
        train_data = data[:, :train_idx, :]
        dev_data = data[:, train_idx:dev_idx, :]
        test_data = data[:, dev_idx:, :]
    else:
        train_data, dev_data, test_data = None, None, None
    return train_data, dev_data, test_data


def make_dataset_ol(Y, U, D, nsteps, device):
    """
    creates dataset for open loop system
    :param U: inputs
    :param Y: outputs
    :param nsteps: future windos (prediction horizon)
    :param device:
    :param norm:
    :return:
    """

    # Outputs: data for past and future moving horizons
    Yp, Yf = [batch_data(Y[:-nsteps], nsteps).to(device), batch_data(Y[nsteps:], nsteps).to(device)]
    # Inputs: data for past and future moving horizons
    Up = batch_data(U[:-nsteps], nsteps).to(device) if U is not None else None
    Uf = batch_data(U[nsteps:], nsteps).to(device) if U is not None else None
    # Disturbances: data for past and future moving horizons
    Dp = batch_data(D[:-nsteps], nsteps).to(device) if D is not None else None
    Df = batch_data(D[nsteps:], nsteps).to(device) if D is not None else None
    print(f'Yp shape: {Yp.shape} Yf shape: {Yf.shape} Up shape: {Up.shape} Uf shape: {Uf.shape}')
    return Yp, Yf, Up, Uf, Dp, Df


def make_dataset_cl(Y, U, D, R, nsteps, device):
    """
    creates dataset for closed loop system
    :param U: inputs
    :param Y: outputs
    :param nsteps: future windos (prediction horizon)
    :param device:
    :param norm:
    :return:
    """
    Yp, Yf, Up, Uf, Dp, Df = make_dataset_ol(Y, U, D, nsteps, device)
    Rf = batch_data(R[nsteps:], nsteps).to(device) if R is not None else None
    return Yp, Yf, Up, Dp, Df, Rf


def data_setup(args, device):

    if args.system_data == 'datafile':
        Y, U, D = load_data_from_matlab(file_path=args.datafile)  # load data from file
    elif args.system_data == 'emulator':
        Y, U, D = load_data_from_emulator(system=args.datafile, nsim=args.nsim)

    U = min_max_norm(U) if ('U' in args.norm and U is not None) else None
    Y = min_max_norm(Y) if ('Y' in args.norm and Y is not None) else None
    D = min_max_norm(D) if ('D' in args.norm and D is not None) else None

    print(f'Y shape: {Y.shape}')
    plot.pltOL(Y, U=U, D=D)
    plt.savefig('test.png')
    # system ID or time series dataset
    Yp, Yf, Up, Uf, Dp, Df = make_dataset_ol(Y, U, D, nsteps=args.nsteps, device=device)
    train_data = [split_train_test_dev(data)[0] for data in [Yp, Yf, Up, Uf, Dp, Df]]
    dev_data = [split_train_test_dev(data)[1] for data in [Yp, Yf, Up, Uf, Dp, Df]]
    test_data = [split_train_test_dev(data)[2] for data in [Yp, Yf, Up, Uf, Dp, Df]]

    nx, ny = Y.shape[1]*args.nx_hidden, Y.shape[1]
    nu = U.shape[1] if U is not None else 0
    nd = D.shape[1] if D is not None else 0

    return train_data, dev_data, test_data, nx, ny, nu, nd


if __name__ == '__main__':
    datapaths = ['./datasets/NLIN_SISO_two_tank/NLIN_two_tank_SISO.mat',
                 # './datasets/NLIN_SISO_predator_prey/PredPreyCrowdingData.mat',
                 # './datasets/NLIN_TS_pendulum/NLIN_TS_Pendulum.mat',
                 './datasets/NLIN_MIMO_vehicle/NLIN_MIMO_vehicle3.mat',
                 './datasets/NLIN_MIMO_CSTR/NLIN_MIMO_CSTR2.mat',
                 './datasets/NLIN_MIMO_Aerodynamic/NLIN_MIMO_Aerodynamic.mat']

    for name, path in zip(['twotank', 'vehicle', 'reactor', 'aero'], datapaths):
        Y, U, D = load_data_from_matlab(path)
        plot.pltOL(Y, U=U, D=D, figname='test.png')

        Yp, Yf, Up, Uf, Dp, Df = make_dataset_ol(Y, U, D, nsteps=32, device='cpu')
        plot.pltOL(np.concatenate([Yp[:, k, :] for k in range(Yp.shape[1])])[:1000],
                   Ytrain=np.concatenate([Yf[:, k, :] for k in range(Yf.shape[1])])[:1000], figname=f'{name}_align_test.png')

        R = np.ones(Y.shape)
        Yp, Yf, Up, Dp, Df, Rf = make_dataset_cl(Y, U, D, R, nsteps=5, device='cpu')


#   TESTING dataset creation from the emulator
    ninit = 0
    nsim = 1000
    building = emulators.Building_hf()   # instantiate building class
    building.parameters()      # load model parameters
    # generate input data
    M_flow = emulators.Periodic(nx=building.n_mf, nsim=nsim, numPeriods=6, xmax=building.mf_max, xmin=building.mf_min, form='sin')
    DT = emulators.Periodic(nx=building.n_dT, nsim=nsim, numPeriods=9, xmax=building.dT_max, xmin=building.dT_min, form='cos')
    D = building.D[ninit:nsim,:]
    # simulate open loop building
    U, X, Y = building.simulate(ninit, nsim, M_flow, DT, D)
    # plot trajectories
    plot.pltOL(Y=Y, U=U, D=D, X=X)
    # create datasets
    Yp, Yf, Up, Uf, Dp, Df = make_dataset_ol(Y, U, D, nsteps=12, device='cpu')
    R = 25*np.ones(Y.shape)
    Yp, Yf, Up, Dp, Df, Rf = make_dataset_cl(Y, U, D, R, nsteps=12, device='cpu')
    print(Yp.shape, Yf.shape, Up.shape, Dp.shape, Df.shape)

