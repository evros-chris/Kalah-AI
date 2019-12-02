# training script for dqn agent
import torch
import torch.nn.functional as F
import torch.optim as optim

import dqn
from dqn_engine import KalahEnvManager
from agent import Move

from IPython.display import clear_output

# hyper parameters
num_episodes = 3000
max_steps = 200
batch_size = 256
gamma = 0.9
eps_start = 0.9
eps_end = 0.05
eps_decay = 0.0001
# how often update the target net: 1000(OpenAI) or 10000(DeepMind)
# too small may make training unstable
target_update = 10000
memory_size = 5000
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
avg_score = 0
illegal_moves = 0
loss = None
steps = 0
for episode in range(1, num_episodes+1):
    num_played += 1
    env.reset()
    is_game_over = False
    illegal = False
    side, state, reward = env.get_initial_state()
    # print(state)
    for step in range(max_steps):
        steps += 1
        # DQN select a move according to policy_net
        move = agent.select_action_valid(state, policy_net, side, env.kalah)
        move = Move(env.dqn_side, move)
        if env.kalah.isLegalMove(move) == False:
            illegal_moves += 1
            is_game_over = True
            illegal = True
            next_state = state
            reward = -1000
        else:    
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
            target_q_values = (next_q_values * gamma) + rewards.to(device)

            # gradient descent: update weights
            loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
            optimizer.zero_grad()  # clear previous gradients
            loss.backward()  # back prop, calculate gradients
            optimizer.step()  # update weights
        
        # synchronize the target_net
        # if steps % target_update == 0:
        #     target_net.load_state_dict(policy_net.state_dict())
        
        # stop episode if game is over
        if is_game_over:
            dqn_win, final_score = env.winner()
            if dqn_win == True and illegal == False:
                wins += 1
            break
    
    dqn_win, final_score = env.winner()
    if illegal:
        final_score = -1000
    avg_score += final_score
    
    if episode % 100 == 0:
        # print current winning rate
        avg_score /= num_played
        winning_rate = wins / num_played
        clear_output(wait=True)
        print("episode: " + str(episode-99) + '-' + str(episode))
        print("DQN avg scores: " + str(avg_score))
        print("winning rate(past 100 games): " + str(winning_rate))
        print("illegal moves: " + str(illegal_moves))
        print("loss: " + str(loss))
        wins = 0
        num_played = 0
        illegal_moves = 0

torch.save(policy_net.state_dict(), "dqn_model")