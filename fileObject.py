import time
import os

unit_seconds = {
            "day": 24 * 60 * 60,
            "week": 7 * 24 * 60 * 60,
            "month": 30 * 24 * 60 * 60,
            "year": 365 * 24 * 60 * 60,
}

class FileObject:

    def __init__(self,full_path):
        self.full_path = full_path
        self.file_name = os.path.basename(full_path)
        self.flags = [] #<-- is this necessary since we will always check the flags upon change
        

    def is_file_old(self,selected_time_unit,selected_time_value):
        # --> returns true if the file has aged past selected time stamp #
        #file_last_modified = os.path.getmtime(full_path)
        file_created = os.path.getctime(self.full_path)
        checkingAge = file_created #we want to check file_create, change if wanted
        
        # Check if file was modified past the selected time threshold
        current_time = time.time()
        selected_unit_seconds = unit_seconds.get(selected_time_unit, 0)
        cutoff_time = current_time - (selected_time_value * selected_unit_seconds)
        if checkingAge < cutoff_time:
            return True
        else:
            return False
        
    



