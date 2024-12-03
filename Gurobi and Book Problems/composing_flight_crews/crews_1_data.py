N = 8

lang_dict = {1 : "English", 
             2 : "French", 
             3 : "Dutch", 
             4 : "Norwegian"}

flight_dict = {1 : "Reconnaissance", 
               2 : "Transport", 
               3 : "Bomber", 
               4 : "Fighter-Bomber", 
               5 : "Supply Plane"}

lang_scores = []
flight_scores = []

with open("crews_data_1.dat") as data:
    lines = data.read().splitlines()
    
    lang_lines = lines[2:6]
    for line in lang_lines:
        curr_line = line.replace("[", "")\
                        .replace("]", "")\
                        .replace("(", "")\
                        .replace(")", "")\
                        .replace("LANG: ", "")
        curr_line = curr_line.split()
        lang_line = [int(n) for n in curr_line[2:]]
        lang_scores.append(lang_line)
    
    flight_lines = lines[7:12]
    for line in flight_lines:
        curr_line = line.replace("[", "")\
                        .replace("]", "")\
                        .replace("(", "")\
                        .replace(")", "")\
                        .replace("PTYPE: ", "")
        curr_line = curr_line.split()
        flight_line = [int(n) for n in curr_line[2:]]
        flight_scores.append(flight_line)

arcs = []
unique_arcs = []
lang_score_dict = {}
flight_score_dict = {}

for li in range(len(lang_scores)):
    for fi in range(len(flight_scores)):
        for i in range(N):
            for j in range(i+1, N):
                l_score_p1 = lang_scores[li][i]
                l_score_p2 = lang_scores[li][j]
                f_score_p1 = flight_scores[fi][i]
                f_score_p2 = flight_scores[fi][j]
                
                if (l_score_p1 >= 10 and 
                    l_score_p2 >= 10 and 
                    f_score_p1 >= 10 and 
                    f_score_p2 >= 10):
                    
                    # print((l_score_p1 + l_score_p2), (f_score_p1 + f_score_p2))
                    arcs.append((i+1, j+1, li+1, fi+1))
                    unique_arcs.append((i+1, j+1))
                    if (i+1, j+1) not in lang_score_dict:
                        lang_score_dict[(i+1, j+1)] = [li+1, l_score_p1 + l_score_p2]
                        flight_score_dict[(i+1, j+1)] = [fi+1, f_score_p1 + f_score_p2]
                    else:
                        if l_score_p1 + l_score_p2 > lang_score_dict[(i+1, j+1)][1]:
                            lang_score_dict[(i+1, j+1)] = [li+1, l_score_p1 + l_score_p2]
                        if f_score_p1 + f_score_p2 > flight_score_dict[(i+1, j+1)][1]:
                            flight_score_dict[(i+1, j+1)] = [fi+1, f_score_p1 + f_score_p2]

arcs = list(set(arcs))
unique_arcs = set(unique_arcs)

# print(lang_scores[2][5], lang_scores[2][7])
# print(flight_scores[4][5], flight_scores[4][7])
