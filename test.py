# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
from __future__ import absolute_import
from game.agent import Agent

import numpy as np

#rl
if __name__=="__main__":
    
    step = 0
    num_epochs = 10000
    agent = Agent(models=["rl","cxgz","random"])
    
    rl_model = "double_dqn"
    
    if rl_model == "dqn":
        from rl.dqn import DeepQNetwork
        RL = DeepQNetwork(agent.dim_actions, agent.dim_states,num_epochs,
                      learning_rate=0.01,
                      reward_decay=0.9,
                      e_greedy=0.9,
                      replace_target_iter=200,
                      memory_size=2000,
                      )
    #发散到60
    elif rl_model == "double_dqn":
        from rl.double_dqn import DoubleDQN
        RL = DoubleDQN(agent.dim_actions, agent.dim_states,num_epochs,
                      learning_rate=0.0001,
                      reward_decay=0.9,
                      e_greedy=1,
                      replace_target_iter=200,
                      memory_size=2000,
                      double_q=True,
                      )
    #收敛到50
    elif rl_model == "prioritized_dqn":
        from rl.prioritized_dqn import DQNPrioritizedReplay
        RL = DQNPrioritizedReplay(agent.dim_actions, agent.dim_states,num_epochs,
                      learning_rate=0.01,
                      reward_decay=0.9,
                      e_greedy=0.9,
                      replace_target_iter=200,
                      memory_size=2000,
                      prioritized=True
                      )
    elif rl_model == "dueling_dqn":
        from rl.dueling_dqn import DuelingDQN
        RL = DuelingDQN(agent.dim_actions, agent.dim_states,num_epochs,
                      learning_rate=0.001,
                      reward_decay=0.9,
                      e_greedy=0.9,
                      replace_target_iter=200,
                      memory_size=2000,
                      dueling=True
                      )

    RL.load_model(rl_model, 30000)
    
    winners = []
    win_rate = 0
    for episode in range(num_epochs):
        # initial observation
        s = agent.reset()
        done = False
        loss = 0
        while(not done):
            
            #print(agent.game.get_record())
            # RL choose action based on observation
            actions = agent.get_actions_space()
            #print(actions)
            #action to one-hot
            actions_ont_hot = np.zeros(agent.dim_actions)
            for k in range(len(actions)):
                actions_ont_hot[actions[k]] = 1
                
            action, action_id = RL.choose_action(s, actions_ont_hot, actions)
            #print(action)
            # RL take action and get next observation and reward
            s_, r, done = agent.step(action_id=action_id)

            # swap observation
            s = s_

            step += 1

        if r == 1:
            winners.append(1)
        else:
            winners.append(0)
            
        win_rate = np.mean(winners)
            
            
    # end of game
    print('game over')
    RL.plot_cost()

