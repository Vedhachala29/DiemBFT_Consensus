import random
from enum import Enum
from partition_generator import generate_heuristic_partitions, persist_to_file
import math
import os
import json

def scenario_generator(nodes, twins, n_partitions, n_rounds, partition_limit, partition_leader_limit, 
            max_testcases, seed, is_Faulty_Leader, is_Deterministic, file_path):  
    """
        Example : 
        1,2,3,4 => Non-faulty
        5 => Faulty
    """
    random.seed(seed)
    total_nodes = nodes + list(twins.values())
    #Step 1
    partitions_list = generate_heuristic_partitions(n_partitions, nodes, twins, partition_limit, is_Deterministic, seed, f'./partitions.txt')
    print("Length of partition_list : " , len(partitions_list), "\n")
    for i in partitions_list:
        print(i)
    
    #Step 2
    partition_leader_list_high_p = []
    partition_leader_list_low_p = []
    partition_leader_list = []
    count = 0

    if is_Faulty_Leader: 
        n = [int(i) for i in list(twins.keys())]                      #Filtering only faulty nodes if is_Faulty_Leader is set
    else :
        n = total_nodes

    flag = False
    for partition_set in partitions_list:
        for partition in partition_set:
            if len(partition) >= 2*len(twins) + 1:  #Generating leader-partition pairs of quorum partitions.
                twin_list = []
                for node in partition:
                    if node not in n:               #Applying filter on node.
                        continue
                    count+=1
                    if count > partition_leader_limit:
                        flag = True
                        break
                    partition_leader_list_high_p.append([node, partition_set])
                    if node in twins:
                        twin_list.append([twins[node], partition_set])
    
                for item in twin_list:
                    count+=1
                    if count > partition_leader_limit:
                        flag = True
                        break
                    partition_leader_list_high_p.append(item)
            else:
                twin_list = []
                for node in partition:
                    if node not in n:               #Applying filter on node.
                        continue
                    count+=1
                    if count > partition_leader_limit:
                        flag = True
                        break
                    partition_leader_list_low_p.append([node, partition_set])
                    if node in twins:
                        twin_list.append([twins[node], partition_set])
    
                for item in twin_list:
                    count+=1
                    if count > partition_leader_limit:
                        flag = True
                        break
                    partition_leader_list_low_p.append(item)
                
            if flag: break
        if flag: break
    
    if is_Deterministic:
        l = partition_leader_list_high_p + partition_leader_list_low_p
        partition_leader_list = l[:partition_leader_limit]
    
    else: 
        # Randomly pick partition_leader_limit elements from partition_leader_list_high_p and partition_leader_list_low_p
        l = partition_leader_list_high_p + partition_leader_list_low_p
        partition_leader_list = random.sample(l, min(partition_leader_limit, len(l)))
        

    print("Length of partition_leader_list : " , len(partition_leader_list), "\n")
    for i in partition_leader_list:
        print(i)
    
    #Step 3 and #Step 4 combined
    num_scenarios=0
    iterator = 0
    scenarios = []
    count=0
    while num_scenarios < max_testcases and count < 10*max_testcases:
        count+=1
        scenario_tuple = create_scenario(partition_leader_list_high_p, seed, is_Deterministic, n_rounds, len(nodes), len(twins), iterator)
        iterator = scenario_tuple[1]
        if is_valid(scenario_tuple[0], n_rounds, len(twins), 3):
            num_scenarios+=1
            scenarios.append(scenario_tuple[0])

    with open(file_path, 'w+') as file:
        file.write(json.dumps(scenarios, default=str))
        file.flush()
        os.fsync(file.fileno())
        file.close()
    print("Length of scenarios flushed to file and total scenarios explored are ", len(scenarios), count)
    
def create_scenario(partition_leader_list, seed, is_Deterministic, rounds, n_nodes, n_twins, iterator):

    scenario={}
    scenario['n_replicas'] = n_nodes
    scenario['n_twins'] = n_twins

    rounds_dict = {}

    #For each round, determine if a failures are being introduced. 
    #Accordingly make amends to partition-leader combination and append it to scenario.
    
    for round in range(rounds):
        introduce_failure = random.random()
        if introduce_failure < 0.85:
            t = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.WILDCARD, iterator)
            rounds_dict[round] = {}
            rounds_dict[round]["leader"] = t[0]
            rounds_dict[round]["partitions"] = [t[1:]]
            iterator= (iterator+1)%len(partition_leader_list)
            
        elif introduce_failure < 0.9:
            tuple1 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.WILDCARD, iterator)
            tuple2 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.PROPOSE, iterator)
            rounds_dict[round] = {}
            rounds_dict[round]["leader"] = tuple1[0]
            rounds_dict[round]["partitions"] = [tuple1[1:], tuple2[1:]]
            iterator = (iterator+1)%len(partition_leader_list)
            
        elif introduce_failure < 0.95:
            tuple1 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.WILDCARD, iterator)
            tuple2 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.VOTE, iterator)
            rounds_dict[round] = {}
            rounds_dict[round]["leader"] = tuple1[0]
            rounds_dict[round]["partitions"] = [tuple1[1:], tuple2[1:]]
            iterator=(iterator+1)%len(partition_leader_list)
        
        else :
            tuple1 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.WILDCARD, iterator)
            tuple2 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.PROPOSE, iterator)
            tuple3 = get_tuple(is_Deterministic, partition_leader_list, Failure_Type.VOTE, iterator)
            rounds_dict[round] = {}
            rounds_dict[round]["leader"] = tuple1[0]
            rounds_dict[round]["partitions"] = [tuple1[1:], tuple2[1:], tuple3[1:]]
            iterator=(iterator+1)%len(partition_leader_list)
    
    scenario["n_rounds"] = rounds
    scenario["rounds"] = rounds_dict
    return (scenario, iterator)
    
def get_tuple(is_Deterministic, partition_leader_dict, failure_type, iterator):
    item = None
    if is_Deterministic:
        item = partition_leader_dict[iterator % len(partition_leader_dict)] #Get item at location iterator deterministically and increment iterator

    else :
        id = math.floor(random.uniform(0, 1)*len(partition_leader_dict))  #Get item randomly from the partition_leader_dict
        item = partition_leader_dict[id]

    return (item[0], item[1], failure_type)

class Failure_Type(Enum):
    WILDCARD = 1
    PROPOSE = 2
    VOTE = 3

def is_valid(scenario, rounds, n_twins, threshold):
    # This check is used to prune potentially non-responsive cases.

    quorum_len = 2 * n_twins + 1
    r=0
    t=0
    while r+2 < rounds:
        l_0 = scenario["rounds"][r]["leader"]
        l_1 = scenario["rounds"][r+1]["leader"]
        l_2 = scenario["rounds"][r+2]["leader"]

        if (any(True if len(p)>=quorum_len and l_0 in p else False for p in scenario["rounds"][r]["partitions"][0][0])
            and any(True if len(p)>=quorum_len and l_1 in p else False for p in scenario["rounds"][r]["partitions"][0][0])
            and any(True if len(p)>=quorum_len and l_1 in p else False for p in scenario["rounds"][r+1]["partitions"][0][0]) 
            and any(True if len(p)>=quorum_len and l_2 in p else False for p in scenario["rounds"][r+1]["partitions"][0][0])
            and any(True if len(p)>=quorum_len and l_2 in p else False for p in scenario["rounds"][r+2]["partitions"][0][0])
            ):
            t+=1
        
        r+=3
    return t>=threshold

# scenario_generator([0,1,2,3], {0:4}, 2, 20, 30, 100, 500, 42, False, False, f'./scenarios.json')
def main():
    c = open('../config/configs.json')
    configs = json.load(c)
    os.makedirs('../scenarios/', exist_ok=True) 
    for config in configs:
        config_id = config['id']
        nodes = [i for i in range(config['nvalidators'])]
        scenario_generator(nodes, config['twin'], config['n_partitions'], config['n_rounds'], config['partition_limit'], 
                config['partition_leader_limit'], config['max_testcases'], config['seed'], config['is_Faulty_Leader'], 
                config['is_Deterministic'], f'../scenarios/config_{config_id}.json')

if __name__ == '__main__':
    main()
