# training script for dqn agent
import torch
import torch.nn.functional as F
import torch.optim as optim

from PyAlpha.neural_nets import MLP, QValues
from PyAlpha.neural_nets import ReplayMemory, extract_tensors, Experience
from PyAlpha.neural_nets import MiniMaxAgent, EpsilonGreedyStrategy
from PyEnv.env_manager import KalahEnvManager
from PyEnv.kalah import Move

from PyEnv.kalah import Side

import time
import sys

from IPython.display import clear_output

# hyper parameters
num_episodes = 300
max_steps = 200

lr = 1e-5  # learning rate
eps_start = 0.9
eps_end = 0.1
eps_decay = 0.001
memory_size = 5000
batch_size = 256

minimax_depth = 5
opponent = "java -jar Agents/JimmyPlayer.jar"
dqn_side = Side.SOUTH
continue_train = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# build neural networks
value_net = MLP(rows=2, cols=8).to(device)
if continue_train:
    value_net.load_state_dict(torch.load("model/max_score"))

strategy = EpsilonGreedyStrategy(eps_start, eps_end, eps_decay)
memory = ReplayMemory(memory_size)

optimizer = optim.Adam(params=value_net.parameters(), lr=lr)

em = KalahEnvManager(opponent, device, dqn_side)
wins = 0
num_played = 0
avg_score = 0
loss = None
min_loss = sys.maxsize
max_win_rate = 0
max_score = 0

steps = 0
start_time = time.time()
for episode in range(1, num_episodes + 1):
    mem_state = []
    mem_action = []
    mem_next = []
    num_played += 1
    em.reset()
    done = False
    side = em.side
    state = em.get_state_val()
    reward = 0
    for step in range(max_steps):
        steps += 1
        side = em.get_side()
        # minimax select action
        eps = strategy.get_exploration_rate(steps)
        value, move = MiniMaxAgent.minimax_dl(em.kalah, side, side, minimax_depth, -sys.maxsize, sys.maxsize, value_net, eps)
        move = Move(em.side, move)

        # agent makes a move
        reward = em.take_action(move)
        done = em.done
        state = em.get_state_val()
        side = em.get_side()

        # save in memory
        mem_state.append(torch.unsqueeze(state, 0))

        # Memory replay
        if memory.exp_count >= batch_size:
            experiences = memory.sample(batch_size)
            states, scores = extract_tensors(
                experiences
            )
            current_q_values = QValues.get_current(
                value_net, states
            )
            # gradient descent: update weights
            loss = F.mse_loss(current_q_values, scores.to(device).unsqueeze(1))
            optimizer.zero_grad()  # clear previous gradients
            loss.backward()  # back prop, calculate gradients
            optimizer.step()  # update weights

        # stop episode if game is over
        if done:
            dqn_win, final_score = em.winner()
            if dqn_win:
                wins += 1
                print("eps for win: " + str(eps))
                torch.save(value_net.state_dict(), "model/latest_win")
                if final_score > max_score:
                    max_score = final_score
                    torch.save(value_net.state_dict(), "model/max_score")

            for i in range(len(mem_state)):
                memory.exp_save(
                        Experience(
                            mem_state[i], torch.Tensor([final_score])
                        )
                    )
            break

    dqn_win, final_score = em.winner()
    avg_score += final_score

    if episode % 10 == 0:
        # print current winning rate
        avg_score /= num_played
        winning_rate = wins / num_played
        clear_output(wait=True)
        print("episode: " + str(episode - 9) + '-' + str(episode))
        print("DQN avg scores: " + str(avg_score))
        print("current best score: " + str(max_score))
        print("winning rate(past 10 games): " + str(winning_rate))
        print("loss: " + str(loss))
        print("current eps: " + str(eps))
        wins = 0
        num_played = 0
        if winning_rate > max_win_rate:
            max_win_rate = winning_rate
            torch.save(value_net.state_dict(), "model/max_win_rate")
        end_time = time.time()
        print("training time: " + str(end_time-start_time) + "\n")

print("max winning rate during training: " + str(max_win_rate))