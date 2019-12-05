import torch

from kalah import Side
from kalah_env import KalahEnv


class KalahEnvManager():
    """
    Game engine for dqn training.
    """
    def __init__(self, op_command, device, side=Side.SOUTH):
        self.env = KalahEnv(op_command, side)
        self.env.reset()
        self.device = device
        self._state = self.env.get_state()
        self.done = False

    def reset(self):
        """
        Reset the game to the starting state.
        """
        self.env.reset()
        self._state = self.env.get_state()

    def get_state(self):
        """
        Get the current state of the environment as a PyTorch Tensor.
        """
        return torch.Tensor(self._state)

    def take_action(self, move):
        """
        Make a move in the env and return next state and reward back to the
        agent.
        """
        self._state, reward, self.done, _ = self.env.step(move)
        return reward

    def winner(self):
        """
        Check if we won the game.
        """
        final_score = self.env.get_score()
        if final_score > 0:
            return True, final_score
        return False, final_score
