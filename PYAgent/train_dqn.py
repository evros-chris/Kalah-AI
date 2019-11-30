# training script for dqn agent
import torch
import torch.nn.functional as F
import torch.optim as optim

import dqn
from dqn_engine import KalahEnvManager
from agent import Move

# hyper parameters
num_episodes = 1000
max_steps = 100
batch_size = 256
gamma = 0.999
eps_start = 1
eps_end = 0.01
eps_decay = 0.001
target_update = 10
memory_size = 100000
lr = 0.001  # learning rate

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(device)
strategy = dqn.EpsilonGreedyStrategy(eps_start, eps_end, eps_decay)
agent = dqn.Agent(strategy=strategy, num_actions=7, device=device)
memory = dqn.ReplayMemory(memory_size)

# build neural networks
policy_net = dqn.DQN(rows=2, cols=7).to(device)
target_net = dqn.DQN(rows=2, cols=7).to(device)

target_net.load_state_dict(policy_net.state_dict())
target_net.eval()  # this network is not for training

optimizer = optim.Adam(params=policy_net.parameters(), lr=lr)

env = KalahEnvManager(device)
wins = 0
num_played = 0
for episode in range(num_episodes):
    num_played += 1
    env.reset()
    side, state, reward = env.get_initial_state()
    # print(state)
    for step in range(max_steps):
        # DQN select a move according to policy_net
        move = agent.select_action(state, policy_net)
        move = Move(env.dqn_side, move)
        # DQN makes a move
        next_state, reward = env.make_move(move)
        # save in memory
        memory.exp_save(dqn.Experience(torch.unsqueeze(state, 0), torch.LongTensor([move.getHole()-1]), torch.unsqueeze(next_state, 0), torch.Tensor([reward])))
        # update current state
        state = next_state
        # Memory replay
        if memory.exp_count >= batch_size:
            experiences = memory.sample(batch_size)
            states, actions, next_states, rewards = dqn.extract_tensors(
                experiences
            )
            current_q_values = dqn.QValues.get_current(
                policy_net, states, actions
            )
            next_q_values = dqn.QValues.get_next(target_net, next_states)
            target_q_values = (next_q_values * gamma) + rewards

            # gradient descent: update weights
            loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
            # print("loss: " + str(loss))
            optimizer.zero_grad()  # clear previous gradients
            loss.backward()  # back prop, calculate gradients
            optimizer.step()  # update weights

        # synchronize the target_net
        if episode % target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())

        # stop episode if game is over
        if env.is_gameover():
            if env.winner():
                wins += 1
            break

    # print current winning rate
    dqn_win, final_score = env.winner()
    if dqn_win:
        wins += 1
    winning_rate = wins / num_played
    print("episode: " + str(episode))
    print("DQN scores: " + str(final_score))
    print("winning rate: " + str(winning_rate))
