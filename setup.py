from setuptools import setup, find_packages

setup(name='neuromancer',
      version=1.0,
      description='Neural Modules with Adaptive Nonlinear Constraints and Efficient Regularization',
      url='https://pnnl.github.io/neuromancer/',
      author='Aaron Tuor, Jan Drgona, Elliott Skomski',
      author_email='aaron.tuor@pnnl.gov',
      license='GPL3',
      packages=find_packages(),
      zip_safe=False,
      classifiers=['Programming Language :: Python'],
      keywords=['Deep Learning', 'Pytorch', 'Linear Models', 'Dynamical Systems', 'Data-driven control'])