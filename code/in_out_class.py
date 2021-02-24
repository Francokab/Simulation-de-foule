########    Classes Used by the solver and the post-processing code  #########
from numpy import *

class output :
    
    def create_output_file(file_name):
        '''  Create an output file and write the headers''' 
        new_file = open(file_name,'w')
        new_file.write('timeStep  pedestrianId  x \t y \t Vx \t Vy \n')
        new_file.close()
        print("-- Output file created")
        return None
    
    def line_output(str_line,output_file_name):
        output_file = open(output_file_name,'a')
        output_file.write(str_line)
        output_file.close()
        return None
    
    def white_output(agent_id,agent_position,agent_velocity, \
                     time_step_counter,output_file_name):
        '''  Write one line of the output file ''' 
        output_file = open(output_file_name,'a')
        output_file.write(str(time_step_counter)+'\t'\
                              +str(agent_id)+'\t'\
                              +str(agent_position[0])+'\t'\
                              +str(agent_position[1])+'\t'\
                              +str(agent_velocity[0])+'\t'\
                              +str(agent_velocity[1])+'\n' )
        output_file.close()

        return None

class read :
    
    
    
    def read_parameters(parameters_file_name):
        ''' Read and return as an array :
            Mean radius, Mean velocity , stand. Dev.'''
        parameters = loadtxt(parameters_file_name,skiprows=2)
        return parameters
        
    
    
    def read_agents_positions(agents_positions_file_name):
        ''' Read the file containing the position of the agents.
            Two options are available : user_defined or random. 
            The function returns an array'''
        file = open(agents_positions_file_name,'r')
        header = file.readlines()[:10]
        method = (header[-1].strip()).split(',')
        if method[0]=='user_defined':
        ## first method
            Positions = loadtxt(agents_positions_file_name,\
                               skiprows=12,delimiter=',')
            return Positions
        elif method[0]=='random':
            N_agents = int(method[1])
            ## get the positions of the diagonal corner of the box
            Corners_positions = loadtxt(agents_positions_file_name,\
                               skiprows=12,delimiter=',')
        
            x_max = max(Corners_positions[0,0],Corners_positions[1,0]) 
            x_min = min(Corners_positions[0,0],Corners_positions[1,0]) 
            y_max = max(Corners_positions[0,1],Corners_positions[1,1]) 
            y_min = min(Corners_positions[0,1],Corners_positions[1,1]) 
            
            ## Crete the array of the positions
            Positions = zeros( (N_agents,2) )
            
            ## Randomly feel the array
            for i in range(N_agents):
                x = random.uniform(x_min, x_max)
                y = random.uniform(y_min, y_max)
                Positions[i] = array([x, y])
            return Positions
            
            return None
        else :
            print("/!/ -- Wrong method calling -- /!/")
            return None
        
    def read_walls_positions(agents_positions_file_name):
        '''Read the file containing the position of the walls.
        The function returns an array with a dimention (2,N_walls)'''
        raw_walls=loadtxt(agents_positions_file_name,\
                           skiprows=12,dtype=str)
        N_walls = len(raw_walls)    
        walls = zeros((N_walls,2,2))
        for i in range(N_walls):
            x,y = raw_walls[i,0].split(',')
            walls[i,0] = array([float(x),float(y)]) # first point of the wall
            x,y = raw_walls[i,1].split(',')
            walls[i,1] = array([float(x),float(y)]) # second point of the wall
        return walls
    
    def read_goals(goals_file_name):
        '''Read the file containing the position of the goal.
        The function returns a list which contain points and/or segments'''
        file = open(goals_file_name,'r')
        raw_goals = file.readlines()[9 :]
        goals = []
        
        for g in raw_goals:
            if len((g.strip()).split(' '))==2:
            # If the goal treated is a segment
                raw_seg = (g.strip()).split(' ')
                x1,y1 = raw_seg[0].split(',')
                x2,y2 = raw_seg[1].split(',')
                goals.append( [[float(x1),float(y1)] , [float(x2),float(y2)] ])
            elif len((g.strip()).split(' '))==1:
            # If the goal treated is a point
                x,y = g.split(',')
                goals.append( [float(x),float(y)])
            else :
                raise ValueError("Wrong goal format used ")
        return goals

    def read_group(group_file_name):
        file = open(group_file_name,'r')
        diff_group = file.readlines()[16 :]
        goals = []
        i = 0
        while diff_group[i].strip().split()[0] != "random" and diff_group[i].strip().split()[0] != "manual":
            if len((diff_group[i].strip()).split(' '))==2:
            # If the goal treated is a segment
                raw_seg = (diff_group[i].strip()).split(' ')
                x1,y1 = raw_seg[0].split(',')
                x2,y2 = raw_seg[1].split(',')
                goals.append( [[float(x1),float(y1)] , [float(x2),float(y2)] ])
            elif len((diff_group[i].strip()).split(' '))==1:
            # If the goal treated is a point
                x,y = diff_group[i].split(',')
                goals.append( [float(x),float(y)])
            else :
                raise ValueError("Wrong goal format used ")
            i += 1
        
        #at this point, we've meet the first type of distribution of the NPC and how many there are
        Box_corner = []
        Box_agents = []
        Box_goals = []
        Man_Position = []
        Man_goals = []

        #print(diff_group[i]) test to read the last line
        if diff_group[i].strip().split()[0] == "random":
            i += 1
            switch_to_manual = False
            while i != len(diff_group) and not switch_to_manual :
                if diff_group[i].strip().split()[0] == "manual":
                    switch_to_manual = True
                else:
                    raw_seg = (diff_group[i].strip()).split(' ')
                    x1,y1 = raw_seg[0].split(',')
                    x2,y2 = raw_seg[1].split(',')
                    N1 = raw_seg[2]
                    g = raw_seg[3].split(',')
                    for j in range(len(g)):
                        g[j] = int(g[j])
                    Box_corner.append( [[float(x1),float(y1)] , [float(x2),float(y2)] ])
                    Box_agents.append(int(N1))
                    Box_goals.append(g)
                    i += 1

        if switch_to_manual:
            i += 1
            while i != len(diff_group):
                raw_seg = (diff_group[i].strip()).split(' ')
                x1,y1 = raw_seg[0].split(',')
                g = raw_seg[1].split(',')
                for j in range(len(g)):
                    g[j] = int(g[j])
                Man_Position.append([float(x1),float(y1)])
                Man_goals.append(g)
                i += 1

        N_agents = int(sum(Box_agents) + len(Man_Position))
        
        Positions = zeros( (N_agents,2) )
        incr = 0
        for i in range(len(Box_corner)):
            x_max = max(Box_corner[i][0][0],Box_corner[i][1][0])
            x_min = min(Box_corner[i][0][0],Box_corner[i][1][0])
            y_max = max(Box_corner[i][0][1],Box_corner[i][1][1])
            y_min = min(Box_corner[i][0][1],Box_corner[i][1][1])
            
            ## Randomly feel the array 
            for j in range(Box_agents[i]): 
                x = random.uniform(x_min, x_max)
                y = random.uniform(y_min, y_max)
                Positions[incr+j] = array([x, y])
            incr += Box_agents[i]
        
        for i in range(len(Man_Position)):
            Positions[incr+i] = array(Man_Position[i])
            
        #here, we know all the positions of the agents and their goals
        
        Checkpoints = ones((N_agents,len(goals)))
        other_incr=0
        for i in range(len(Box_goals)): #first we do it for the random part, according to the creation of Positions
            series_of_goals=Box_goals[i]
            for h in range(Box_agents[i]):   
                for j in range(len(series_of_goals)):
                    objectif=series_of_goals[j]
                    Checkpoints[other_incr][objectif]=0
                other_incr+=1

        for i in range(len(Man_goals)): #then we do it for the manual part
            series_of_goals=Man_goals[i]
            for j in range(len(series_of_goals)):
                objectif=series_of_goals[j]
                Checkpoints[other_incr+i][objectif]=0
                
        return Positions,goals,Checkpoints