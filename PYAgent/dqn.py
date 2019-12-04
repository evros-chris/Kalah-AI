# define a dqn agent here
import math
import random
from collections import namedtuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T

from agent import RandomAgent


# structure of dqn policy_net and target_net
class DQN(nn.Module):
    def __init__(self, rows, cols):
        super().__init__()

        # input is the board matrix
        self.fc1 = nn.Linear(in_features=rows * cols, out_features=128)
        self.linear1_dropout = nn.Dropout(p=0.2)
        self.fc2 = nn.Linear(in_features=128, out_features=256)
        self.linear2_dropout = nn.Dropout(p=0.2)
        self.fc3 = nn.Linear(in_features=256, out_features=512)
        self.linear3_dropout = nn.Dropout(p=0.2)
        self.out = nn.Linear(in_features=512, out_features=7)

    def forward(self, start_point):
        t = start_point.flatten(start_dim=1)
        t = F.relu(self.linear1_dropout(self.fc1(t)))
        t = F.relu(self.linear2_dropout(self.fc2(t)))
        t = F.relu(self.linear3_dropout(self.fc3(t)))
        t = self.out(t)
        return t


# Experience
Experience = namedtuple(
    'Experience',
    ('state', 'action', 'next_state', 'reward'),
)


# Replay Memory
class ReplayMemory():
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.exp_count = 0

    def exp_save(self, experience):
        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.exp_count % self.capacity] = experience
        self.exp_count += 1

    # randomly pick batch_size experience from replay memory
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)


# the epsilon greedy strategy
class EpsilonGreedyStrategy():
    def __init__(self, start, end, decay):
        # starting, ending, decay values of epsilon
        self.start = start
        self.end = end
        self.decay = decay

    # exponential decay
    def get_exploration_rate(self, current_step):
        return self.end + (self.start - self.end) * \
            math.exp(-1. * current_step * self.decay)


# the agent
class Agent():
    def __init__(self, strategy, num_actions, device):
        self.current_step = 0
        self.strategy = strategy
        self.num_actions = num_actions
        self.device = device

    def select_action(self, state, policy_net, side, kalah):
        rate = self.strategy.get_exploration_rate(self.current_step)
        self.current_step += 1

        possible_moves = RandomAgent().getPossibleMoves(
                    side, kalah
                )
        if rate > random.random():
            # explore
            # choose randomly
            action = RandomAgent().random_move(possible_moves)
            # action = random.randrange(1, self.num_actions)
            return action
        else:
            # exploit
            with torch.no_grad():
                actions = policy_net(torch.unsqueeze(state.to(self.device), 0))
                action = actions.argmax()
                return int(action)+1

    def select_action_valid(self, state, policy_net, side, kalah):
        rate = self.strategy.get_exploration_rate(self.current_step)
        self.current_step += 1

        possible_moves = RandomAgent().getPossibleMoves(
                    side, kalah
                )
        if rate > random.random():
            # explore
            # choose randomly
            action = RandomAgent().random_move(possible_moves)
            # action = random.randrange(1, self.num_actions)
            return action
        else:
            # exploit
            with torch.no_grad():
                actions = policy_net(torch.unsqueeze(state.to(self.device), 0))
                actions = actions.argsort(descending=True).tolist()[0]
                for action in actions:
                    if action+1 in possible_moves:
                        break
                return int(action)+1


def extract_tensors(experiences):
    # convert batch of experiences to experience of batches
    # e.g. experience(1,1,1,1), experience(2,2,2,2) -> experience(1,2),(1,2),(1,2),(1,2)
    batch = Experience(*zip(*experiences))

    states = torch.cat(batch.state)
    actions = torch.cat(batch.action)
    next_states = torch.cat(batch.next_state)
    rewards = torch.cat(batch.reward)

    return (states, actions, next_states, rewards)


# Calculating Q-values
class QValues():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def get_current(policy_net, states, actions):
        # get current q values
        return policy_net(states.to(QValues.device)).gather(dim=1, index=actions.to(QValues.device).unsqueeze(-1))

    @staticmethod
    def get_next(target_net, next_states):
        # final_state_locations = next_states.flatten(start_dim=1) \
        #     .max(dim=1)[0].eq(0).type(torch.bool)
        # non_final_state_locations = (final_state_locations == False)
        # non_final_states = next_states[non_final_state_locations]
        # batch_size = next_states.shape[0]
        # values = torch.zeros(batch_size).to(QValues.device)
        # values[non_final_state_locations] = target_net(non_final_states).max(dim=1)[0].detach()
        # return values
        values = target_net(next_states.to(QValues.device)).max(dim=1)[0].detach()
        return values
