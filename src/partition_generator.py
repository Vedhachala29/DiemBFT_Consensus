import os
import random
import copy

partitions = []

def gen_partitions(nodes, twins, k, f, partition_limit, is_Deterministic):
    global partitions
    results=[]
    if not is_Deterministic:
        random.shuffle(nodes)
    
    print("Nodes before generating partitions: ", nodes)

    for i in range(k):
        results.append([])
    
    deterministic_partition_gen_algorithm(0, nodes, k, 0, results, 5*partition_limit)
    return filter_nonquorum(f, twins)

def filter_nonquorum(f, twins):
    global partitions
    final_partitions = []
    for result in partitions:
        # Checking if atleast one partition has quorum and insert into final_partitions if quorum exists.
        for p in result:
            if (len(p) >= 2*f + 1) and not any(key in p and value in p for key, value in twins.items()):
                final_partitions.append(result)
                break
    return final_partitions

def deterministic_partition_gen_algorithm(i, nodes, k, nums, results, partition_limit):
    global partitions
    if len(partitions) == partition_limit:
        return

    if i >= len(nodes):
        if nums == k:
            partitions.append(copy.deepcopy(results))
        return

    for j in range(len(results)):
        results[j].append(nodes[i])
        if len(results[j]) > 1:
            deterministic_partition_gen_algorithm(i + 1, nodes, k, nums, results, partition_limit)
            results[j].pop()
        else:
            deterministic_partition_gen_algorithm(i + 1, nodes, k, nums + 1, results, partition_limit)
            results[j].pop()
            break

def generate_heuristic_partitions(num_partitions, nodes, twins, partition_limit, is_Deterministic, seed, file_path):

    f = len(twins)
    total_nodes = nodes + list(twins.values())

    if is_Deterministic:
        partitions = gen_partitions(total_nodes, twins, num_partitions, f, partition_limit, True)
        persist_to_file(partitions, file_path)
        return partitions
       
    else :
        partitions = gen_partitions(total_nodes, twins, num_partitions, f, partition_limit, False)
        persist_to_file(partitions, file_path)
        return partitions

def persist_to_file(partitions, file_path):
    file = open(file_path, "w+")

    for item in partitions:
        file.write(str(item)+"\n")

    file.flush()
    os.fsync(file.fileno())
    file.close()
    