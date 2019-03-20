import numpy as np
import random
import pandas as pd




#calulate total 'cost' of sequence, outputs as dictionary with cost as keys and sequences that produce that cost as values
def calculate_cost(lstpop,coeffDF):
	rankedPop = {}
	for ind in lstpop:
		x = len(ind)
		i=0
		totcost = 0
		while i != x:
			row= ind[i]
			col = ind[(i+1)%x]
			cost = coeffDF.iloc[row,col]
			totcost += cost
			i+=1
		if totcost not in rankedPop.keys():
			rankedPop[totcost] = []
			rankedPop[totcost].append(ind)
		else:
			if ind not in rankedPop[totcost]:
				rankedPop[totcost].append(ind)		
	return rankedPop;
	
#produces first generation by randomly sorting sequence 	
def first_gen(decisions, **kwargs):
	lst = []
	pop = []
	for e in range(decisions):
		lst.append(e)
	pop.append(lst)
	if 'pop_size' in kwargs:
		pop_size = kwargs['pop_size']
		for i in range(pop_size-1):
			lst = random.sample(lst, len(lst))
			pop.append(lst)
	else:
		for i in range(9999):
			lst = random.sample(lst, len(lst))
			pop.append(lst)
	return pop;
	

#thins population based on best performers and identifies candidate with lowest cost for this generation
def thin_pop (popDict,cutoff):
	thinnedPop = []
	candidates = {}
	vallist = list(popDict.keys())
	vallist.sort()
	setlst = set(vallist)
	setlst = list(setlst)
	setlst.sort()
	cut = cutoff
	fitpop = int(len(setlst)* cut)
	for value, sequence in popDict.items():
		if value in setlst[:fitpop]:
			thinnedPop.append(sequence)
		if value == setlst[0]:
			if value in candidates:
				candidates[value].append(sequence)
			else:
				candidates[value]=sequence
	return [candidates, thinnedPop];

#fills out remaining space in population after crossover with random sequences to added variation
def new_gen(lstThinnedPop, **kwargs):
	current_pop_size = len(lstThinnedPop)
	sequence_size = len(lstThinnedPop[0])
	if 'pop_size' in kwargs:
		pop_size = kwargs['pop_size']
		needed = pop_size-current_pop_size
		new = first_gen(sequence_size,pop_size=needed)
		for item in new:
			lstThinnedPop.append(item)
	else:
		needed = 10000-current_pop_size
		new = first_gen(sequence_size,pop_size=needed)
		for item in new:
			lstThinnedPop.append(item)
	return lstThinnedPop;

#swap mutation
def swap_mutation(sequence):
	slen = len(sequence)
	num1 = np.random.randint(slen)
	num2 = np.random.randint(slen)
	swap1 = sequence[num1]
	swap2 = sequence[num2]
	sequence[num1]=swap2
	sequence[num2]=swap1
	return sequence;
	

#performs mutation based on defined rate
def random_mutation(lstPop,**kwargs):
	if 'mutation_rate' in kwargs:
		rate = kwargs['mutation_rate']
	else:
		rate = .1
	pop_size = len(lstPop)
	sample = int(pop_size * rate)
	i = 0
	lstSample = []
	while i != sample:
		x = np.random.randint(pop_size)
		if x not in lstSample:
			lstSample.append(x)
			i += 1
		else:
			continue
	for item in lstSample:
		lstPop[item]=swap_mutation(lstPop[item])
	return lstPop;

#crossover reproduction of top performing individuals
def Order1Crossover(lstThinnedPop):
	current_pop_size = len(lstThinnedPop)
	sequence_size = len(lstThinnedPop[0])
	new_pop=[]
	while len(new_pop) != current_pop_size:
		child = []
		Parent_1 = lstThinnedPop[np.random.randint(current_pop_size)]
		Parent_2 = lstThinnedPop[np.random.randint(current_pop_size)]
		swap_1 = np.random.randint(sequence_size)
		swap_2 = np.random.randint(sequence_size)
		if swap_1 > swap_2:
			section = Parent_1[swap_2:swap_1]
			child = section
			for gene in Parent_2:
				if gene not in section:
					pos = Parent_2.index(gene)
					child.insert(pos,gene)
			
		if swap_1 <= swap_2:
			section = Parent_1[swap_1:swap_2]
			child = section
			for gene in Parent_2:
				if gene not in section:
					pos = Parent_2.index(gene)
					child.insert(pos,gene)		
		new_pop.append(child)
	return new_pop;


#combines all functions above to iterate throug generations.
def TSPsolver(df,decisions,pop_size,mutation_rate,improved,cutoff,seed):
	np.random.seed(seed)
	random.seed(seed)
	x = thin_pop(calculate_cost(first_gen(decisions,pop_size=pop_size),df),cutoff)

	obj = list(x[0].keys())[0]
	candidates = x[0]
	i = 0
	while i != improved:
		x = x[1][0]
		x = thin_pop(calculate_cost(random_mutation(new_gen(Order1Crossover(x),pop_size=pop_size),mutation_rate=mutation_rate),df),cutoff)
		new_Obj = list(x[0].keys())[0]
		if new_Obj < obj:
			obj = new_Obj
			candidates = x[0]
			i = 0
		elif new_Obj == obj:
			for item in list(x[0].values())[0]:
				if item not in list(candidates.values()):
					candidates[obj].append(item)
			i += 1
		else:
			i += 1
	return candidates;
