import random
import numpy as np

platforms = ['Google', 'Facebook', 'YouTube', 'Instagram']
num_platforms = len(platforms)

# State: Current performance (dummy for now)
# Action: Budget split (index of platform)
# Reward: Reach/clicks

Q = np.zeros((10, num_platforms))  # 10 dummy states x 4 platforms

learning_rate = 0.1
discount = 0.9
epsilon = 0.2  # Exploration vs. exploitation


def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, num_platforms - 1)
    else:
        return np.argmax(Q[state])


def update_q_table(state, action, reward, next_state):
    best_future = np.max(Q[next_state])
    Q[state][action] = Q[state][action] + learning_rate * (reward + discount * best_future - Q[state][action])


def get_q_table():
    return Q.tolist()