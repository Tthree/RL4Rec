import sys
sys.path.append('../src/')
import os
# os.environ['KMP_DUPLICATE_LIB_OK']='True'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
from time import time, localtime, strftime
import configparser

# from env.env import SOFAEnv, simulated_data
from env.env_multiusers import SOFAEnv, simulated_data

from train import train
from evaluation import evaluate, eval_yahoo_sinTurn, yahoo_eval_1, yahoo_eval_1_calu_itemset

import tensorflow as tf
# tf.compat.v1.disable_eager_execution()
import random

def _get_conf(conf_name):
    config = configparser.ConfigParser()
    config.read("../conf/"+conf_name+".properties")
    conf=dict(config.items("default"))

    evalProcess = conf['evaluation']
    if evalProcess.lower() == 'false':
        if (conf["data.input.dataset"] in ['sim4', 'sim5']) and (conf["data.debiasing"] == 'GT'):
            rating_file = conf["data.input.path"] + conf["data.input.dataset"] + "_GT_ratingM.ascii"
        else:
            rating_file = conf["data.input.path"] + conf["data.input.dataset"] + '_' + \
            conf["data.gen_model"] + '_' + conf["data.debiasing"] + "_ratingM.ascii"
            if conf["data.debiasing"] == 'GT':
                rating_file = conf["data.input.path"] + conf["data.input.dataset"] + "_pseudoGT_ratingM.ascii"
                print("we use a pseudo GT for yahoo, which is generated by MF on unbiased testset:", rating_file)
    else:
        if conf["data.input.dataset"].lower() in ['sim4', 'sim5']:
            print('now evaluation process only for simulated dataset which has the groundTruth')
            rating_file = conf["data.input.path"] + conf["data.input.dataset"] + "_GT_ratingM.ascii"
        elif conf["data.input.dataset"].lower() in ["yahoo", "coat"]:
            rating_file = conf["data.input.path"] + conf["data.input.dataset"] + '_' + \
            conf["data.gen_model"] + '_' + conf["data.debiasing"] + "_ratingM.ascii" # this simulator is not for evaluation directly, but for several interaction to generate states
            # solution-2 with pseudo GT
            rating_file = conf["data.input.path"] + conf["data.input.dataset"] + "_pseudoGT_ratingM.ascii"
            print("we use a pseudo GT for yahoo, which is generated by MF on unbiased testset:", rating_file)
        else:
            print("check data")
    conf["RATING_TYPE"] = conf["rating_type"]
    conf["RATINGS"] = np.clip(np.round(np.loadtxt(rating_file)).astype('int'), 1, 5)
    conf["EPISODE_LENGTH"] = conf["episode_length"]
    conf['mode'] = conf['mode'].upper()
    if conf['mode'] == 'DOUBLEDQN':
        conf['mode'] = 'DoubleDQN'
    return conf

def _logging_(basis_conf, params_conf):
    now = localtime(time())
    now = strftime("%Y-%m-%d %H:%M:%S", now)
    origin_data_name = basis_conf["data.input.dataset"]
    gen_model = basis_conf["data.gen_model"]
    debiasing = basis_conf["data.debiasing"]
    print(now + " - data:%s" % origin_data_name)
    print(now + " - gen_model:%s, debiasing:%s" % (gen_model, debiasing))
    print(now + " - RL Algo: %s, state_encoder: %s" % (basis_conf['mode'], params_conf['state_encoder']))
    print("conf : " + str(params_conf), flush=True)


def run_dqn():
    conf = _get_conf('yahoo')
    # # simulated data: 
    # conf['RATINGS'], item_vec = simulated_data(10, 20)
    # conf["data.input.dataset"] = 'sim_u10_i20'

    # item_vec = conf["ITEM_VEC"]
    sofa = SOFAEnv(conf)
    action_space = sofa.num_items
    num_users = sofa.num_users

    # init DQN
    config = load_parameters(conf['mode'])
    config['STATE_MAXLENGTH'] = int(conf["episode_length"])
    config['ACTION_SPACE'] = action_space

    # # for multiple jobs in 
    args = set_hparams()
    if args.state_encoder:
        config["state_encoder"] = args.state_encoder
    config['SAVE_MODEL_FILE'] = conf["data.input.dataset"] + '_' + conf['mode'] + '_' + config["state_encoder"]
    if args.debiasing:
        conf["data.debiasing"] = args.debiasing
    if args.seed:
        conf["seed"] = args.seed
        config['SAVE_MODEL_FILE'] += "_seed%d" % args.seed
    if args.action_dim:
        config["ACTION_DIM"] = args.action_dim
        config['SAVE_MODEL_FILE'] += "_acdim_%d" % args.action_dim
    if args.rnn_state_dim:
        config["RNN_STATE_DIM"] = args.rnn_state_dim
        config['SAVE_MODEL_FILE'] += "_rnndim%d" % args.rnn_state_dim
    assert conf["data.debiasing"] == 'ips'
    
    # config['SAVE_MODEL_FILE'] = conf["data.input.dataset"] + '_' + \
    #     conf["data.gen_model"] + '_' + conf["data.debiasing"] + '_' + \
    #     conf['mode'] + '_' + config["state_encoder"] + '_' + 'r-12_SmoothL1_' + 'nohuman' + "_seed" + conf["seed"]
    # config['SAVE_MODEL_FILE'] = conf["data.input.dataset"] + '_' + conf['mode'] + '_' + config["state_encoder"] + "_seed" + conf["seed"]
    
    _logging_(conf, config)
    if ('seed' in conf) and (conf['seed'].lower() != 'none'):
        seed = int(conf['seed'])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        random.seed(seed)
        print("now the seed is", seed, flush=True)
    else:
        print("now the seed is None")

    # # train process
    evalProcess = conf['evaluation']
    if evalProcess.lower() == 'false':
        try:
            train(conf, config, sofa)
        except:
            print("Learning being interrupted. Start evalution.")
    
    if conf["data.input.dataset"].lower() in ['yahoo', 'coat']:
        test_file = conf["data.input.path"] + conf["data.input.dataset"] + "_test.ascii"
        # eval_yahoo_sinTurn(conf, config, sofa, test_file)
        yahoo_eval_1(conf, config, sofa, test_file)
        # yahoo_eval_1_calu_itemset(conf, config, sofa, test_file)
        # # solution-2 with a pseudo GT
        # evaluate(conf, config, sofa, test_file)
    else:
        evaluate(conf, config, sofa)


def load_parameters(mode):
    ## load from configfile
    params = {}
    config = configparser.ConfigParser()
    config.read("../conf/"+mode+".properties")
    conf=dict(config.items("hyperparameters"))
    params['ACTION_DIM'] = int(conf['action_dim'])
    params['MEMORY_SIZE'] = int(conf['memory_size'])
    params['GAMMA'] = float(conf['gamma']) # reward decay
    params['LEARNING_RATE'] = float(conf['learning_rate'])
    params['EPSILON'] = float(conf['epsilon'])
    params['BATCH_SIZE'] = int(conf['batch_size'])
    params['REPLACE_TARGETNET'] = int(conf['replace_targetnet'])
    params['OPTIMIZER'] = conf['optimizer']
    params['RNN_STATE_DIM'] = int(conf['rnn_state_dim'])
    params['state_encoder'] = conf['state_encoder']
    params['lr_decay_step'] = conf['lr_decay_step']
    params['epsilon_decay_step'] = conf['epsilon_decay_step']
    return params
    
def set_hparams():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int)
    parser.add_argument('--debiasing', type=str)
    parser.add_argument('--action_dim', type=int)
    parser.add_argument('--rnn_state_dim', type=int)
    parser.add_argument('--state_encoder', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    run_dqn()
    print("End. " + strftime("%Y-%m-%d %H:%M:%S", localtime(time())))