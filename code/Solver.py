########    Solver : Crowd simulation with force navigation model  #########
from numpy import *
import time
from in_out_class import read
from in_out_class import output
import Animation as Anim

##############################################################################
############################     Parameters     ##############################
##############################################################################
input_folder = 'Crossroad/'
input_files_name_test = [input_folder+'parameter_template.txt',\
                          input_folder+'walls_positions_template.txt',\
                          input_folder+'group_template.txt']
output_file_name_test = input_folder+'case_output.txt'
scalar_output_name_test = input_folder+'scalar_output.txt'



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
#########################     Force functions      ###########################
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

def agent_repulsion_Force(pos_agent_i,pos_agent_j,velocity_agent_i, \
                          velocity_agent_j,t_step):
    # From Helbing 2013
    Y_ab = (array(velocity_agent_j)-array(velocity_agent_j) )*t_step
    #e_j = vect(pos_agent_i,pos_agent_j)/dist_point(pos_agent_i,pos_agent_j)
    d_ab = array(pos_agent_j)-array(pos_agent_i)
    b = 0.5 * sqrt( ( norm(d_ab)+norm(d_ab+Y_ab)  )**2 - norm(Y_ab)**2 )
  
    return -2.1*exp(-b/0.3)* ((norm(d_ab)+norm(Y_ab))/2*b) \
        *0.5* (d_ab/norm(d_ab) + (d_ab+Y_ab)/norm(d_ab+Y_ab) )

def wall_repulsion_Force(pos_agent,wall):
    w_p = closest_point_seg(wall[0], wall[1], pos_agent)
    d_w = dist_point(pos_agent,w_p) #distance to the wall
    e_w = vect(pos_agent,w_p) / d_w
    # normal vector from the agent pointing toward the wall
    
    return -10*exp(-d_w/0.2)*e_w # Model from Helbing & Molnar 1998

def force_power_law(x_i,x_j,v_i,v_j,Ri,Rj,tho_0,k):
    xij=vect(x_j,x_i)
    vij=vect(v_j,v_i)
    a=norm(vij)**2
    b=-dot(xij,vij)
    c=norm(xij)**2-(Ri+Rj)**2
    d=b**2-(a*c)
    tho=(b-sqrt(d))/a
    if tho > 0:
      Fij=-((k*exp(-tho/tho_0)/(a*tho**2))*((2/tho)+(1/tho_0)))*(vij-(a*xij+b*vij)/sqrt(d))
    else:
      Fij=zeros(2)
    return Fij

def contact_force_agents(pos_agent_i,pos_agent_j,radius_i,radius_j):
    # Contact force as defined in Helbing et al. 2000 (also in Moussaid 2011)
    k= 10  # defined in Helbing 2000 for dt=0.1
    vect_ij =vect(pos_agent_j,pos_agent_i)
    e_cf = vect_ij / norm(vect_ij) # normlized vector fom the direction of force
    if norm(vect_ij) < radius_i+radius_j :
        return k*(radius_i + radius_j - norm(vect_ij))*e_cf
    else :
        return zeros(2)

def contact_force_walls(pos_agent,wall,radius):
    # Contact force as defined in Helbing et al. 2000 (also in Moussaid 2011)
    k= 50  # defined in Helbing 2000 for dt=0.1
    w_p = closest_point_seg(wall[0], wall[1], pos_agent)
    d_w = dist_point(pos_agent,w_p) #distance to the wall
    e_w = vect(w_p,pos_agent) / d_w
    # normal vector from the agent pointing toward the wall
    if d_w < radius:
        return k*(radius- d_w)*e_w 
    else :
        return zeros(2)

##############################################################################
#########################     Augular dependence       #######################
##############################################################################

def angular_dependence(pos_agent_i,pos_agent_j,velocity_agent_i):
    v_a = norm(velocity_agent_i)
    e_j = vect(pos_agent_i,pos_agent_j)/dist_point(pos_agent_i,pos_agent_j)
    x = velocity_agent_i/v_a
    cos_angle=dot((velocity_agent_i/v_a),e_j)
    
    lb= 0.1 #Model from Helbing & Molnar 1998
    angular_dependent_prefactor = (lb + (1 - lb)*(1+cos_angle)/2) #Model from Helbing & Molnar 1998
    return angular_dependent_prefactor

##################


##############################################################################
#                                                                            #  
#                                                                            # 
#                               SOLVER                                       #
#                                                                            #
#                                                                            #
##############################################################################
def run_social_force(input_files_name = input_files_name_test,output_file_name = output_file_name_test,scalar_output_name = scalar_output_name_test):
    
    ''' Run the script defined by the input files selected and create an output
     file with the selected name.'''
    
    ## Read the input file (not done yet)
    force_law,mean_radius,mean_velocity,std,max_it,k,tho_0 = \
        read.read_parameters(input_files_name[0])
    Position, goals, Checkpoints = read.read_group(input_files_name[2]) # Checkpoints is the Array of the current goals
    walls = read.read_walls_positions(input_files_name[1])
    print('-- input successfuly read')
          
    ## Initialise with the variables read before
    N_agents = len(Position)
    N_walls = len(walls)
    t_step = 0.3*(mean_radius/mean_velocity) # CFL criteria besed time step 
    V_max = random.normal(loc=mean_velocity, scale=std, size=N_agents)
    Radius = random.normal(loc=mean_radius, scale=std, size=N_agents)
    #Checkpoints = zeros((N_agents,len(goals)))
    Velocity = random.rand(N_agents,2) # Array of the velocities
    UP_Velocity=Velocity # Velocity at time t+dt
    UP_Position=Position # Position at time t+dt
    Density=0
    norm_v=[]
    
    ## Create an output file :
    output.create_output_file(output_file_name)
    output.line_output('timestep  = '+str(t_step)+' [s] \n',output_file_name)
    ## Write the initial pos tion and Velocity
    for i in range(N_agents):
        output.white_output(i,Position[i],Velocity[i], \
                0,output_file_name)
    
    ## Begin simulation
    time_step_counter=0
    while abs(sum(Checkpoints))!=len(Checkpoints.flatten()) :
        print(str(time_step_counter) + "/" + str(max_it))
     ## Whilee all the agents havent reach all their goals
        time_step_counter+=1
        if max_it > 0 : 
            if time_step_counter >= max_it :
                #if the maximal number of iteration is reached then the sim is 
                # artificialy terminated by setting all the check points to 1
                Checkpoints = ones((N_agents,len(goals)))
                print('-- Maximal number of iterations reached')
        ## Agent loop :
        for i in range(N_agents) :
            if abs(sum(Checkpoints[i]))<len(goals) :
                
                # If the agents haven't reach all his goals yet
             
               # Compute the Forces acting on agent i
               # Wall loop :
               F_wall=zeros(2)
               for w in range(N_walls):
                   F_wall+=wall_repulsion_Force(Position[i],walls[w])
                   F_wall+=contact_force_walls(Position[i],walls[w],Radius[i])
             
               # Other agents loop :
               F_agents=zeros(2)
               for j in range(N_agents):
                   if i!=j and abs(sum(Checkpoints[j]))<len(goals) :
                      # only the active agents are taken into account
                      if force_law==0:#"agent_repulsion_Force":
                            prefactor=angular_dependence(Position[i],Position[j],Velocity[i])
                            F_agents+=prefactor*agent_repulsion_Force(Position[i],\
                                                                        Position[j],\
                                                                        Velocity[i],\
                                                                        Velocity[j],\
                                                                        t_step    )
                      elif force_law==1: #"force_power_law":
                            F_agents+=force_power_law(Position[i],\
                                                      Position[j],\
                                                      Velocity[i],\
                                                      Velocity[j],\
                                                      Radius[i],Radius[j],\
                                                      tho_0,k)
                      F_agents+=contact_force_agents(Position[i],Position[j],Radius[i],Radius[j])
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
      
          ### if the agent is into the box for the density
            if (Position[i,0] >= 4 and Position[i,0] <= 8 and Position[i,1] >= -4 and Position[i,1] <= 0):
                Density+=1
                
          ### determine the norm of velocity for each agent
            norm_v.append(norm(Velocity[i]))
      
        ### Position and velocity of all agents are exported
            output.white_output(i,UP_Position[i],UP_Velocity[i], \
                                time_step_counter,output_file_name)
        
        ### We want the density and the mean velocity
        mean_velocity=mean(norm_v)
        output.scalar_output(mean_velocity,Density,scalar_output_name)
        Density=0
                                      
        #### Position and Velocity are Updated
        Velocity=UP_Velocity
        Position=UP_Position
    
    ### Final Position output :
    Velocity = zeros((N_agents,2)) # No agents is moving anymore
    for i in range(N_agents):
        output.white_output(i,Position[i],Velocity[i], \
                    time_step_counter+1,output_file_name)
    print('-- Simulation completed')
    return None
    