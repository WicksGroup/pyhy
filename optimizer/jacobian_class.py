import os
import json
import configparser
from tools.hyades_reader import HyadesOutput, ShockVelocity


class Jacobian:

    def __init__(self, run_name):
        """Set up run_name, experimental data, optimization_json, and config file"""
        path = os.path.join('..', 'data')
        self.run_name = run_name

        pass

    def jacobian(self, pressure):
        """Returns the partial derivative in each dimension"""
        inf_names = self.write_infs(pressure)
        self.run_in_parallel(inf_names)
        residual = self.calculate_residual(inf_names)

    def write_infs(self, pressure):
        """Write an inf for each point in pressure

        Args:
            pressure:

        Returns:
            inf_names (list): the names of each inf written

        """
        inf_names = []
        return inf_names

    def run_in_parallel(self, inf_names):
        """Runs all inf_names in parallel

        Args:
            inf_names:
        """
        pass

    def calculate_residual(self, run_names):
        """

        Args:
            run_names:

        Returns:
            residual (numpy array): An array of the partial derivative in each dimension
        """
        pass
