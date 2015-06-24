# -*- coding: utf-8 -*-
#!/usr/bin/python
import inspect
import sys, getopt, os
from osgeo import gdal
import time  

def main(argv):
  inputfile = None
  outputfile = None
  layer = None
  try:
    opts, args = getopt.getopt(argv,"hi:o:l:",["ifile=","ofile=","layer="])
  except getopt.GetoptError:
    printhelp()
  if not opts:
    printhelp()
  for opt, arg in opts:
    if opt == '-h':
      printhelp()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg
    elif opt in ("-l", "--layer"):
      try:
        layer = int(arg)
      except:
        print "Some error while parsing layer_number"
        printhelp()


  
  print "----- Info: ------------------"
  print '\nInput file is ', inputfile
  print 'Output file is ', outputfile
  print 'Layer is ', layer

  hdf = gdal.Open(inputfile)
  if layer and layer != 0:
    print "Layer info:"
    print hdf.GetSubDatasets()[layer]
    print "\n"

  names = get_layer_names(hdf)
  sds = make_sds_list(names)

  print_layer_list(names, sds)
  print "\n"

  if layer is None:
    layer = input("Input layer number to continue, press 0 for all layers...\n")
  if outputfile is None:
    outputfile = inputfile
  if layer == 0:
    outputfile = names
  
  create_layer_images(layer, sds, outputfile)
     
def printhelp():
  print 'test.py -i <inputfile> -o <outputfile> -l <layer_num>'
  sys.exit()

def get_layer_names(hdf):
  sdslist = hdf.GetSubDatasets()
  names = [] 
  for s in sdslist:
    names.append(s[0])
  return names

def make_sds_list(names):
  sds = []
  for n in names:
    sds.append(gdal.Open(n))
  return sds

def print_layer_list(names, sds):
  print "----- Accessible layers: -----"
  out_names = [s.rsplit(':', 1)[1] for s in names]
  for ind, name in enumerate(out_names):
    geotrans  = gdal.GCPsToGeoTransform(sds[ind].GetGCPs())
    if geotrans:
      print "%s. %s" %(ind, name)

def copy_and_transform(file_name, sds):
  format = "GTiff"
  print "Format: GTiff"
  driver = gdal.GetDriverByName( format )
  file_name += '.tif'
  print "File name: %s" %file_name
  driver = gdal.GetDriverByName( format )
  
  dst_ds = driver.CreateCopy( file_name, sds, 1 )

  print "Status: Created" 
  
  geotrans  = gdal.GCPsToGeoTransform(sds.GetGCPs())
  print "Geotrans: ", geotrans
  
  if geotrans:
    # geotrans = (20.776085394125101, 0.061360126841990, 0, 65.899963721633995, 0, -0.061360126841990)
    dst_ds.SetGeoTransform( geotrans ) 
    print "Status: Transformed"

def create_layer_images(layer, sds, file_name):
  print "----- Creating directory: --------"
  directory = time.strftime("%d%m%Y_%H%M%S")
  if not os.path.exists(directory):
    os.makedirs(directory)
    print "Directory ", directory, " created"
  print "----- Creating image: ------------"
  if layer != 0:
    print "Layer: %s" %layer
    file_name = directory+"/"+file_name
    copy_and_transform(file_name, sds[layer])
  else:
    print "Layer: all"
    out_names = [s.rsplit(':', 1)[1] for s in file_name]
    for ind, name in enumerate(out_names):
      name = directory+"/"+name
      copy_and_transform(name, sds[ind]) 
  print "----- Successfully made ----------\n"

if __name__ == "__main__":
   main(sys.argv[1:])


# image storing

  # for ind, name in enumerate(out_names):
  #     geotrans  = gdal.GCPsToGeoTransform(sds[ind].GetGCPs())
  #     if geotrans:
  #         dst_name = name + '.tif'
  #         format = "GTiff"
  #         driver = gdal.GetDriverByName( format )
  #         dst_ds = driver.CreateCopy( dst_name, sds[ind], 1 )
  #         dst_ds.SetGeoTransform( geotrans )