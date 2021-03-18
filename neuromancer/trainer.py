"""

"""
from copy import deepcopy

import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np

from neuromancer.loggers import BasicLogger
from neuromancer.visuals import Visualizer
from neuromancer.problem import Problem
from neuromancer.datasets import Dataset
from neuromancer.simulators import Simulator
from neuromancer.callbacks import SysIDCallback


class Trainer:
    """
    Class encapsulating boilerplate PyTorch training code. Training procedure is somewhat
    extensible through methods in Callback objects associated with training and evaluation
    waypoints.
    """
    def __init__(
        self,
        problem: Problem,
        dataset: Dataset,
        optimizer: torch.optim.Optimizer,
        logger: BasicLogger = None,
        callback=SysIDCallback(),
        lr_scheduler=False,
        epochs=1000,
        patience=5,
        warmup=0,
        train_metric="nstep_train_loss",
        eval_metric="loop_dev_loss",
        eval_mode="min",
        clip=100.0,
    ):
        """

        :param problem: Object which defines multi-objective loss function and computational graph
        :param dataset: Batched (over chunks of time if sequence data) dataset for non-stochastic gradient descent
        :param optimizer: Pytorch optimizer
        :param logger: Object for logging results
        :param epochs: (int) Number of epochs to train
        :param patience: (int) Number of epochs to allow no improvement before early stopping
        :param warmup: (int) How many epochs to wait before enacting early stopping policy
        :param eval_metric: (str) Performance metric for model selection and early stopping
        """
        self.model = problem
        self.optimizer = optimizer
        self.dataset = dataset
        self.callback = callback
        self.logger = logger
        self.epochs = epochs
        self.logger.log_weights(self.model)
        self.train_metric = train_metric
        self.eval_metric = eval_metric
        self._eval_min = eval_mode == "min"
        self.lr_scheduler = (
            ReduceLROnPlateau(self.optimizer, mode="min", factor=0.5)
            if lr_scheduler
            else None
        )
        self.patience = patience
        self.warmup = warmup
        self.badcount = 0
        self.clip = clip
        self.best_devloss = np.finfo(np.float32).max if self._eval_min else 0.
        self.best_model = deepcopy(self.model.state_dict())

    def train(self):
        """
        Optimize model according to train_metric and validate per-epoch according to eval_metric.
        Trains for self.epochs and terminates early if self.patience threshold is exceeded.
        """
        for i in range(self.epochs):
            output = {}
            self.callback.begin_epoch(self, output)

            self.model.train()
            output = {**output, **self.model(self.dataset.train_data)}
            self.optimizer.zero_grad()
            output[self.train_metric].backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip)
            self.optimizer.step()

            if self.lr_scheduler is not None:
                self.lr_scheduler.step(output[self.train_metric])

            self.callback.pre_eval(self, output)

            with torch.no_grad():
                self.model.eval()
                output = {**output, **self.model(self.dataset.dev_data)}

                self.callback.begin_eval(self, output) # potential simulator

                if (self._eval_min and output[self.eval_metric] < best_devloss)
                        or (not self._eval_min and output[self.eval_metric] > best_devloss):
                    best_model = deepcopy(self.model.state_dict())
                    best_devloss = output[self.eval_metric]
                    self.badcount = 0
                else:
                    if i > self.warmup:
                        self.badcount += 1
                self.logger.log_metrics(output, step=i)

                self.callback.end_eval(self, output) # visualizations

            if self.badcount > self.patience:
                break

        self.callback.end_train(self, output) # write training visualizations

        self.logger.log_artifacts({
            f"{self.logger.args.system}_best_model_state_dict.pth": best_model,
            f"{self.logger.args.system}_best_model.pth": self.model,
        })
        return best_model

    def evaluate(self, best_model):
        """
        Evaluate the model on all data splits.
        """
        self.model.load_state_dict(best_model)
        self.model.eval()

        all_output = {}

        with torch.no_grad():
            self.callback.begin_test(self, all_output)  # setup simulator

            splits = [
                self.dataset.train_data,
                self.dataset.dev_data,
                self.dataset.test_data,
            ]
            for dset, dname in zip(splits, ["train", "dev", "test"]):
                all_output = {**all_output, **self.model(dset)}

            self.callback.end_test(self, all_output)    # simulator/visualizations/output concat

        self.logger.log_metrics({f"best_{k}": v for k, v in all_output.items()})

        return all_output


def freeze_weight(problem, module_names=['']):
    """
    ['parent->child->child']
    :param component:
    :param module_names:
    :return:
    """
    modules = dict(problem.named_modules())
    for name in module_names:
        freeze_path = name.split('->')
        if len(freeze_path) == 1:
            modules[name].requires_grad_(False)
        else:
            parent = modules[freeze_path[0]]
            freeze_weight(parent, ['->'.join(freeze_path[1:])])


def unfreeze_weight(problem, module_names=['']):
    """
    ['parent->child->child']
    :param component:
    :param module_names:
    :return:
    """
    modules = dict(problem.named_modules())
    for name in module_names:
        freeze_path = name.split('->')
        if len(freeze_path) == 1:
            modules[name].requires_grad_(True)
        else:
            parent = modules[freeze_path[0]]
            freeze_weight(parent, ['->'.join(freeze_path[1:])])
