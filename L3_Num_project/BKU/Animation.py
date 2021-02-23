## Animation : Post-process the output of the Solver to create an animation ##

from numpy import *
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from in_out_class import read



##############################################################################
############################     Parameters     ##############################
##############################################################################
input_folder = 'Complex_scenario/'
input_files_name_test = [input_folder+'parameter_template.txt',\
                         input_folder+'agents_positions_template.txt',\
                          input_folder+'walls_positions_template.txt',\
                          input_folder+'goals_template.txt'   ]
output_file_name_test = input_folder+'case_output.txt'

default_save_name = input_folder+'anim_test.gif'

##############################################################################
##########################     Functions        ##############################
##############################################################################

def load_output(output_file_name = output_file_name_test):
    ''' Read the output data file and returns the time step (float), 
    The position of the agents (array size=(itteration,N_agents,2)),
    The velocity of the agents (array size=(itteration,N_agents,2))'''
    
    ## get the time step 
    file = open(output_file_name,'r')
    file.readline()
    dt = float(((file.readline()).strip()).split(' ')[-2])
    
    
    ## Get Positions and velocity 
    raw_data = loadtxt(output_file_name ,skiprows=2)
    N_iterations = int(raw_data[-1,0])+1 # Nb of iterations
    N_agents = int(raw_data[-1,1])+1 # Nb of agents
    # Creation of the array Positions and Velocity
    Positions = zeros( (N_iterations,N_agents,2) )
    Velocities =  zeros( (N_iterations,N_agents,2) )
    for line in raw_data:
        it, agent, x,y ,v_x,v_y = line
        it = int(it)
        agent = int(agent)
        Positions[it,agent,:] = array( [x,y] )
        Velocities[it,agent,:] = array( [v_x,v_y] )    
    
    return dt, Positions, Velocities



##############################################################################
#                                                                            #  
#                                                                            # 
#                           Animation Function                               #
#                                                                            #
#                                                                            #
##############################################################################

def create_animation(save_name = default_save_name ,
                    input_files_name = input_files_name_test,
                    output_file_name = output_file_name_test):
    
    # Get useful values :
    Walls = read.read_walls_positions(input_files_name[2])
    Goals = read.read_goals(input_files_name[3])
    dt, Positions, Velocities = load_output(output_file_name)
    N_agents = len(Positions[0]) # Number of agents
    N_frames = len(Positions) # Number of frame to animate
    
    
        
    ## Creation of the Canevas :
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    
    
    ## Plot the Walls :
    for wall in Walls :
        ax.plot([wall[0,0],wall[1,0]],[wall[0,1],wall[1,1]],lw=2,color='k')
        
        
    
    # Initialize the patches that rpz the agents
    Agents = [ax.add_patch(plt.Circle((pos[0], pos[1]), 0.3) ) 
              for pos in Positions[0]]
    
    
    # Get all Goal Points
    goal_points = []
    for g in Goals :
        try :
            # if the goal is a segment : no exeption is created
            goal_points.append([g[0][0],g[0][1]])
            goal_points.append([g[1][0],g[1][1]])
        except :
            # if the geol is a point an exception is created 
            # and the code read this line.
            goal_points.append( [g[0],g[1]] )
    goal_points = array(goal_points) # allow to use the np methods
    
    
    # Set the Size of the final canevas 
    xmin = min( [ min(goal_points[:,0]),  min(Walls[:,:,0].flatten()) ] )*1.1
    xmax = max( [ max(goal_points[:,0]), max(Walls[:,:,0].flatten()) ]  )*1.1
    ymin = min( [ min(goal_points[:,1]), min(Walls[:,:,1].flatten()) ] )*1.2
    ymax = max( [ max(goal_points[:,1]), max(Walls[:,:,1].flatten()) ] )*1.1
    
    
    if abs(xmin)-1e-3 < 0 : xmin = -0.5
    if abs(ymin)-1e-3 < 0 : ymin = -0.5 
    if abs(xmax)-1e-3 < 0 : xmax = 0.5
    if abs(ymax)-1e-3 < 0 : ymax = 0.5
        
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    
    # time marker centered below the anim:
    time_text = ax.text(0.5*(xmin+xmax),ymin+abs(ymin*0.05) , 'Time:')
        
    
    
    
    
    def animate(t_step):
        # global N_agents
        arrows = []
        ax.patches = ax.patches[0:N_agents]
        t_step += 1
        for i in range(N_agents):
            Agents[i].set_center((Positions[t_step,i,0], Positions[t_step,i,1]))
            arrows.append(ax.add_patch(plt.Arrow(Positions[t_step,i,0], 
                                                       Positions[t_step,i,1],
                                                       Velocities[t_step,i,0], 
                                                       Velocities[t_step,i,1], 
                                                       width=0.3,
                                                       color='red')))
        time_text.set_text('Time: '+str(round(dt*t_step,2))+'s')
        return None
    
    
    #Set the the interval between frames so the visualisation is at real speed
    interval_delay = int(dt*1000) # milliseconds between frames (must be an int)
    
    anim = animation.FuncAnimation(fig, animate, N_frames, repeat=False,
                                   interval=interval_delay)
    
    anim.save(save_name, writer='Pillow')
    
    return None
