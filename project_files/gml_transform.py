import os, sys
import getopt
import xml.etree.ElementTree as ET

# ----------------------------------------------------------------------------------------------------------------------

global usage
usage = \
"""==============================================================
| Usage:                                                     |
--------------------------------------------------------------
| python gml_transform.py -i <inputfile> [-o <outputpath>]   |
=============================================================="""
   
 
def parameters(argv):
    """Processing command line input arguments."""
    
    inputfile = ''
    outputpath = ''

    try:
        opts, _ = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print usage
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h","--help"):
            print usage
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputpath = arg
            
    if outputpath == '':
        outputpath = os.path.split(inputfile)[0]
            
    return inputfile, outputpath

# ----------------------------------------------------------------------------------------------------------------------


def get_gml_src_proj(path_gml):
    """Reads the source projection system."""
    f = open(path_gml)
    text = f.read()
    text = text.split('xmlns:gml=')[-1]
    gml = text.split('"')[1]
    
    tree = ET.parse(path_gml)
    
    # GET EOP-URL
    root = tree.getroot()
    eop_url = root.tag.split('}')[0].strip('{')
    
    node = tree.find('.//{'+gml+'}Envelope')
    try:
        srs_string = node.get('srsName')
        epsg_no = srs_string.split(':')[-1]
        epsg_code = 'EPSG:{}'.format(epsg_no)
    except:
        print('Warning, gml has no SRS information.')
        epsg_code = None
    
    return epsg_code

# ----------------------------------------------------------------------------------------------------------------------


def get_cloud_shp(path_in_gml, path_out):
    """Transform the gml cloud mask to a shape file."""
    
    if not os.path.isdir(path_out):
        os.mkdir(path_out)
    
    name = os.path.split(path_in_gml)[-1]
    if name.endswith('gml'):
        path_out_shp = os.path.join(path_out,name.replace('.gml','.shp'))
                
        src_srs = get_gml_src_proj(path_in_gml)
        trg_srs = 'EPSG:4326'
        
        if src_srs is None:
            cmd = 'ogr2ogr -t_srs {} -f "ESRI Shapefile" {} {}'.format(trg_srs, path_out_shp, path_in_gml)
        else:
            cmd = 'ogr2ogr -s_srs {} -t_srs {} -f "ESRI Shapefile" {} {}'.format(src_srs, trg_srs, path_out_shp, path_in_gml)
            
        os.system(cmd)     
    
    print 'GML [{}] successfully converted to SHP [{}]'.format(path_in_gml, path_out_shp)
    
    return path_out_shp

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    path_in, path_out = parameters(sys.argv[1:])
    path_out_shp = get_cloud_shp(path_in, path_out)