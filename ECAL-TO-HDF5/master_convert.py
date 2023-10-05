from convert_depth_camera import convert as convert_depth
from convert_colour_camera import convert as convert_color
from convert_infra_camera import convert as convert_infra

from convert_radar import convert as convert_radar

def main(): 
    expNum = 5
    convert_depth(expNum)
    convert_color(expNum,filename=None)
    convert_infra(expNum)
    convert_radar(expNum)


 
if __name__ == "__main__":
    main()