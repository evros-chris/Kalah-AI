# testing script for dqn agent
import torch

import dqn
from env_manager import KalahEnvManager
from agent import Move
from kalah import Side

num_episodes = 1
wins = 0
num_played = 0

env = KalahEnvManager('java -jar Agents/JimmyPlayer.jar', 'cpu', Side.SOUTH)
strategy = dqn.EpsilonGreedyStrategy(0, 0, 0)
agent = dqn.Agent(strategy=strategy, num_actions=7, device='cpu')

policy_net = dqn.DQN(2, 7)
policy_net.load_state_dict(torch.load("dqn_model", map_location=torch.device('cpu')))
policy_net.eval()


for episode in range(num_episodes):
    env.reset()
    num_played += 1
    illegal_moves = 0
    side = env.side
    state = env.get_state()
    while 1:
        # DQN select a move according to policy_net
        side = env.get_side()
        move = agent.select_action_valid(state, policy_net, side, env.kalah)
        move = Move(side, move)
        if env.kalah.isLegalMove(move) == False:
            illegal_moves += 1
            break

        # DQN makes a move
        reward = env.take_action(move)
        is_game_over = env.done
        next_state = env.get_state()

        # update current state
        state = next_state

        # stop episode if game is over
        if is_game_over:
            dqn_win, final_score = env.winner()
            if dqn_win:
                wins += 1
            break
    
    # print current winning rate
    if episode % 100 == 0:
        dqn_win, final_score = env.winner()
        winning_rate = wins / num_played
        print("episode: " + str(episode))
        print("DQN scores: " + str(final_score))
        print("winning rate: " + str(winning_rate))

print("Overall winning rate: " + str(winning_rate))
