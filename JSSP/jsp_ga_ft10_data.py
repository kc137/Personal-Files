
machining_sequence = []
processing_times = []

with open("instances/ft10.txt", "r") as data:
    lines = data.read().splitlines()
    
    for line in lines[1:11]:
        line_str = line.strip().split()
        line_lst = [int(j) for j in line_str]
        processing_times.append(line_lst)
    
    for line in lines[11:21]:
        line_str = line.strip().split()
        line_lst = [int(j) for j in line_str]
        machining_sequence.append(line_lst)