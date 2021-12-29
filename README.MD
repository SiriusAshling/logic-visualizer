Visualize a given areas.wotw logic file as lines on top of a world map.

Requires [GIMP](https://www.gimp.org/)

Instructions:
- put the areas.wotw and loc_data.csv that you want to visualize into this folder
- open "rando map.png" in GIMP
- open GIMPs python console (Filters -> Python-Fu -> Console)
- enter: `import sys;sys.path=sys.path+["<path to folder with this file>"];import visuallogic;visuallogic.run()`
