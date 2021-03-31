from in_out_class import read
from Solver import *
import Animation as Anim

input_folder = 'Crossroad/'
input_files_name_test = [input_folder+'parameter_template.txt',\
                          input_folder+'walls_positions_template.txt',\
                          input_folder+'group_template.txt']
output_file_name_test = input_folder+'case_output.txt'
scalar_output_name_test = input_folder+'scalar_output.txt'
default_save_name = input_folder+'anim_test.gif'

#run_social_force(input_files_name = input_files_name_test,output_file_name = output_file_name_test,scalar_output_name = scalar_output_name_test)
#Anim.load_output(output_file_name = output_file_name_test)
#Anim.create_animation(save_name = default_save_name ,input_files_name = input_files_name_test,output_file_name = output_file_name_test)

Anim.plot_density()