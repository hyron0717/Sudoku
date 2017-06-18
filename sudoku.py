import math
import random
import time
import copy

def check_row(board,row,col,value):
	for i in range(0,9):
		if board[row][i]==value:
			return False
	return True

def check_col(board,row,col,value):
	for i in range(0,9):
		if board[i][col]==value:
			return False
	return True

def check_block(board,row,col,value):
	for i in range(0,3):
		for j in range(0,3):
			if board[i+row][j+col]==value:
				return False
	return True

def find_empty(board):
	empty_set = []
	for i in range(0,9):
		for j in range(0,9):
			if board[i][j] == 0:
				empty_set.append([i,j])
	return empty_set

def print_board(board):
	for row in board:
		print row

node = 0

def solver_back(board):
	global node
	empty_set = find_empty(board)

	if len(empty_set)==0:
		return True

	#empty_box = empty_set[0]
	empty_box = random.choice(empty_set)

	#print len(empty_set)

	row = empty_box[0]
	col = empty_box[1]

	domain = range (1,10)

	while len(domain)!=0:
		value = domain[int(math.floor(random.random()*len(domain)))]
		domain.remove(value)
		#print value

		if check_row(board,row,col,value) and check_col(board,row,col,value) and check_block(board,row-row%3,col-col%3,value):
			board[row][col] = value
			node = node + 1
			if solver_back(board):
				return True
			else:
				board[row][col]=0


	return False

def solver_btfc(board):
	global node

	empty_set = find_empty(board)

	if len(empty_set)==0:
		return True

	empty_box = random.choice(empty_set)

	row = empty_box[0]
	col = empty_box[1]

	remain_list = get_remaining_list(board)
	domain = list(remain_list[col+row*9])

	while len(domain)!=0:
		value = domain[int(math.floor(random.random()*len(domain)))]
		domain.remove(value)

		if forward_check(remain_list,value,row,col):
			board[row][col]=value
			node = node + 1

			if solver_btfc(board):
				return True
			else:
				board[row][col]=0

	return False

def solver_btfch(board):
	global node

	empty_set = find_empty(board)

	if len(empty_set)==0:
		return True

	remain_list = get_remaining_list(board)

	#find most constrained variable
	mcv_list = []
	for empty_box in empty_set:
		temp_row=empty_box[0]
		temp_col=empty_box[1]
		mcv_list.append(len(remain_list[temp_row*9+temp_col]))

	min_rv_list = []
	for i in range(0,len(mcv_list)):
		value = mcv_list[i]
		if value == min(mcv_list):
			min_rv_list.append(empty_set[i])

	#find the most constraining variable
	if len(min_rv_list)==1:
		square = min_rv_list[0]
	else:
		degree_list = []
		for box in min_rv_list:
			degree = get_degree(box,board)
			degree_list.append(degree)

			max_degree_list = []
			for i in range(0,len(degree_list)):
				value = degree_list[i]
				if value == max(degree_list):
					max_degree_list.append(min_rv_list[i])

			square = max_degree_list[0]

	row = square[0]
	col = square[1]

	domain = list(remain_list[row*9+col])

	while len(domain)!=0:
		#find the least constraining value
		lcv_list = least_constraining_value(domain,row,col,remain_list)

		value = domain[lcv_list.index(min(lcv_list))]
		domain.remove(value)

		if forward_check(remain_list,value,row,col):
			board[row][col] = value
			node = node + 1

			if solver_btfch(board):
				return True
			else:
				board[row][col] = 0

	return False


def least_constraining_value(domain,row,col,remain_list):
	lcv_list = []

	for x in domain:
		count = 0

		for i in range(0,9):
			l = remain_list[9*i+col]
			if x in l:
				count = count + 1

		for j in range(0,9):
			l = remain_list[row*9+j]
			if x in l:
				count = count + 1

		block_row = row/3
		block_col = col/3

		for i in range(0,3):
			for j in range(0,3):
				l = remain_list[block_col*3+j + (block_row*3+i)*9]
				if x in l:
					count = count + 1

		lcv_list.append(count)

	return lcv_list

def get_degree(box,board):
	row = box[0]
	col = box[1]
    
	degree = 0
    
	for i in range(0,9):              
		if board[row][i] == 0:
			degree+=1
     
	for i in range(0,9):
		if board[i][col] == 0:
			degree = degree + 1

	block_row = row/3
	block_col = col/3  
	for i in range(0,3):
		for j in range(0,3):                  
			if board[block_row*3+i][block_col*3+j] == 0:
				degree = degree + 1

	return degree 


def get_remaining_list(board):
	remain_list = []
	for i in range(0,81):
		remain_list.append(range(1,10))

	for row in range(0,9):
		for col in range(0,9):
			if board[row][col]!=0:

				value = board[row][col]
				remain_list[col+row*9]=[0]

				for row_check in remain_list[row*9:row*9+9]:
					try:
						row_check.remove(value)
					except ValueError:
						pass

				for col_check in range(0,9):
					try:
						remain_list[col+9*col_check].remove(value)
					except ValueError:
						pass

				block_row = row/3
				block_col = col/3

				for i in range(0,3):
					for j in range(0,3):
						try:
							remain_list[block_col*3+j+(block_row*3+i)*9].remove(value)
						except ValueError:
							pass
	return remain_list

def forward_check(remain_list,value,row,col):
	for i in range(0,9):
		if i ==col:
			continue

		l = remain_list[row*9+i]

		if len(l)==1:
			if l[0]==value:
				return False

	for j in range(0,9):
		if j == row:
			continue

		l = remain_list[9*j+col]

		if len(l)==1:
			if l[0]==value:
				return False

	block_row = row/3
	block_col = col/3

	for i in range(0,3):
		for j in range(0,3):
			if block_row*3+i == row and block_col*3+j == col:
				continue

			l = remain_list[block_col*3+j+(block_row*3+i)*9]

			if len(l)==1:
				if l[0]==value:
					return False

	return True


easy=[[0, 6, 1, 0, 0, 0, 0, 5, 2],
	  [8, 0, 0, 0, 0, 0, 0, 0, 1],
	  [7, 0, 0, 5, 0, 0, 4, 0, 0],
	  [9, 0, 3, 6, 0, 2, 0, 4, 7],
	  [0, 0, 6, 7, 0, 1, 5, 0, 0],
	  [5, 7, 0, 9, 0, 3, 2, 0, 6],
	  [0, 0, 4, 0, 0, 9, 0, 0, 5],
	  [1, 0, 0, 0, 0, 0, 0, 0, 8],
	  [6, 2, 0, 0, 0, 0, 9, 3, 0]]

medium=[[5, 0, 0, 6, 1, 0, 0, 0, 0],
		[0, 2, 0, 4, 5, 7, 8, 0, 0],
		[1, 0, 0, 0, 0, 0, 5, 0, 3],
		[0, 0, 0, 0, 2, 1, 0, 0, 0],
		[4, 0, 0, 0, 0, 0, 0, 0, 6],
		[0, 0, 0, 3, 6, 0, 0, 0, 0],
		[9, 0, 3, 0, 0, 0, 0, 0, 2],
		[0, 0, 6, 7, 3, 9, 0, 8, 0],
		[0, 0, 0, 0, 8, 6, 0, 0, 5]]

hard=[[0, 4, 0, 0, 2, 5, 9, 0, 0],
	  [0, 0, 0, 0, 3, 9, 0, 4, 0],
	  [0, 0, 0, 0, 0, 0, 0, 6, 1],
	  [0, 1, 7, 0, 0, 0, 0, 0, 0],
	  [6, 0, 0, 7, 5, 4, 0, 0, 9],
 	  [0, 0, 0, 0, 0, 0, 7, 3, 0],
	  [4, 2, 0, 0, 0, 0, 0, 0, 0],
	  [0, 9, 6, 5, 4, 0, 0, 0, 0],
	  [0, 0, 8, 9, 6, 0, 0, 5, 0]]

evil=[[0, 6, 0, 8, 2, 0, 0, 0, 0],
	  [0, 0, 2, 0, 0, 0, 8, 0, 1],
	  [0, 0, 0, 7, 0, 0, 0, 5, 0],
	  [4, 0, 0, 5, 0, 0, 0, 0, 6],
	  [0, 9, 0, 6, 0, 7, 0, 3, 0],
 	  [2, 0, 0, 0, 0, 1, 0, 0, 7],
	  [0, 2, 0, 0, 0, 9, 0, 0, 0],
	  [8, 0, 4, 0, 0, 0, 7, 0, 0],
	  [0, 0, 0, 0, 4, 8, 0, 2, 0]]


time_set = []
node_set = []
begin_time = time.time()

for trials in range(0,1):
	start_time = time.time()

	if start_time-begin_time>=1000:
		break

	"""
	---------------
	Change the sudoku level
	---------------
	"""
	temp_copy = copy.deepcopy(easy)
	#temp_copy = copy.deepcopy(medium)
	#temp_copy = copy.deepcopy(hard)
	#temp_copy = copy.deepcopy(evil)
	
	node = 0

	"""
	----------------------------------------------------------
	Change the function name to change the way to solve sudoku
	----------------------------------------------------------
	"""
	#result = solver_back(temp_copy)
	result = solver_btfc(temp_copy)
	#result = solver_btfch(temp_copy)

	time_set.append(time.time()-start_time)
	node_set.append(node)

if result:
	print_board(temp_copy)

	
ave_time = sum(time_set)/len(time_set)
ave_node = sum(node_set)/len(time_set)

print "average time: " , ave_time
print "average nodes: ", ave_node

total_time = 0
total_node = 0
for i in range(0,len(time_set)):
	total_time = (time_set[i]-ave_time)**2 + total_time
	total_node = (node_set[i]-ave_node)**2 + total_node

std_time = math.sqrt(total_time/len(time_set))
std_node = math.sqrt(total_node/len(node_set))

print "time std: ", std_time
print "node std: ", std_node

print time_set
print node_set
