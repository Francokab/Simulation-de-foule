########    Solver : Crowd simulation with force navigation model  #########
from numpy import *
import time
from in_out_class import input
from in_out_class import output

##############################################################################
############################     Parameters     ##############################
##############################################################################
input_files_name_test = ['Input_templates/parameter_template.txt',\
                         'Input_templates/agents_positions_template.txt',\
                          'Input_templates/walls_positions_template.txt',\
                          'Input_templates/goals_template.txt'   ]
output_file_name_test = 'test_output.txt'





##############################################################################
##########################     Functions        ##############################
##############################################################################
def norm(vector):
    '''  norm of a vector''' 
    return sqrt(vector[0]**2+vector[1]**2)
    
def vect(a,b):
    '''  vector from a pointing toward b''' 
    return array([b[0]-a[0],b[1]-a[1]])

def dist_point(a,b):
    '''  return the norm of the distance between 2 points : a and b''' 
    x,y = vect(a,b)
    return sqrt(x**2+y**2)
    

def closest_point_seg(a,b,c) :
    '''  return the closest point to c on the segment [ab]
     using a dichotomi method''' 
    cut_off = dist_point(a,b)*1e-4
    left = array(a) # left end of the considered segment
    right = array(b) # left end of the considered segment
    
    while dist_point(left,right) > cut_off:
        mid_vec = (right-left)/2
        if dist_point(left,c) < dist_point(right,c):
            right = left + mid_vec
        else :
            left = right - mid_vec

    return left + mid_vec



def dist_point_seg(a,b,c):
    ''' return the norm of the minimal distance between a point 'c' 
     and a segment [a,b]''' 
    return dist_point(c, closest_point_seg(a,b,c))





##############################################################################
#### Forces ####
##############################################################################

def direction_Force(V_max_agent,agent_position,agent_velocity,goal) :
    relaxation_time = 0.5 #[s]
     ## As Goal could be point or segment it come from a list and thus 
     # have to be transformed into an array in order to fit with the
     # other variables.
    goal=array([goal[0],goal[1]])
    if len(goal.flatten())>2 :
        ## the goal is a segment
        e_direction= (closest_point_seg(goal[0],goal[1],agent_position)\
            -agent_position)/dist_point_seg(goal[0],goal[1],agent_position)
    else :
        ## the goal is a point
        e_direction = vect(agent_position,goal)/dist_point(goal,agent_position)
    
    # def of the direction Force
    F_dir = ( e_direction*V_max_agent-agent_velocity)/relaxation_time    
    return  F_dir

def agent_repulsion_Force(pos_agent_i,pos_agent_j,velocity_agent_j,t_step):
    v_b = norm(velocity_agent_j)
    e_j = vect(pos_agent_i,pos_agent_j)/dist_point(pos_agent_i,pos_agent_j)
    b = 0.5 * sqrt( (dist_point(pos_agent_i,pos_agent_j) \
             + norm(pos_agent_j-pos_agent_i - v_b*t_step*e_j)   )**2 \
             - (v_b*t_step)**2)
    return -2.1*exp(-b/0.3)*e_j # Model from Helbing & Molnar 1998

def wall_repulsion_Force(pos_agent,wall):
    w_p = closest_point_seg(wall[0], wall[1], pos_agent)
    d_w = dist_point(pos_agent,w_p) #distance to the wall
    e_w = vect(pos_agent,w_p) / d_w
    # normal vector from the agent pointing toward the wall
    
    return -10*exp(-d_w/0.2)*e_w # Model from Helbing & Molnar 1998

##################








##############################################################################
#                                                                            #  
#                                                                            # 
#                               SOLVER                                       #
#                                                                            #
#                                                                            #
##############################################################################
def run_script(input_files_name = input_files_name_test,\
        output_file_name = output_file_name_test):
    
    ''' Run the script defined by the input files selected and create an output
     file with the selected name.'''
    
    ## Read the input file (not done yet)
    mean_radius,mean_velocity,std = input.read_parameters(input_files_name[0])
    Position = input.read_agents_positions(input_files_name[1])
    walls = input.read_walls_positions(input_files_name[2])
    goals = input.read_goals(input_files_name[3])
    print('-- input successfuly read')
          
    ## Initialise with the variables read before
    N_agents = len(Position)
    N_walls = len(walls)
    t_step = 0.5*(mean_radius/mean_velocity) # CFL criteria besed time step 
    V_max = random.normal(loc=mean_velocity, scale=std, size=N_agents)
    Radius = random.normal(loc=mean_radius, scale=std, size=N_agents)
    Velocity = zeros((N_agents,2)) # Array of the velocities
    Checkpoints = zeros((N_agents,len(goals))) # Array of the current goals
    UP_Velocity=Velocity # Velocity at time t+dt
    UP_Position=Position # Position at time t+dt
    
    ## Create an output file :
    output.create_output_file(output_file_name)
    output.line_output('timestep  = '+str(t_step)+' [s] \n',output_file_name)
    ## Write the initial position and Velocity
    for i in range(N_agents):
        output.white_output(i,Position[i],Velocity[i], \
                0,output_file_name)
    
    ## Begin simulation
    time_step_counter=0
    while abs(sum(Checkpoints))!=len(Checkpoints.flatten()):
     ## Whilee all the agents havent reach all their goals
        time_step_counter+=1
     
        ## Agent loop :
        for i in range(N_agents) :
            if abs(sum(Checkpoints[i]))<len(goals) :
                
                # If the agents haven't reach all his goals yet
             
               # Compute the Forces acting on agent i
               # Wall loop :
               F_wall=zeros(2)
               for w in range(N_walls):
                   F_wall+=wall_repulsion_Force(Position[i],walls[w])
             
               # Other agents loop :
               F_agents=zeros(2)
               for j in range(N_agents):
                   if i!=j and abs(sum(Checkpoints[j]))<len(goals) :
                       # only the active agents are taken into account
                       F_agents+=agent_repulsion_Force(Position[i],\
                                                       Position[j],\
                                                       Velocity[j],\
                                                       t_step    )
               # Direction Force :
               F_goal=zeros(2)
               # finding the current goal of agent i
               g=0
               while Checkpoints[i,g]>0:
                   g+=1
               F_goal=direction_Force(V_max[i],Position[i],\
                                      Velocity[i],goals[g])
        
        
               ## The velocity of agent i is updated :
               #  Folowing the steps described in Helbing & Molnar 1998
               w_up=Velocity[i]+(t_step)*(F_wall+F_agents+F_goal)
    
               if norm(w_up)<=V_max[i]:
                   UP_Velocity[i]=w_up
               else :
                   UP_Velocity[i]=(V_max[i]/norm(w_up))*w_up
               # Position and velocity are updated :
               
               UP_Position[i] = Position[i] + UP_Velocity[i]*t_step
               
            
            
               ## Check if the agents have reached its current goal:
               if len(array(goals[g]).flatten())>2:
               # if the goal is a segment
                   if dist_point(UP_Position[i], closest_point_seg(goals[g][0],\
                                                             goals[g][1],\
                                                            UP_Position[i] )) \
                   <=Radius[i]:
                    # if the agent touch the goal :
                        Checkpoints[i,g]=1
                        print('Agent '+str(i)+' reached goal '+str(g))
               else :
               # if the goal is a dot:
                  if dist_point(UP_Position[i], goals[g])<=Radius[i]:
                      Checkpoints[i,g]=1
                      print('Agent '+str(i)+' reached goal '+str(g))
                      
                      
          ### If the agents have reached all its goals then it stops
            else:
                UP_Velocity[i] = zeros(2)
      
        ### Position and velocity of all agents are exported
            output.white_output(i,UP_Position[i],UP_Velocity[i], \
                                time_step_counter,output_file_name)
                
        #### Position and Velocity are Updated
        Velocity=UP_Velocity
        Position=UP_Position
    
    ### Final Position output :
    Velocity = zeros((N_agents,2)) # No agents is moving anymore
    for i in range(N_agents):
        output.white_output(i,Position[i],Velocity[i], \
                    time_step_counter+1,output_file_name)
    print('-- Simulation complited')



    