# -*- coding: utf-8 -*-

import csv, re, datetime
import pandas as pd
import numpy as np


class HoboReader():
    """A class for reading in a Hobo data csv file
    """
    
    def __init__(self,fp=None):
        """
        
        Arguments:
            fp (str) - a filepath
        
        """
        
        if fp: self.read_csv(fp)
    
        
    def read_csv(self,fp):
        """Reads in the csv file and converts the information into attributes
        
        Arguments:
            fp (str) - a filepath
        
        """
        
        # Internal functions
        
        def get_datetimes(header_list,data_columns,tz):
            
            def get_date_time_column_index(header_list):
                for header_dict in header_list:
                    if header_dict['title'] in ['Time','Date Time']:
                        return header_dict['column']
                    
            col=get_date_time_column_index(header_list)
            timestamps=data_columns[col]
            return [convert_timestamp_to_datetime(x,tz) for x in timestamps]
            
                
        def get_hobo_timezone_str(header_list):
            for header_dict in header_list:
                tz=header_dict['timezone_str']
                if tz: return tz
                
                
        def get_timezone_timedelta(hobo_timezone_str):
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
        
        
        def get_timezone(hobo_timezone_str):
            td=get_timezone_timedelta(hobo_timezone_str)
            return datetime.timezone(td,hobo_timezone_str)
        
        
        def convert_timestamp_to_datetime(timestamp,tz):
            dt=datetime.datetime.strptime(timestamp, '%m/%d/%y %I:%M:%S %p')
            return datetime.datetime(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,0,tz)
        
                
        def get_header_row(reader):
            for row in reader:
                if row[0]=='#':
                    return row
                
                
        def get_header_list(header_row):
            result=[]
            for i,header in enumerate(header_row):
                d={}
                d['column']=i
                d['title']=get_title(header)
                d['timezone_str']=get_timezone_str(header)
                d['units']=get_units(header)
                d['logger_serial_number']=get_logger_serial_number(header)
                d['sensor_serial_number']=get_sensor_serial_number(header)
                result.append(d)
            return result
                
        
        def get_title(header):
            result = re.search('(.*?)((,|[(])|$)', header)
            try:
                return result.group(1).strip()
            except AttributeError:
                return None
        
        def get_timezone_str(header):
            result = re.search('Time, (.*)', header)
            try:
                return result.group(1)
            except AttributeError:
                return None
        
        
        def get_units(header):
            result = re.search(', (.*)[(]', header)
            try:
                return result.group(1).strip()
            except AttributeError:
                return None
        
        
        def get_logger_serial_number(header):
            result = re.search('LGR S/N: (.*?)[\),]', header)
            try:
                return result.group(1)
            except AttributeError:
                return None
        
        
        def get_sensor_serial_number(header):
            result = re.search('SEN S/N: (.*?)[\),]', header)
            try:
                return result.group(1)
            except AttributeError:
                return None
        
        
        def get_data_rows(reader):
            result=[]
            for row in reader:
                try:
                    int(row[0])
                    result.append(row)
                except ValueError:
                    pass
            return result
        
        
        def get_data_columns(data_rows):
            return list(zip(*data_rows))
        
        
        # Start
        
        with open(fp, newline='') as f:
            
            self.reader = csv.reader(f)
            
            self.header_row=get_header_row(self.reader)
            #print(self.header_row)
            
            self.header_list=get_header_list(self.header_row)
            #print(self.header_list)
            
            self.hobo_timezone_str=get_hobo_timezone_str(self.header_list)
            
            self.timezone=get_timezone(self.hobo_timezone_str)
            
            self.data_rows=get_data_rows(self.reader)
            
            self.data_columns=get_data_columns(self.data_rows)
            
            self.datetimes=get_datetimes(self.header_list,
                                         self.data_columns,
                                         self.timezone)
            
            
    def get_sensor_serial_number(self):
        for header_dict in self.header_list:
            if header_dict['sensor_serial_number']:
                return header_dict['sensor_serial_number']
            
            
    def get_dataframe(self):
        """Converts the data to a Pandas DataFrame
        
        """
        
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
        
        df=df.replace('',np.nan)
    
        # convert strings to numerical values where possible
        for col in df.columns:
            if not col[0] in ['#','Date Time']:
                try:
                    df[col]=pd.to_numeric(df[col])
                except ValueError:
                    pass
        
        return df
            
            
# rdf functions
    
    def get_rdf(self,
                my_sensor_id=r'http:www.example.org/my_sensor',
                my_sensor_model='My sensor model',
                my_sensor_manufacturer='Onset',
                my_feature_of_interest_id='rhttp:www.example.org/my_feature_of_interest'
                ):
        """Returns a rdflib graph of the data
        
        """
        
        import rdflib
        from rdflib.namespace import RDF, RDFS
        SSN=rdflib.Namespace(r'http://www.w3.org/ns/ssn/')
        SOSA=rdflib.Namespace(r'http://www.w3.org/ns/sosa/')
        TIME=rdflib.Namespace(r'http://www.w3.org/2006/time#')
        BOO=rdflib.Namespace(r'http://www.purl.org/berg/ontology/objects#')
        QUANTITYKIND=rdflib.Namespace(r'http://qudt.org/2.1/vocab/quantitykind/')
        UNIT=rdflib.Namespace(r'http://qudt.org/vocab/unit/')
        QUDT=rdflib.Namespace(r'http://qudt.org/schema/qudt/')
        
        # Internal functions
        
        def add_rdf_sensor(g,my_sensor_id):
            qu = \
            """
                INSERT DATA
                {
                    <%s> a sosa:Sensor ;
                        a ssn:System ;
                        a sosa:FeatureOfInterest ;
                        a boo:PhysicalObject .
                }
            """ % (rdflib.URIRef(my_sensor_id))
            g.update(qu)
            
            
        def add_rdf_feature_of_interest(g,my_FoI_id):
            qu = \
            """
                INSERT DATA
                {
                    <%s> a sosa:FeatureOfInterest ;
                        a boo:PhysicalObject .
                }
            """ % (rdflib.URIRef(my_FoI_id))
            g.update(qu)
            
            
        def get_rdf_property_labels(header_list):
            return ['Serial number','Model','Manufacturer'] + [x['title'] 
                    for x in header_list 
                    if not x['title'] in ['#','Date Time','Time']]
        
        
        def get_feature_of_interest_uri(g,property_label,header_list,
                                        my_sensor_id,my_feature_of_interest_id):
            for header_dict in header_list:
                if header_dict['title']==property_label:
                    if header_dict['sensor_serial_number']:
                        return rdflib.URIRef(my_feature_of_interest_id)
            return rdflib.URIRef(my_sensor_id) 
        
        
        def get_qudt_quantity_kind(property_label):
            if property_label=='Temp': return QUANTITYKIND.Temperature
            if property_label=='RH': return QUANTITYKIND.RelativeHumidity
            if property_label=='Intensity': return QUANTITYKIND.Illuminance
            return None
        
        
        def get_rdf_property_uri(g,p_label):
            
            q = \
            """
                SELECT ?s
                WHERE
                {
                    ?s a ssn:Property ;
                        a sosa:ObservableProperty ;
                        rdfs:label "%s" .
                }
            """ % str(p_label)
            #print(q)
            qres = g.query(q)
            #print (list(qres))
            try:
                return list(qres)[0][0]
            except IndexError:
                raise KeyError()
                
                
        def add_rdf_property(g,p_label,FoI_uri,pk_uri=None):
            
            b=rdflib.BNode()
            
            g.add( (b, RDF.type, SSN.Property) )
            g.add( (b, RDF.type, SOSA.ObservableProperty) )
            g.add( (b, RDFS.label, rdflib.Literal(p_label)) )
            g.add( (b, SSN.isPropertyOf, FoI_uri) )
            g.add( (FoI_uri, SSN.hasProperty, b) )
            
            if pk_uri:
                g.add( (b, QUDT.hasQuantityKind, pk_uri) )
                g.add( (pk_uri, QUDT.isQuantityKindOf, b) )
                
                
        def add_observation(g,
                            ObservableProperty_uri=None,
                            FoI_uri=None,
                            Sensor_uri=None,       
                            simple_result_uri=None,
                            qudt_result=None,
                            result_time_instant=None):
            
            n=rdflib.BNode()
            
            g.add( (n, RDF.type, SOSA.Observation) )
            
            if ObservableProperty_uri:
                g.add( (n, SOSA.observedProperty, ObservableProperty_uri) )
                
            if FoI_uri:
                g.add( (n, SOSA.hasFeatureOfInterest, FoI_uri) )
                g.add( (FoI_uri, SOSA.isFeatureOfInterestOf, n) )
                
            if Sensor_uri:
                g.add( (Sensor_uri, SOSA.madeObservation, n) )
                g.add( (n, SOSA.madeBySensor, Sensor_uri) )
                
            if simple_result_uri: 
                g.add( (n, SOSA.hasSimpleResult, simple_result_uri) )
                
            if qudt_result:
                value=qudt_result[0]
                units_uri=qudt_result[1]
                b=rdflib.BNode()
                g.add( (n, SOSA.hasResult, b) )
                g.add( (b, RDF.type, QUDT.QuantityValue) )
                g.add( (b, QUDT.numericValue, value) )
                g.add( (b, QUDT.unit, units_uri) )
            
            if result_time_instant:
                b=rdflib.BNode()
                g.add( (n, SOSA.resultTime, b) )
                g.add( (b, RDF.type, TIME.Instant) )
                g.add( (b, TIME.inXSDDateTimeStamp, result_time_instant) )
                
                
        def get_units_uri(unit_str):
            if unit_str in ['°C','Â°F']: return UNIT.DEG_F
            if unit_str in ['°C','Â°C']: return UNIT.DEG_C
            if unit_str=='%': return UNIT.PERCENT
            if unit_str=='Lux': return UNIT.LUX
            return rdflib.Literal(unit_str)
            
        
        # Start
        
        g=rdflib.Graph()
        
        g.bind('ssn', SSN)
        g.bind('sosa', SOSA)
        g.bind('time', TIME)
        g.bind('boo',BOO)
        g.bind('quantitykind',QUANTITYKIND)
        g.bind('unit',UNIT)
        g.bind('qudt',QUDT)
    
        df=self.get_dataframe()
        
        add_rdf_sensor(g,my_sensor_id)
        
        add_rdf_feature_of_interest(g,my_feature_of_interest_id)
        
        property_labels=get_rdf_property_labels(self.header_list)
        #print(property_labels)
        
        for p_label in property_labels:
            #print(p_label)
            
            FoI_uri=get_feature_of_interest_uri(g,
                                                p_label,
                                                self.header_list,
                                                my_sensor_id,
                                                my_feature_of_interest_id)
            pk_uri=get_qudt_quantity_kind(p_label)
            
            try:
                get_rdf_property_uri(g,p_label)
            except KeyError:
                add_rdf_property(g,p_label,FoI_uri,pk_uri)
        
        sn=self.get_sensor_serial_number()
        
        # serial number
        add_observation(g,
                ObservableProperty_uri=get_rdf_property_uri(g,"Serial number"),
                FoI_uri=rdflib.URIRef(my_sensor_id),
                simple_result_uri=rdflib.Literal(sn)
               )
        
        # model
        add_observation(g,
                ObservableProperty_uri=get_rdf_property_uri(g,"Model"),
                FoI_uri=rdflib.URIRef(my_sensor_id),
                simple_result_uri=rdflib.Literal(my_sensor_model)
               )

        # manufacturer
        add_observation(g,
                ObservableProperty_uri=get_rdf_property_uri(g,"Manufacturer"),
                FoI_uri=rdflib.URIRef(my_sensor_id),
                simple_result_uri=rdflib.Literal(my_sensor_manufacturer)
               )
        
        for col in df.columns:
            if not col[0] in ['#','Date Time','Time']:
                
                title,timezone_str,units,logger_serial_number,sensor_serial_number=col
                #print(title)
                
                p_uri=get_rdf_property_uri(g,title)
                
                if not pd.isna(sensor_serial_number):
                    Sensor_uri=rdflib.URIRef(my_sensor_id)
                    FoI_uri=rdflib.URIRef(my_feature_of_interest_id)
                else:
                    Sensor_uri=None
                    FoI_uri=rdflib.URIRef(my_sensor_id)
                
                s=df[col]
                s=s.dropna()
                
                for i,v in s.iteritems():
                    
                    if not pd.isna(units):
                        
                        units_uri=get_units_uri(units)
                        
                        add_observation(g,
                                        ObservableProperty_uri=p_uri,
                                        FoI_uri=FoI_uri,
                                        Sensor_uri=Sensor_uri,
                                        qudt_result=(rdflib.Literal(v),units_uri),
                                        result_time_instant=rdflib.Literal(i.isoformat(),
                                                                           datatype=rdflib.XSD.dateTimeStamp)
                                       )
                        
                    else:
                    
                        add_observation(g,
                                        ObservableProperty_uri=p_uri,
                                        FoI_uri=FoI_uri,
                                        Sensor_uri=Sensor_uri,
                                        simple_result_uri=rdflib.Literal(v),
                                        result_time_instant=rdflib.Literal(i.isoformat(),
                                                                           datatype=rdflib.XSD.dateTimeStamp)
                                       )        
                
        return g
    
    


    
if __name__=="__main__":
    
    h=HoboReader()
    h.read_csv(r'..\tests\sample_hobo_pendant_data.csv')
    print(h.header_list)
    print(h.datetimes[:5])
    print(h.get_dataframe())
    
    g=h.get_rdf(
            my_sensor_id=r'http://www.example.org/MyHobo',
            my_sensor_model='Hobo Pendant',
            my_sensor_manufacturer='Onset',
            my_feature_of_interest_id=r'http://www.example.org/MyLivingRoom')
    print(g.serialize(format='turtle').decode())
    