# NeuroMANCER
## Neural Modules with Adaptive Nonlinear Constraints and 	Efficient Regularizations

## [Complete Documentation](https://pnnl.github.io/neuromancer/)
![UML diagram](figs/class_diagram.png)

## Setup

##### Clone and install neuromancer, linear maps, and emulator submodules 
```console

user@machine:~$ mkdir ecosystem; cd ecosystem
user@machine:~$ git clone https://github.com/pnnl/neuromancer.git
user@machine:~$ git clone https://github.com/pnnl/psl.git
user@machine:~$ git clone https://github.com/pnnl/slim.git

# Resulting file structure:
    ecosystem/
        neuromancer/
        psl/
        slim/
```

##### Create the environment via .yml (Linux)

```console
user@machine:~$ conda env create -f env.yml
(neuromancer) user@machine:~$ source activate neuromancer
```

##### If .yml env creation fails create the environment manually

```console
user@machine:~$ conda config --add channels conda-forge pytorch
user@machine:~$ conda create -n neuromancer python=3.7
user@machine:~$ source activate neuromancer
(neuromancer) user@machine:~$ conda install pytorch -c pytorch
(neuromancer) user@machine:~$ conda install scipy pandas matplotlib control pyts numba scikit-learn dill
(neuromancer) user@machine:~$ conda install mlflow boto3 seaborn
(neuromancer) user@machine:~$ conda install -c powerai gym
(neuromancer) user@machine:~$ conda install pytest hypothesis ipykernel cvxpy jupyter notebook 
(neuromancer) user@machine:~$ conda install -c coecms celluloid

```

##### Install neuromancer ecosystem

```console
(neuromancer) user@machine:~$ cd psl
(neuromancer) user@machine:~$ python setup.py develop
(neuromancer) user@machine:~$ cd ../slim
(neuromancer) user@machine:~$ python setup.py develop
(neuromancer) user@machine:~$ cd ../ # into neuromancer
(neuromancer) user@machine:~$ python setup.py develop
```

## Examples
Several tutorials and examples using Neuromancer to solve different parameteric programming problems
can be found in the examples folder. 

## Publications
+ Drgoňa, J., Tuor, A. R., Chandan, V., & Vrabie, D. L. (2021). Physics-constrained deep learning of multi-zone building thermal dynamics. Energy and Buildings, 243, 110992.
+ Tuor, A., Drgona, J., & Vrabie, D. (2020). Constrained neural ordinary differential equations with stability guarantees. arXiv preprint arXiv:2004.10883.
+ Drgona, Jan, et al. "Differentiable Predictive Control: An MPC Alternative for Unknown Nonlinear Systems using Constrained Deep Learning." arXiv preprint arXiv:2011.03699 (2020).
+ E. Skomski, S. Vasisht, C. Wight, A. Tuor, J. Drgoňa and D. Vrabie, "Constrained Block Nonlinear Neural Dynamical Models," 2021 American Control Conference (ACC), 2021, pp. 3993-4000, doi: 10.23919/ACC50511.2021.9482930.
+ Skomski, E., Drgoňa, J., & Tuor, A. (2021, May). Automating Discovery of Physics-Informed Neural State Space Models via Learning and Evolution. In Learning for Dynamics and Control (pp. 980-991). PMLR.
+ Drgoňa, J., Tuor, A., Skomski, E., Vasisht, S., & Vrabie, D. (2021). Deep Learning Explicit Differentiable Predictive Control Laws for Buildings. IFAC-PapersOnLine, 54(6), 14-19.
+ Drgona, J., Skomski, E., Vasisht, S., Tuor, A., & Vrabie, D. (2020). Spectral Analysis and Stability of Deep Neural Dynamics. arXiv preprint arXiv:2011.13492.
+ Drgona, J., Tuor, A., & Vrabie, D. (2020). Constrained physics-informed deep learning for stable system identification and control of unknown linear systems. arXiv preprint arXiv:2004.11184.

## Cite as
```yaml
@article{Neuromancer2022,
  title={{NeuroMANCER: Neural Modules with Adaptive Nonlinear Constraints and Efficient Regularizations}},
  author={Tuor, Aaron and Drgona, Jan and Skomski, Mia},
  Url= {https://github.com/pnnl/neuromancer}, 
  year={2022}
}
```
