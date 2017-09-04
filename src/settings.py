import sys

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def initSettings():

    if sys.version_info[0] < 3:
        import ConfigParser
        Config = ConfigParser.ConfigParser()
    else:
        import configparser
        Config = configparser.ConfigParser()

    # read the config file
    Config.read("settings.txt")

    # prepare global settings variable
    global use_globus
    global gpd_enabled
    global scale
    global window_width
    global window_height

    # load the variables from the settings file
    use_globus = Config.getboolean("General", "show_globe")
    gpd_enabled = Config.getboolean("gpd", "enabled")
    scale = Config.getfloat("gpd", "font_scale")
    window_width = Config.getint("gpd", "window_width")
    window_height = Config.getint("gpd", "window_height")
