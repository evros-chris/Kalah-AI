# testing script for dqn agent
import torch

import dqn
from dqn_engine import KalahEnvManager
from agent import Move

num_episodes = 1000
wins = 0
num_played = 0
eps_start = 0
eps_end = 0
eps_decay = 0.001

env = KalahEnvManager("cpu")
strategy = dqn.EpsilonGreedyStrategy(eps_start, eps_end, eps_decay)
agent = dqn.Agent(strategy=strategy, num_actions=7, device='cpu')

policy_net = dqn.DQN(2, 7)
policy_net.load_state_dict(torch.load("dqn_model"))
policy_net.eval()

for episode in range(num_episodes):
    env.reset()
    num_played += 1
    side, state, reward = env.get_initial_state()
    while 1:
        # DQN select a move according to policy_net
        move = agent.select_action(state, policy_net)
        move = Move(env.dqn_side, move)
        # DQN makes a move
        is_game_over, next_state, reward = env.make_move(move)
        # update current state
        state = next_state

        # stop episode if game is over
        if is_game_over:
            dqn_win, final_score = env.winner()
            if dqn_win:
                wins += 1
            break
    
    # print current winning rate
    dqn_win, final_score = env.winner()
    winning_rate = wins / num_played
    print("episode: " + str(episode))
    print("DQN scores: " + str(final_score))
    print("winning rate: " + str(winning_rate))

print("Overall winning rate: " + str(winning_rate))