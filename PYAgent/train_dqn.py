# training script for dqn agent
import torch
import torch.nn.functional as F
import torch.optim as optim

import dqn
from dqn_engine import KalahEnvManager
from agent import Move

from IPython.display import clear_output

# hyper parameters
num_episodes = 5000
max_steps = 200
batch_size = 256
gamma = 0.9
eps_start = 0.9
eps_end = 0.05
eps_decay = 0.001
# how often update the target net: 1000(OpenAI) or 10000(DeepMind)
# too small may make training unstable
target_update = 1000
memory_size = 3000
lr = 1e-5  # learning rate

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
loss = None
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
        is_game_over, next_state, reward = env.make_move(move)
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
            optimizer.zero_grad()  # clear previous gradients
            loss.backward()  # back prop, calculate gradients
            optimizer.step()  # update weights
        
        # stop episode if game is over
        if is_game_over:
            dqn_win, final_score = env.winner()
            if dqn_win:
                wins += 1
            break

    # synchronize the target_net
    if episode % target_update == 0:
        target_net.load_state_dict(policy_net.state_dict())
    
    # print current winning rate
    dqn_win, final_score = env.winner()
    winning_rate = wins / num_played
    clear_output(wait=True)
    print("episode: " + str(episode))
    print("DQN scores: " + str(final_score))
    print("winning rate: " + str(winning_rate))
    print("loss: " + str(loss))

torch.save(policy_net.state_dict(), "dqn_model")