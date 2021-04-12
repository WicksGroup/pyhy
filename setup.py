'''
Connor Krill
September 2019
Setup file for the PyHy repository
Creates double-clickable files to run the python tools,
installs required python packages
'''
import os

def writeCommand(filename):
    '''Create a .command file and change its permissions to executable'''
    CWD = os.getcwd().replace(' ', '\ ')
    lines = [f'cd {os.path.join(CWD, "tools")}',
             f'python {filename + ".py"}']
    with open(filename + '.command', 'w') as f:
        f.write('\n'.join(lines))
    try:
        os.system(f'chmod 744 {filename + ".command"}')
    except Exception as e:
        print(f'Unable to change permissions on {filename}, try manually from terminal')
        raise e

# Write command file for data_viewer_GUI and inf_GUI
writeCommand('data_viewer_GUI')
writeCommand('inf_GUI')

# Write command file for data_dashboard
CWD  = os.getcwd().replace(' ', '\ ')
lines = [f'cd {os.path.join(CWD, "tools")}',
         f'open http://127.0.0.1:8000/',
          'python data_dashboard.py']
with open('data_dashboard.command', 'w') as f:
    f.write('\n'.join(lines))
os.system('chmod 744 data_dashboard.command')

# Write command file to launch jupyter notebooks
CWD = os.getcwd().replace(' ', '\ ')
lines = [f'cd {os.path.join(CWD)}',
         f'jupyter notebook']
with open('launch_jupyter.command', 'w') as f:
     f.write('\n'.join(lines))
os.system('chmod 744 launch_jupyter.command')


# install required python packages. Assumes you already have many common ones
command = "pip install -r requirements.txt"
os.system(command)
