import opendssdirect
import numpy as np
import pandas as pd
from os import getcwd, chdir

class PowerFlow:
    def __init__(self, path:str , kV, loadmult:float = 1):
        try:
            open(path,'r')
        except:
            raise Exception("O arquivo não existe")
        
        self.__path = path
        self.__kV = kV
        self.__dss = opendssdirect
        self.__loadmult = loadmult


    def get_path(self):
        return self.__path

    def get_kV(self):
        return self.__kV

    def get_loadmult(self):
        return self.__loadmult

    def run_power_flow(self):
        directory = getcwd()
        self.__dss.run_command(f"Compile {self.__path}")
        self.__dss.run_command(f"Set voltagebases=[{self.__kV}]")
        self.__dss.run_command("calcv")
        self.__dss.run_command(f"Set loadmult = {self.__loadmult}")
        self.__dss.Solution.Solve()
        chdir(directory)

    def get_erros(self):
        return self.__dss.Error.Description()

    def get_all_bus_names(self):
        return self.__dss.Circuit.AllBusNames()

    def get_all_v_pu_angle_pandas(self):  
        all_v_pu = self.__get_all_v_pu()
        all_ang = self.__get_all_ang()
        
        df_bus_names = pd.DataFrame(self.get_all_bus_names(), columns =['bus_names'])
        df_v_pu = pd.DataFrame(all_v_pu, columns =['v_pu_a','v_pu_b', 'v_pu_c'])
        df_ang = pd.DataFrame(all_ang, columns =['ang_a', 'ang_b', 'ang_c'])
        result = pd.concat([df_bus_names, df_v_pu, df_ang], axis=1, sort=False)

        result['phases']  = self.__get_all_num_ph()    
        return result

    def __get_bus_v_pu_ang(self, bus: str):
        self.__dss.Circuit.SetActiveBus(bus)
        return self.__dss.Bus.puVmagAngle()

    def __get_bus_ph(self, bus: str):
        self.__dss.Circuit.SetActiveBus(bus)
        return self.__dss.Bus.Nodes()
    

    def __get_bus_v_pu(self, bus: str):
        v_pu_ang_dss = self.__get_bus_v_pu_ang(bus)
        list_ph = self.__get_bus_ph(bus)
        v_pu = [np.NaN , np.NaN , np.NaN]
        v_pu_dss = []
        for indx in range(0, len(v_pu_ang_dss), 2):
            v_pu_dss.append(v_pu_ang_dss[indx])
        
        indx = 0
        for ph in list_ph:
            v_pu[ph-1] = v_pu_dss[indx]
            indx += 1

        return v_pu

    def __get_bus_ang(self, bus: str):
        v_pu_ang_dss = self.__get_bus_v_pu_ang(bus)
        list_ph = self.__get_bus_ph(bus)
        ang = [np.NaN  , np.NaN , np.NaN ]    
        ang_dss = []

        for indx in range(1, len(v_pu_ang_dss)+1, 2):
            ang_dss.append(v_pu_ang_dss[indx])
        
        indx = 0
        for ph in list_ph:
            ang[ph-1] = ang_dss[indx]
            indx += 1

        return ang


    def __get_all_v_pu(self):
        all_bus_names = self.get_all_bus_names()
        all_v_pu = []
        for bus in all_bus_names:
            v_pu = self.__get_bus_v_pu(bus)
            all_v_pu.append(v_pu)

        return all_v_pu

    def __get_all_ang(self):
        all_bus_names = self.get_all_bus_names()
        all_ang = []
        for bus in all_bus_names:
            ang = self.__get_bus_ang(bus)
            all_ang.append(ang)

        return all_ang
    
    def __get_all_num_ph(self):
        all_bus_names = self.get_all_bus_names()
        all_num_ph = []
        for bus in all_bus_names:
            ph = self.__get_bus_ph(bus)
            # print(ph)
            if ph == [1, 2, 3]:
                ph_abc = 'abc'
            elif ph == [1, 2]:
                ph_abc = 'ab'
            elif ph == [1, 3]:
                ph_abc = 'ac'
            elif ph == [2, 3]:
                ph_abc = 'bc'
            else:
                ph_abc = 'ERR'

            all_num_ph.append(ph_abc)

        return all_num_ph

