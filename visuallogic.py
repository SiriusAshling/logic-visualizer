from gimpfu import *
import re
import os

def transform(x, y, img):  # transform ingame coordinates to picture coordinates
  factor = img.width / 4390.0
  x = x + 2015
  y = y + 3536
  x = x * factor
  y = y * -factor  # the y axis is inverted between the game and gimp
  return x, y

pickupDict = {
  "GladesTown.AcornQI": (-366, -4185),
  "InnerWellspring.WaterEscape": (-1159, -3635),
  "WoodsEntry.DollQI": (469, -4180),
  "GladesTown.HoleHutEC": (-230, -4095),
  "GladesTown.HoleHutEX": (-230, -4095),
  "GladesTown.BraveMokiHutEX": (-329, -4123),
  "GladesTown.MotayHutEX": (-394, -4136),
  "GladesTown.KeyMokiHutEX": (-387, -4161),
  "GladesTown.LupoSoupEX": (-209, -4163),
  "UpperReach.SpringSeed": (-33, -3926),
  "LupoShop.HCMapIcon": (-209, -4162),
  "LupoShop.ECMapIcon": (-209, -4162),
  "LupoShop.ShardMapIcon": (-209, -4162),
}

def run():
  if not os.path.exists("C:/moon/areas.wotw"):
    print("Could not find areas.wotw at C:/moon. Put it there please oriHug")
    return
  if not os.path.exists("C:/moon/loc_data.csv"):
    print("Could not find loc_data at C:/moon. Put it there please oriHug")
    return
  
  pdb.gimp_context_set_defaults()
  pdb.gimp_context_set_brush_spacing(0.01)
  pdb.gimp_context_set_brush_hardness(0.75)
  
  img = gimp.image_list()[0]
  print "using image: %s" % (pdb.gimp_image_get_filename(img))
  
  pdb.plug_in_autocrop(img, img.layers[-1])
  parent = pdb.gimp_layer_group_new(img)
  anchorconns = pdb.gimp_layer_new(img, img.width, img.height, 1, "anchor-anchor", 100, 28)
  pickupconns = pdb.gimp_layer_new(img, img.width, img.height, 1, "anchor-pickup", 100, 28)
  pdb.gimp_image_insert_layer(img, parent, None, 0)
  pdb.gimp_image_insert_layer(img, anchorconns, parent, 0)
  pdb.gimp_image_insert_layer(img, pickupconns, parent, 0)
  
  logic = open("C:/moon/areas.wotw")
  
  x = None
  for line in logic:
    line = line.split("#")[0]  # remove comments which can have all kinds of surprising characters
    if re.search("anchor .+ at -?[0-9]+, -?[0-9]+", line):
      x, y = re.findall("-?[0-9]+", line)  # set current origin location
      x, y = int(x), int(y)
      x, y = transform(x, y, img)
      pdb.gimp_displays_flush()  # who cares about speed this is too satisfying
      continue
    if re.search("anchor .+:", line):  # on anchors without coordinates, skip through to the next anchor
      x = None
    if x == None: continue
    pickup = re.search("pickup .+:|quest .+:", line)
    if pickup:
      if pickup.group()[0] == "p": name = pickup.group()[7:-1]
      if pickup.group()[0] == "q": name = pickup.group()[6:-1]  # Yes yes very graceful
      if name in pickupDict:
        targetx, targety = pickupDict[name]  # See if this pickup has different map coordinates than loc_data coordinates
      else:
        pickups = open("C:/moon/loc_data.csv")
        for check in pickups:
          if name in check:
            targetx, targety = check.rsplit(", ")[-2:]  # set target location
            break
      if targetx == None:
        print "Warn: could not find %s" % (name)
        continue
      targetx, targety = int(targetx), int(targety)
      targetx, targety = transform(targetx, targety, img)
      pdb.gimp_context_set_brush_size(4)
      pdb.gimp_context_set_foreground("#0B610B")
      pdb.gimp_paintbrush_default(pickupconns, 4, [x, y, targetx, targety])
      continue
    conn = re.search("conn .+:", line)
    if conn:
      name = conn.group()[5:-1]
      areas = open("C:/moon/areas.wotw")
      targetx = None
      for check in areas:
        if re.search("anchor %s at -?[0-9]+, -?[0-9]+" % (name), check):
          targetx, targety = re.findall("-?[0-9]+", check)  # set target location
          targetx, targety = int(targetx), int(targety)
          targetx, targety = transform(targetx, targety, img)
          break
      if targetx == None:
        print "Warn: could not find %s" % (name)
        continue
      halfx, halfy = (targetx + x) / 2, (targety + y) / 2  # dot the line after the halfway mark to represent one-way connections
      pdb.gimp_context_set_brush_size(5)
      pdb.gimp_context_set_foreground("#B43104")
      pdb.gimp_paintbrush_default(anchorconns, 4, [x, y, halfx, halfy])
      pdb.gimp_context_set_brush_spacing(1.5)
      pdb.gimp_paintbrush_default(anchorconns, 4, [halfx, halfy, targetx, targety])
      pdb.gimp_context_set_brush_spacing(0.01)