import numpy as np

def pyecloud_device(device, coast_str, device_list, coast_strs, hl_pyecloud):
   if device not in device_list or coast_str not in coast_str:
       raise ValueError('Wrong device name or coast string in pyecloud_device!')

   device_ctr = device_list.index(device)
   coast_ctr = coast_strs.index(coast_str)
   hl_device = hl_pyecloud[:,device_ctr,coast_ctr,:]
   return hl_device

