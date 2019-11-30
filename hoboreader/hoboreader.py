# -*- coding: utf-8 -*-

import csv, re, datetime
import pandas as pd

class HoboReader():
    """
    """
    
    def __init__(self,fp=None):
        """
        """
        
        if fp: self.read_csv(fp)
    
    
    def read_csv(self,fp):
        """
        """
        
        with open(fp, newline='') as f:
            
            self.reader = csv.reader(f)
            
            self.header_row=self.get_header_row(self.reader)
            
            self.header_list=self.get_header_list(self.header_row)
            
            self.hobo_timezone_str=self.get_hobo_timezone_str(self.header_list)
            
            self.timezone=self.get_timezone(self.hobo_timezone_str)
            
            self.data_rows=self.get_data_rows(self.reader)
            
            self.data_columns=self.get_data_columns(self.data_rows)
            
            self.datetimes=self.get_datetimes(self.header_list,
                                              self.data_columns,
                                              self.timezone)
            
            
    def get_dataframe(self):
        
        def get_dataframe_column_multiindex(self,header_list):
            names=[]
            tuples=[]
            for header in self.header_list:
                for k in header.keys():
                    if not k in names and not k=='column': names.append(k)
                t=[]
                for name in names:
                    t.append(header.get(name,None))
                tuples.append(tuple(t))
    
            return pd.MultiIndex.from_tuples(tuples,names=names)
        
        
        columns=get_dataframe_column_multiindex(self,self.header_list)
        index=pd.Index(self.datetimes, name='datetimes')
        df=pd.DataFrame(columns=columns,data=self.data_rows,index=index)
        return df
            
            
    def get_datetimes(self,header_list,data_columns,tz):
        
        def get_date_time_column_index(header_list):
            for header_dict in header_list:
                if header_dict['title']=='Date Time':
                    return header_dict['column']
                
        col=get_date_time_column_index(header_list)
        timestamps=data_columns[col]
        return [self.convert_timestamp_to_datetime(x,tz) for x in timestamps]
        
            
    def get_hobo_timezone_str(self,header_list):
        for header_dict in header_list:
            tz=header_dict['timezone_str']
            if tz: return tz
            
            
    def get_timezone_timedelta(self,hobo_timezone_str):
        if hobo_timezone_str.startswith('GMT'):
            pass
        else:
            print('Warning: timezone code not understood - GMT assumed')
                    
        sign=hobo_timezone_str[-6:-5]
        if sign=='+':
            mod=1
        else:
            mod=-1
            
        time_str=hobo_timezone_str[-5:]
        dt=datetime.datetime.strptime(time_str, '%I:%M')
        hour=dt.hour*mod
        minutes=dt.minute*mod        
    
        return datetime.timedelta(hours=hour,minutes=minutes)
    
    
    def get_timezone(self,hobo_timezone_str):
        td=self.get_timezone_timedelta(hobo_timezone_str)
        return datetime.timezone(td,hobo_timezone_str)
    
    
    def convert_timestamp_to_datetime(self,timestamp,tz):
        dt=datetime.datetime.strptime(timestamp, '%m/%d/%y %I:%M:%S %p')
        return datetime.datetime(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,0,tz)
    
            
            
    def get_header_row(self,reader):
        for row in reader:
            if row[0]=='#':
                return row
            
            
    def get_header_list(self,header_row):
        result=[]
        for i,header in enumerate(header_row):
            d={}
            d['column']=i
            d['title']=self.get_title(header)
            d['timezone_str']=self.get_timezone_str(header)
            d['units']=self.get_units(header)
            d['logger_serial_number']=self.get_logger_serial_number(header)
            d['sensor_serial_number']=self.get_sensor_serial_number(header)
            result.append(d)
        return result
            
    
    def get_title(self,header):
        result = re.search('(.*?)((,| [(])|$)', header)
        try:
            return result.group(1)
        except AttributeError:
            return None
    
    def get_timezone_str(self,header):
        result = re.search('Date Time, (.*)', header)
        try:
            return result.group(1)
        except AttributeError:
            return None
    
    
    def get_units(self,header):
        result = re.search(', (.*) [(]', header)
        try:
            return result.group(1)
        except AttributeError:
            return None
    
    
    def get_logger_serial_number(self,header):
        result = re.search('LGR S/N: (.*?)[\),]', header)
        try:
            return result.group(1)
        except AttributeError:
            return None
    
    
    def get_sensor_serial_number(self,header):
        result = re.search('SEN S/N: (.*?)[\),]', header)
        try:
            return result.group(1)
        except AttributeError:
            return None
    
    
    def get_data_rows(self,reader):
        result=[]
        for row in reader:
            try:
                int(row[0])
                result.append(row)
            except ValueError:
                pass
        return result
    
    
    def get_data_columns(self,data_rows):
        return list(zip(*data_rows))
    
    
    
    
    
if __name__=="__main__":
    
    h=HoboReader()
    h.read_csv(r'..\tests\sample_hobo_data.csv')
    print(h.header_list)
    print(h.datetimes[:5])
    print(h.get_dataframe())
    
    