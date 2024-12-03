def run():
    
    data_dict = {n : [] for n in range(1, 12)}
    
    with open("c2glass.dat") as data:
        lines = data.read().splitlines()
        j = 1
        for line in lines[2:10]:
            if line:
                data_dict[j] = line.split(":")[1]
                data_dict[j] = data_dict[j].replace("[", "").replace("]", "")
                data_dict[j] = data_dict[j].split()
                data_dict[j] = [int(n) for n in data_dict[j]]
                j += 1
        
        for line in lines[10:16]:
            if line[0] == "D":
                curr = line.split(":")[1]
                curr = curr.replace("[", "").replace("]", "")
                curr = curr.split()
                curr = [int(n) for n in curr]
                data_dict[j].append(curr)
            else:
                line = line.replace("[", "").replace("]", "")
                curr = line.strip().split(" ")
                curr = [int(n) for n in curr if n]
                data_dict[j].append(curr)
        j += 1
        for line in lines[17:20]:
            if line:
                num = line.split(":")[1]
                data_dict[j] = int(num)
                j += 1
                
        for line in lines[21:]:
            if line:
                curr = line.split(":")[1]
                curr = curr.replace("[", "").replace("]", "")
                curr = curr.split()
                curr = [int(n) for n in curr]
                data_dict[j] = curr
                j += 1
        
        return data_dict

final_data = run()

CPROD = final_data[1]
CSTOCK = final_data[2]
FSTOCK = final_data[3]
ISTOCK = final_data[4]
DEM = final_data[5]
CAPW = final_data[6]
CAPM = final_data[7]
CAPS = final_data[8]
TIMEW = final_data[9]
TIMEM = final_data[10]
SPACE = final_data[11]
