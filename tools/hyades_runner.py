'''
Connor Krill August 6, 2019
Functions to run hyades. Intended for use with the inf_GUI.
'''

import os
import shutil
import time
import logging
from excel_writer import writeExcel
import traceback
import pathlib

def batchRunHyades(inf_path, final_destination, copy_data_to_excel, debug=1):
    '''Use the runHyades and runHyadesPostProcess functions to simulate all .inf in a given folder.'''
    inf_path = os.path.abspath(inf_path)
    final_destination = os.path.abspath(final_destination)#.replace(' ','\ ')
    
    variables = ('Pres', 'Rho', 'Te', 'Tr', 'Ti', 'U', 'sd1')
    # setup a logging file
    filename   = 'hyades.log'
    log_format = '%(asctime)s %(levelname)s:%(message)s'
    datefmt    = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename=filename, 
                        format=log_format, datefmt=datefmt, level=logging.DEBUG)
    error_str = f'{filename} not in current directory, {os.getcwd()}'
    assert filename in os.listdir(os.getcwd()), error_str

    inf_files = sorted([os.path.splitext(f)[0] for f in os.listdir(inf_path)
                       if (f.endswith('.inf')) and ('setup' not in f)])
    

    print(inf_files[0])
    print(inf_path)
    if inf_files:
        if debug > 0:
            print(f'Found {len(inf_files)} .inf files: {", ".join(inf_files)} \n')
    else:
        raise Exception(f'Found no .inf files in {inf_path!r}')
    for run_name in inf_files:
        print(run_name)
        # changed a current directory to an abs path, i think this will fix it
        # creates a new folder named "run_name"
        try:
            t2complete = runHyades(inf_path, run_name,
                                   final_destination, debug=debug)
        except Exception:
            errorfile = f"{os.path.join(final_destination, run_name, run_name)}_ErrorLog.txt"
            with open(errorfile, "w") as log:
                traceback.print_exc(file=log)
                print(f"ERROR IN {run_name} - recording error in {errorfile} and skipping this .inf")
                continue
        logging.info(f'Complete HYADES run for {run_name} in {round(t2complete,1)} seconds')
        runHyadesPostProcess(os.path.join( os.path.abspath(final_destination), run_name, run_name),
                             variables, debug=debug) # post processing on all variables
        logging.info(f'Completed post processing for {run_name} variables: {", ".join(variables)}')

        if copy_data_to_excel:
            writeExcel(os.path.join(final_destination, run_name, run_name),
                       os.path.join(final_destination, run_name, run_name), variables)
        

        # move the folder and post processing to final_destination
#        if (final_destination != './') and (final_destination != os.getcwd()):
#            shutil.move(os.path.join(inf_path, run_name), final_destination)
#        print("FINISHED THE RUN AND POST LOOP FOR", run_name)
        if debug > 0:
            print()
    if debug > 0:
        print('Finished')



def runHyades(path, run_name, final_destination, debug=0):
    ''' Run hyades for a given run name
        Create a new directory and move all files into it.'''
    currpath = pathlib.Path(__file__).parent.absolute() 
    os.chdir(path)
    assert f'{run_name}.inf' in os.listdir(path), f'Did not find {run_name}.inf in {path!r}'
    
    try:
        t0 = time.time()
        command = f'hyades -c {run_name}'
        if debug==2:
            print(os.getcwd())
            print(os.listdir())
        if debug==1 or debug==2:
            print(f'Started {command!r}')
        os.system("rm SCRATCHX1")
        os.system(command)
        t1 = time.time()
        t2complete = t1 - t0
        if debug==1 or debug==2:
            print(f'Completed {command!r} in {str(int(t2complete))} seconds')
    except:
        raise Exception(f'Error occured running {command!r}')
    
    # create a directory for this run
    if not os.path.isdir(os.path.join(final_destination, run_name)):
        os.mkdir(os.path.join(final_destination, run_name))
        if debug==2:
            print(f'Createdy a directory named: {run_name}')
        
    # Get the names of all files to move
    files_to_move = [f for f in os.listdir(path) if (f.startswith(run_name)) and (not os.path.isdir(os.path.join(path, f))) ]
    print(files_to_move)
    try: # move the files
        for file in files_to_move:
            shutil.move(os.path.join(path, file), os.path.join(final_destination, run_name, file))
        if debug==2:
            print(f'Moved {str(len(files_to_move))} files to {run_name}')
    except:
        raise Exception(f'Error occured moving {file}')

    assert len(files_to_move)==4, f'Expected to find 4 files to move (.inf, .otf, .ppf, .tmf) - instead found {files_to_move}'
    os.chdir(currpath)
    return t2complete

    
def runHyadesPostProcess(run_name, variables, debug=0):
    '''Run HyadesPostProcess for a list of variables'''

    for var in variables:
        command = f'sh HyadesPostProcess.sh {run_name} {var}'
        os.system(command)
        if debug==2:
            print(f'Completed {command!r}')
            try:
                matching = [f for f in os.listdir(pathlib.Path(run_name+"_Pres.dat").parent.absolute()) if f.startswith(run_name) and f.endswith(f'{var}.dat')]
            except:
                print("uhhh pressure?")
            print(matching)
            #assert matching, f'Error: did not process {var}'
    if debug==1 or debug==2:    
        print(f'Completed HyadesPostProcess for {variables}')
        
        
        
if __name__=='__main__':
    inf_path = '../data/inf'
    final_destination = '../data/'
    copy_data_to_excel = True
    batchRunHyades(inf_path, final_destination, copy_data_to_excel)
