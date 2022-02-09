# RL4Rec
This repository contains the code used for the experiments in "State Encoders in Reinforcement Learning for Recommendation: A Reproducibility Study".

## Required packages
You can install conda and then create Python 3.6 Conda environment. Run conda create -n RL4Rec python=3.6 to create the environment. Activate the environment by running conda activate RL4Rec. 
Then try to install the required packages:
```
$ pip install -r requirements.txt
```
Or
```
$ conda install --yes --file requirements.txt
```
## Reproducing Experiments
We compare seven state encoders in a DQN-based RL4Rec framework when evaluating in the debiased simulations of Yahoo! R3 dataset and the coat shopping dataset.

Reproducing the results of policies with the BOI, PLD, Avg, Attention, MLP, GRU, and CNN state encoders in this paper can be done with the following commands with the best hyperparameters given for each state encoder:
#### On the debiased simulation of Yahoo! R3 dataset, 
```
$ cd examples
$ python run_dqn.py --dataset yahoo --state_encoder BOI --action_dim 64 
$ python run_dqn.py --dataset yahoo --state_encoder PLD --action_dim 64 
$ python run_dqn.py --dataset yahoo --state_encoder MLP --action_dim 64 
$ python run_dqn.py --dataset yahoo --state_encoder Att --action_dim 64 --rnn_state_dim 16
$ python run_dqn.py --dataset yahoo --state_encoder MLP --action_dim 64 --activation relu
$ python run_dqn.py --dataset yahoo --state_encoder GRU --action_dim 32 --rnn_state_dim 32
$ python run_dqn.py --dataset yahoo --state_encoder CNN --action_dim 64 --rnn_state_dim 32
```
#### On the debiased simulation of the coat shopping dataset, 
```
$ cd examples
$ python run_dqn.py --dataset coat --state_encoder BOI --action_dim 64 
$ python run_dqn.py --dataset coat --state_encoder PLD --action_dim 64 
$ python run_dqn.py --dataset coat --state_encoder MLP --action_dim 64 
$ python run_dqn.py --dataset coat --state_encoder Att --action_dim 64 --rnn_state_dim 32
$ python run_dqn.py --dataset coat --state_encoder MLP --action_dim 64 --activation tanh
$ python run_dqn.py --dataset coat --state_encoder GRU --action_dim 32 --rnn_state_dim 16
$ python run_dqn.py --dataset coat --state_encoder CNN --action_dim 64 --rnn_state_dim 64
```
Due to the large size of Yahoo! R3 dataset,  we do not upload it in this project. For using the simulation of Yahoo! R3 dataset, please download it [here](https://surfdrive.surf.nl/files/index.php/s/U8bh3zzzaDdlR5u), unzip and put it in the folder ```./data/```.

<!-- ## Parameters
- `./conf/yahoo.properties`
    - `data.input.dataset`: default sim4, a simulated dataset. You can also choose yahoo or coat dataset, which would lead to two kinds of evaluation: (1) Solution-1: Limiting Action Selection; (2) Solution-2: Completing the Rating Matrix.
    - `mode`: default DQN.
    - `seed`: default 2010. Set random seed to achieve reproducibility.
    - `episode_length`: default 10. It means the max number of interaction turns.
    - `evaluation`: default false. It means if we directly evaluate with the saved models.
- `./conf/DQN.properties`
    - `state_encoder`: default GRU. The models of the state encoder include MLP and GRU for now. We will add CNN, Attention etc.
    - Others -->

<!-- ![](DQN-parameters.png) -->

<!-- ## Markov Decision Process (MDP)
We will now describe how we model the recommendation task as an Markov Decision Process (MDP):
- State space ![1](http://latex.codecogs.com/svg.latex?S): A state represents all the current information on which a decision can be based, including the recommended items and the corresponding feedback, denoted as ![1](http://latex.codecogs.com/svg.latex?s^u_t=([i_1,i_2,\dots,i_{t}],[f_1,f_2,\dots,f_{t}])), with ![1](http://latex.codecogs.com/svg.latex?i_k) the item recommended by the RS in turn k, and ![1](http://latex.codecogs.com/svg.latex?f_k) the corresponding user feedback.
- Action space ![1](http://latex.codecogs.com/svg.latex?A): An action taken by the RS consists of the recommendation of a single item in turn t. 
- Reward ![1](http://latex.codecogs.com/svg.latex?R): After receiving the action, consisting of item being recommended by the RS, the (simulated) user gives feedback ![1](http://latex.codecogs.com/svg.latex?f_t\in\{0,1\})  (i.e. skip or click) on this item.
- Transition probabilities ![1](http://latex.codecogs.com/svg.latex?T): After the user provides feedback on the recommended item, the state transitions deterministically to the next state by appending this item and feedback to the current state.
- Discount factor ![1](http://latex.codecogs.com/svg.latex?\gamma): As usual in MDP,  ![1](http://latex.codecogs.com/svg.latex?\gamma\in[0,1]) aims to balance the effect of immediate rewards and future rewards.  -->