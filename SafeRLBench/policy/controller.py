from SafeRLBench import Policy

import numpy as np

import logging

logger = logging.getLogger(__name__)


class NonlinearQuadrocopterController(Policy):
    """Non-linear quadrocopter controller."""

    def __init__(self, zeta_z=0.7, params=[.7, .7, .7, .5, .707],
                 reference=None):
        self._zeta_z = zeta_z
        self._params = params
        self._reference = reference

    def map(self, state):
        ref = self._reference.reference

        # Allocate memory for the 4 outputs of the controller.
        action = np.empty((4,), dtype=np.float32)

        # Retrieve the different parameters and make sure the critical ones
        # are non zero.
        tau_x, tau_y, tau_z, tau_w, zeta = self._params
        if tau_x < 1e-3:
            tau_x = 1e-3
            logger.warning('Parameter `tau_x` too small for controller, '
                           + 'has been clipped to 1e-3"')
        if tau_y < 1e-3:
            tau_y = 1e-3
            logger.warning('Parameter `tau_y` too small for controller, '
                           + 'has been clipped to 1e-3"')
        if zeta < 1e-3:
            zeta = 1e-3
            logger.warning('Parameter `zeta` too small for controller, '
                           + 'has been clipped to 1e-3"')

        # desired acceleration in x and y (global coordinates, [m/s^2] )
        ax = (2. * zeta / tau_x * (ref.vel[0] - state.vel[0])
              + 1. / (tau_x**2) * (ref.pos[0] - state.pos[0]))
        ay = (2. * zeta / tau_y * (ref.vel[1] - state.vel[1])
              + 1. / (tau_y**2) * (ref.pos[1] - state.pos[1]))

        # Normalize by thrust
        thrust = np.linalg.norm(np.array([ax, ay, 9.81 + state.acc[2]]))
        ax /= thrust
        ay /= thrust

        # Rotate desired accelerations into the yaw-rotated inertial frame
        ax_b = ax * np.cos(state.euler[2]) + ay * np.sin(state.euler[2])
        ay_b = -ax * np.sin(state.euler[2]) + ay * np.cos(state.euler[2])

        # Get euler angles from rotation matrix
        action[1] = np.arcsin(-ay_b)
        action[0] = np.arcsin(ax_b / np.cos(action[1]))

        # Z-velocity command m/sec)
        action[2] = (2. * self._zeta_z / tau_z * (ref.vel[2] - state.vel[2])
                     + 1. / (tau_z**2) * (ref.pos[2] - state.pos[2]))

        # Yaw rate command (rad/sec)??
        yaw_err = (np.mod(ref.euler[2] - state.euler[2] + np.pi, 2 * np.pi)
                   - np.pi)
        action[3] = yaw_err / tau_w + ref.omega_b[2]

        return action

    @property
    def parameters(self):
        return self._params

    @parameters.setter
    def parameters(self, params):
        self._params = params

    @property
    def parameter_space(self):
        return None
