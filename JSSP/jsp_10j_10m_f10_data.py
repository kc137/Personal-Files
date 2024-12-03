machine_sequence, processing_times = [], []

with open("ft10.txt", "r") as data:
    lines = data.read().splitlines()
    for line in lines[1:11]:
        line_str = line.split()
        processing_times.append([int(j) for j in line_str])
    for line in lines[11:21]:
        line_str = line.split()
        machine_sequence.append([int(j) for j in line_str])