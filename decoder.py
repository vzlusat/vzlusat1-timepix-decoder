#!/usr/bin/python

#{ def installAndImport(package):
def installAndImport(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)
#}

#{ IMPORTS

installAndImport('matplotlib')
installAndImport('Pmw')
installAndImport('ephem')

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.patches as patches # for plotting rectangles in the custom histogram
from matplotlib.figure import Figure

# to fix the colorbar's position
from mpl_toolkits.axes_grid1 import make_axes_locatable

import os
import sys
import numpy
import datetime
import re
import time

# my custom functions
from src.Image import Image
from src.HouseKeeping import HouseKeeping
from src.loadImage import loadImage
from src.saveImage import saveImage
from src.saveHouseKeeping import saveHouseKeeping
from src.loadHouseKeeping import loadHouseKeeping
from src.parseInputFile import parseInputFile

# imports that depend on the python version
if sys.version_info[0] < 3:
    import Tkinter as Tk
    import tkFileDialog
    import ttk
else:
    import tkinter as Tk
    import tkinter.filedialog
    from tkinter import ttk
#}

# for plotting the globe
from mpl_toolkits.basemap import Basemap

# core methods

#{ def reloadData(index): reloads and shows metadata and image for a particular index in the listbox
def reloadData(index, manual):

    list_files = loadFiles()
    global file_names
    file_name = file_names[index]

    global loaded_image

    if file_name[-5] == 'h':
        housekeeping = loadHouseKeeping(file_names[index])
        loaded_image = housekeeping
        showHouseKeeping(housekeeping)
    else:
        image = loadImage(file_names[index])

        # if the file could not been opened, return
        if image == 0:
            print("file_could_not_be_opened")
            return

        loaded_image = image

        showImage(image, manual)
#}

#{ def loadFiles(): inspects "images_bin" folders and prepares the content for the listbox
def loadFiles():

    # updated the filename list
    global file_names
    file_names = os.listdir("images_bin")

    file_names2 = sorted(file_names, key=numericalSort)
    file_names = []

    list_files = []

    # create the list of files for the listbox
    for file in file_names2:

        if file[-5] == 'h':

            housekeeeping = loadHouseKeeping(file)

            if housekeeeping != 0:

                if hide_housekeeping_var.get():
                    pass
                elif (show_favorite_var.get() and not housekeeeping.favorite):
                    pass
                elif ((not show_hidden_var.get()) and (housekeeeping.hidden)):
                    pass
                else:
                    file_names.append(file)
                    list_files.append(str(housekeeeping.images_taken)+"_"+str(housekeeeping.boot_count)+"_"+str(housekeeeping.time_since_boot)+"s_hk")
            else:
                print("could not open file "+file)

        else:

            image = loadImage(file)

            if image != 0:

                if (hide_without_data_var.get() and (not image.got_data)):
                    pass
                elif (show_only_without_data_var.get() and image.got_data):
                    pass
                elif (show_favorite_var.get() and not image.favorite):
                    pass
                elif ((not show_hidden_var.get()) and (image.hidden)):
                    pass
                else:
                    file_names.append(file)
                    list_files.append(str(image.id)+"_"+str(image.type))
            else:
                print("could not open file "+file)

    return list_files
#}

#{ def showHouseKeeping(housekeeping): resets and shows housekeeping data
def showHouseKeeping(housekeeping):

    my_figure.clf()
    subplot1 = my_figure.add_subplot(111)
    subplot1.text(0.5, 0.5, 'No data', horizontalalignment='center',verticalalignment='center', transform = subplot1.transAxes)
    subplot1.axes.get_xaxis().set_visible(False)
    subplot1.axes.get_yaxis().set_visible(False)
    subplot1.patch.set_visible(False)
    subplot1.axis('off')

    figure_canvas.show()

    # clear the text
    for i in range(0, len(Image.metadata_labels)):
        text_labels_var[i].set("")

    for i in range(0, len(Image.metadata_labels)):
        metadatas_var[i].set("")

    # fill the labels
    for i in range(0, len(HouseKeeping.housekeeping_labels)):
        text_labels_var[i].set(HouseKeeping.housekeeping_labels[i])

    metadatas_var[0].set(str(housekeeping.boot_count))
    metadatas_var[1].set(str(housekeeping.images_taken))
    metadatas_var[2].set(str(housekeeping.temperature)+" C")

    if housekeeping.fram_status == 1:
        fram_status = "OK"
    else:
        fram_status = "ERROR"

    metadatas_var[3].set(str(fram_status))

    if housekeeping.medipix_status == 1:
        medipix_status = "OK"
    else:
        medipix_status = "ERROR"

    metadatas_var[4].set(str(medipix_status))
    metadatas_var[5].set(str(housekeeping.time_since_boot)+" s")

    metadatas_var[6].set(str(housekeeping.TIR_max))
    metadatas_var[7].set(str(housekeeping.TIR_min))
    metadatas_var[8].set(str(housekeeping.IR_max))
    metadatas_var[9].set(str(housekeeping.IR_min))
    metadatas_var[10].set(str(housekeeping.UV1_max))
    metadatas_var[11].set(str(housekeeping.UV1_min))
    metadatas_var[12].set(str(housekeeping.UV2_max))
    metadatas_var[13].set(str(housekeeping.UV2_min))
    metadatas_var[14].set(str(housekeeping.temp_max))
    metadatas_var[15].set(str(housekeeping.temp_min))
    human_readible_time = datetime.datetime.utcfromtimestamp(housekeeping.time)
    metadatas_var[16].set(human_readible_time)

    marked_as_hidden_var.set(housekeeping.hidden)
    marked_as_favorite_var.set(housekeeping.favorite)

    if show_globus_var.get():
        latitude, longitude, tle_date = getLatLong(housekeeping.time)
        globus_label_var.set("{}, {}\nTLE: {}".format(latitude, longitude, tle_date))
        redrawMap(latitude, longitude, human_readible_time)
    else:
        clearMap()
#}

#{ def showImage(image): resets and shows the image
def showImage(image, manual):

    marked_as_hidden_var.set(image.hidden)
    marked_as_favorite_var.set(image.favorite)

    if manual == 0 and image.got_data == 0:
        return

    # Clear the previous metadata
    for i in range(0, 21):
        metadatas_var[i].set("")

    metadatas_var[0].set(str(image.id))

    if image.type == 1:
        img_type = "RAW"
    elif image.type == 2:
        img_type = "Binning 8"
    elif image.type == 4:
        img_type = "Binning 16"
    elif image.type == 8:
        img_type = "Binning 32"
    elif image.type == 16:
        img_type = "Sums"
    elif image.type == 32:
        img_type = "Energy histogram"

    metadatas_var[1].set(img_type)

    #{ METADATA
    if image.got_metadata == 0:

        # try to load metadata from other image
        possible_names =  [1, 2, 4, 8, 16, 32]
        for possible_name in possible_names:

            temp_image = loadImage(image.id, possible_name)

            # skip if there are no metadata
            if temp_image ==  0:
                continue;

            # if we got metadata, use them
            if temp_image.got_metadata == 1:

                print("Metadata are missing in {}_{}, replacing them from {}_{}".format(image.id, image.type, temp_image.id, temp_image.type))
                image.mode = temp_image.mode
                image.threshold = temp_image.threshold
                image.bias = temp_image.bias
                image.exposure = temp_image.exposure
                image.filtering = temp_image.filtering
                image.filtered_pixels = temp_image.filtered_pixels
                image.original_pixels = temp_image.original_pixels
                image.min_original = temp_image.min_original
                image.max_original = temp_image.max_original
                image.min_filtered = temp_image.min_filtered
                image.max_filtered = temp_image.max_filtered
                image.temperature = temp_image.temperature
                image.temp_limit = temp_image.temp_limit
                image.pxl_limit = temp_image.pxl_limit
                image.uv1_thr = temp_image.uv1_thr
                image.chunk_id = -1;
                image.attitude = temp_image.attitude
                image.position = temp_image.position
                image.time = temp_image.time
                image.got_metadata = 1
                saveImage(image)
                break

    if image.got_metadata == 1:

        if image.mode == 0:
            mode = "Medipix (Counting)"
        else:
            mode = "Timepix (Energy)"

        metadatas_var[2].set(mode)

        metadatas_var[3].set(image.threshold)
        metadatas_var[4].set(image.bias)

        exposure = image.exposure

        if image.exposure <= 60000:
            exposure = image.exposure*0.001
        else:
            exposure = 60 + image.exposure%60000

        metadatas_var[5].set("{0:3.3f} s".format(exposure))

        if image.filtering == 0:
            filtering = "OFF"
        else:
            filtering = "ON"

        metadatas_var[6].set(filtering)
        metadatas_var[7].set(image.filtered_pixels)
        metadatas_var[8].set(image.original_pixels)
        metadatas_var[9].set(image.min_original)
        metadatas_var[10].set(image.max_original)
        metadatas_var[11].set(image.min_filtered)
        metadatas_var[12].set(image.max_filtered)
        metadatas_var[13].set(str(image.temperature)+" C")
        metadatas_var[14].set(str(image.temp_limit)+" C")
        metadatas_var[15].set(image.pxl_limit)
        metadatas_var[16].set(image.uv1_thr)

        attitude = ""
        for att in image.attitude:
            attitude += str(att)+" "

        metadatas_var[17].set(attitude)

        position = ""
        for pos in image.position:
            position += str(pos)+" "

        metadatas_var[18].set(position)

        human_readible_time = datetime.datetime.utcfromtimestamp(image.time)
        metadatas_var[19].set(human_readible_time)

        if show_globus_var.get():
            latitude, longitude, tle_date = getLatLong(image.time)
            globus_label_var.set("{}, {}\nTLE: {}".format(latitude, longitude, tle_date))
            redrawMap(latitude, longitude, human_readible_time)
        else:
            clearMap()

        # only print chunk id if we actually got the metadata (-1 if it does not)
        if image.chunk_id >= 0:

            if image.type == 2:
                chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+15)
            elif image.type == 4:
                chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+3)
            elif image.type == 8:
                chunk_id = str(image.chunk_id)
            elif image.type == 16:
                chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+7)
            elif image.type == 32:
                chunk_id = str(image.chunk_id)
            elif image.type == 1:
                chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+int(numpy.floor(image.filtered_pixels/20)))

            metadatas_var[20].set(chunk_id)

    for i in range(0, len(Image.metadata_labels)):
        text_labels_var[i].set(Image.metadata_labels[i])

    #}

    #{ IMAGE
    if image.got_data == 1:

        if image.type >= 1 and image.type <= 8:

            # plot the image
            my_figure.clf()
            subplot1 = my_figure.add_subplot(111)

            subplot1.set_xlabel("Column [-]")
            subplot1.set_ylabel("Row [-]")

            if image.got_metadata == 1:
                subplot1.set_title(img_type+" n.{0}, {1} s exposure, ".format(image.id, exposure)+mode+" mode", fontsize=13, y=1.02)
            else:
                subplot1.set_title(img_type+" n.{0}, ??? s exposure, ".format(image.id)+"??? mode", fontsize=13, y=1.02)

            # show the image
            im = subplot1.imshow(image.data, interpolation='none', cmap=colormap_variable.get())

            # create the colormap bar and place it in the correct place
            divider = make_axes_locatable(my_figure.gca())
            cax = divider.append_axes("right", size="5%", pad=0.2)
            cbar = my_figure.colorbar(im, cax=cax)

            cbar.ax.get_yaxis().labelpad = 20
            if image.type == 1:
                if image.mode == 0:
                    cbar.ax.set_ylabel('[counts]', rotation=270)
                else:
                    cbar.ax.set_ylabel('[keV]', rotation=270)
            else:
                cbar.ax.set_ylabel('[active pixels in the bin]', rotation=270)

            my_figure.tight_layout(pad=1)
        #}

        #{ SUMS
        elif image.type == 16:

            my_figure.clf()
            a1 = my_figure.add_subplot(211)
            a2 = my_figure.add_subplot(212)

            x = numpy.linspace(1, 256, 256)

            a1.plot(x, image.data[0, :])
            a2.plot(x, image.data[1, :])
            a1.axis([1, 256, numpy.min(image.data[0, :]), numpy.max(image.data[0, :])])
            a2.axis([1, 256, numpy.min(image.data[1, :]), numpy.max(image.data[1, :])])

            if image.got_metadata == 1:
                a1.set_title("Row summs n.{0}, {1} s exposure ".format(image.id, exposure), fontsize=13, y=1.02)
            else:
                a1.set_title("Row summs n.{0}, ??? s exposure ".format(image.id), fontsize=13, y=1.02)
            a1.set_xlabel("Row [-]")
            a1.set_ylabel("Active pixel count [-]")

            if image.got_metadata == 1:
                a2.set_title("Column summs n.{0}, {1} s exposure ".format(image.id, exposure), fontsize=13, y=1.02)
            else:
                a2.set_title("Column summs n.{0}, ??? s exposure ".format(image.id), fontsize=13, y=1.02)
            a2.set_xlabel("Column [-]")
            a2.set_ylabel("Active pixel count [-]")

            my_figure.tight_layout(pad=2)
        #}

        #{ HISTOGRAM
        elif image.type == 32:

            my_figure.clf()
            subplot1 = my_figure.add_subplot(111)

            x = [2.9807, 4.2275, 6.4308, 10.3875, 16.6394, 24.7081, 33.7833, 43.3679, 53.2233, 63.2344, 73.3415, 83.5115, 93.7248, 103.9691, 114.2361, 124.5204, 134.8182]

            for i in range(0, 16):

                # rectangle('Position', [x(i), 0, x(i+1)-x(i), image.data(i)], 'FaceColor', [0 0.5 0.5], 'EdgeColor', 'b','LineWidth',1);
                subplot1.add_patch(
                    patches.Rectangle(
                        (x[i], 0),            # (x,y)
                        x[i+1]-x[i],          # width
                        image.data[0, i],                  # height
                    )
                )

            # subplot1.plot(x, image.data[0, :])

            subplot1.relim()
            subplot1.autoscale_view()

            if image.mode == 0:
                subplot1.set_xlabel("Particle counts [-]")
            else:
                subplot1.set_xlabel("Energy [keV]")

            subplot1.set_ylabel("Counts [-]")

            if image.got_metadata == 1:
                subplot1.set_title("Image histogram n.{0}, {1} s exposure, ".format(image.id, exposure)+mode+" mode", fontsize=13, y=1.02)
            else:
                subplot1.set_title("Image histogram n.{0}, ??? s exposure, ".format(image.id)+"??? mode", fontsize=13, y=1.02)

            my_figure.tight_layout(pad=1)
        #}

        if ((manual == 1 and autogenerate_png_view.get() == 1) or (manual == 0)) and image.got_data == 1:

            image_filename='images_png/{}_{}.png'.format(image.id, image.type)
            my_figure.savefig(image_filename, dpi=250, bbox_inches='tight')

    else: # we have not data to show

        my_figure.clf()
        subplot1 = my_figure.add_subplot(111)
        subplot1.text(0.5, 0.5, 'No data', horizontalalignment='center',verticalalignment='center', transform = subplot1.transAxes)
        subplot1.axes.get_xaxis().set_visible(False)
        subplot1.axes.get_yaxis().set_visible(False)
        subplot1.patch.set_visible(False)
        subplot1.axis('off')

    figure_canvas.show()
#}

# callback for marking hidden/favorite checkboxex

def markHiddenCallback():

    global loaded_image
    loaded_image.hidden = marked_as_hidden_var.get()

    if isinstance(loaded_image, Image):
        saveImage(loaded_image)
    elif isinstance(loaded_image, HouseKeeping):
        saveHouseKeeping(loaded_image)

    reloadList(int(listbox.curselection()[0]))

def markFavoriteCallback():

    global loaded_image
    loaded_image.favorite = marked_as_favorite_var.get()

    if isinstance(loaded_image, Image):
        saveImage(loaded_image)
    elif isinstance(loaded_image, HouseKeeping):
        saveHouseKeeping(loaded_image)

    reloadList(int(listbox.curselection()[0]))

def reloadList(new_idx=-1):

    list_files = loadFiles()

    if new_idx >=len(list_files)-1:
        new_idx=-1

    listbox.delete(0, Tk.END)

    for item in list_files:
        listbox.insert(Tk.END, item)

    # listbox.selection_clear()
    if new_idx == -1:
        listbox.after(10, lambda: listbox.selection_set("end"))
        listbox.after(500, lambda: listbox.see(Tk.END))
    else:
        listbox.after(10, lambda: listbox.selection_set(new_idx))
        listbox.after(500, lambda: listbox.see(new_idx))

    global file_names

    # autoselect the last item in the listbox after start
    if len(file_names) > 0:

        file_name = file_names[new_idx]

        global loaded_image
        if file_name[-5] == 'h':
            housekeeping = loadHouseKeeping(file_name)
            loaded_image = housekeeping
            showHouseKeeping(housekeeping)
        else:
            image = loadImage(file_name)
            if image != 0:

                loaded_image = image
                showImage(image, 1)

# AFTER LAUNCH

#{ create directories
if not os.path.exists("images_bin"):
    os.makedirs("images_bin")

if not os.path.exists("images_csv"):
    os.makedirs("images_csv")

if not os.path.exists("images_png"):
    os.makedirs("images_png")
#}

# Load TLE
from src.tle import *
parseTLE()

# create the root window
root = Tk.Tk()
root.resizable(width=1, height=1)
import platform
if platform.system() == "Windows":
    root.geometry('{}x{}'.format(1380, 800))
else:
    root.geometry('{}x{}'.format(1380, 740))
root.wm_title("VZLUSAT-1 X-Ray data decoder")

# create the main Frame in the root window
frame_main = Tk.Frame(root);
frame_main.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# create the figure
my_figure = Figure(facecolor='none', figsize=(8.2, 6.8), dpi=90)
my_figure.clf()

# create the status line
global v # global variable, so anyone can add text to the status line
v = Tk.StringVar()
status_line = Tk.Label(root, anchor=Tk.W, justify=Tk.LEFT, textvariable=v, height=1, bg="white", bd=2, highlightbackground="black")
status_line.pack(side=Tk.BOTTOM, fill=Tk.X, expand=0)

# create the left subframe for the list
frame_left = Tk.Frame(frame_main, bd=1);
frame_left.pack(side=Tk.LEFT, fill=Tk.Y, expand=0, padx=5, pady=5)

# create the right subframe for the figure and its control panel
frame_right = Tk.Frame(frame_main);
frame_right.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1, padx=5, pady=5)

# create the middle subframe for metadata
frame_middle = Tk.Frame(frame_right, bd=1);
frame_middle.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

frame_mid_top = Tk.Frame(frame_middle, bd=1);
if platform.system() == "Windows":
    frame_mid_top.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0, padx=10, pady=0)
else:
    frame_mid_top.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0, padx=10, pady=30)

frame_mid_bottom = Tk.Frame(frame_middle, bd=1);
frame_mid_bottom.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=0, padx=0, pady=0)

#{ create the labels for metadatas and their respective control variables
metadatas = []
metadatas_var = []
text_labels = []
text_labels_var = []
for i in range(0, len(Image.metadata_labels)): #Rows

    # labels on the left containing the "labels"
    text_labels_var.append(Tk.StringVar())
    label = Tk.Label(frame_mid_top, textvariable=text_labels_var[i])
    text_labels.append((label).grid(row=i, column=0, sticky=Tk.E))

    # lables on the right containing the "values"
    metadatas_var.append(Tk.StringVar())
    metadatas.append(Tk.Label(frame_mid_top, textvariable=metadatas_var[i]).grid(row=i, column=1, sticky=Tk.W))

    # filtration
    if i == 0:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Unique image id. The first orbital image is 385.")

    # Threshold
    if i == 3:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Raw value for threshold setpoint. The sensor was calibrated at 414.")

    # Bias
    if i == 4:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Bias is set in RAW value, which can be interpreted as: value 255 corresponds to 0 Volts, value 70 corresponds to 70 Volts.\n For values in between contact Tomas.")

    # filtration
    if i == 6:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Whether large blobs have been filtered out.")

    # nonzero pixel count
    if i == 7:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Number of non-zero pixels in the original image (before applying filtration)")

    # nonzero pixel count
    if i == 8:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Number of non-zero pixel after applying filtration (if applied)")

    # min pixel value
    if i == 9 or i == 11:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Minimal nozero value over all pixels.")

    # max pixel value
    if i == 10 or i == 12:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Maximum over all pixels is 255. That corresponds to ~150 keV in Energy mode.")

    # ChunkID
    if i == 20:
        temp_baloon = Pmw.Balloon(master=root);
        temp_baloon.bind(label, "Chunk ID contains the index (indeces) of S4P3 storage, where the data for this image are contained. If empty, the actual metadata for this image has not been downloaded yet.")

# add two checkboxes for marking images favorite and hidden
marked_as_hidden_var = Tk.IntVar()
metadatas.append(Tk.Checkbutton(frame_mid_top, text="", variable=marked_as_hidden_var, command=markHiddenCallback).grid(row=len(Image.metadata_labels)-2, column=1, sticky=Tk.W))

marked_as_favorite_var = Tk.IntVar()
metadatas.append(Tk.Checkbutton(frame_mid_top, text="", variable=marked_as_favorite_var, command=markFavoriteCallback).grid(row=len(Image.metadata_labels)-1, column=1, sticky=Tk.W))

housekeeping_values = []
housekeeping_labels = []
#}

# create the subframe for the figure
frame_figure = Tk.Frame(frame_right);
frame_figure.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=0, padx=5, pady=5)

# create the matplotlib's figure canvas
figure_canvas = FigureCanvasTkAgg(my_figure, master=frame_figure)
figure_canvas.show()
figure_canvas.get_tk_widget().pack(side=Tk.TOP)
figure_canvas._tkcanvas.pack(side=Tk.TOP)

# globus = Basemap(projection='ortho', lat_0=60.0, lon_0=30.0, resolution='l')
# map.drawcoastlines(linewidth=0.25)
# map.drawcountries(linewidth=0.25)
# map.fillcontinents(color='coral',lake_color='aqua')
# # draw the edge of the map projection region (the projection limb)
# map.drawmapboundary(fill_color='aqua')
# # draw lat/lon grid lines every 30 degrees.
# map.drawmeridians(numpy.arange(0,360,30))
# map.drawparallels(numpy.arange(-90,90,30))

globus_label_var = Tk.StringVar()
globus_label = Tk.Label(frame_mid_bottom, anchor=Tk.S, justify=Tk.CENTER,  textvariable=globus_label_var)
globus_label.pack(side=Tk.BOTTOM)

my_figure2 = Figure(facecolor='none', figsize=(2.0, 2.0), dpi=90)

# create the canvas for the globus
globus_canvas = FigureCanvasTkAgg(my_figure2, master=frame_mid_bottom)
globus_canvas.get_tk_widget().pack(side=Tk.BOTTOM, fill=Tk.BOTH, anchor=Tk.S)
globus_canvas._tkcanvas.pack(side=Tk.BOTTOM, fill=Tk.BOTH, anchor=Tk.S)

def clearMap():
    my_figure2.clf()
    subplot2 = my_figure2.add_subplot(111)
    subplot2.axes.get_xaxis().set_visible(False)
    subplot2.axes.get_yaxis().set_visible(False)
    subplot2.patch.set_visible(False)
    subplot2.axis("off")
    globus_canvas.show()

def redrawMap(lat, lon, timestamp):

    my_figure2.clf()
    subplot2 = my_figure2.add_subplot(111)

    globus = Basemap(
        projection='ortho',
        lat_0=lat,
        lon_0=lon,
        ax=subplot2
    )

    x, y = globus(lon, lat)
    globus.scatter(x, y, 80, marker='o', color='k', zorder=10)

    # draw coastlines, country boundaries, fill continents.
    globus.drawcoastlines(linewidth=0.25)
    globus.drawcountries(linewidth=0.25)
    globus.fillcontinents(color='coral', lake_color='aqua')
    # draw the edge of the globus projection region (the projection limb)
    globus.drawmapboundary(fill_color='aqua')
    # draw lat/lon grid lines every 30 degrees.
    globus.drawmeridians(numpy.arange(0,360,30))
    globus.drawparallels(numpy.arange(-90,90,30))
    globus.nightshade(timestamp)

    globus_canvas.show()

# create the toolbar for the figure
frame_toolbar = Tk.Frame(frame_figure);
frame_toolbar.pack(side=Tk.BOTTOM, fill=Tk.Y, expand=1)

def reloadCurrentImage(evt=0):

    global loaded_image_idx
    listbox.selection_set(loaded_image_idx)
    reloadData(loaded_image_idx, 1)

# create combox for selecting the colormap
colormap_variable = Tk.StringVar()
colormap_variable.set("bone_r")
colormap_combobox = ttk.Combobox(frame_toolbar, textvariable=colormap_variable)

if os.path.isfile("colormaps.txt"):
    with open("colormaps.txt") as colormap_file:
        colormap_combobox['values'] = [line.rstrip() for line in colormap_file.readlines()]
else:
    colormap_combobox['values'] = ('bone_r', 'bone', 'hot', 'jet')

colormap_combobox.current(0)
colormap_combobox.bind("<<ComboboxSelected>>", reloadCurrentImage)
colormap_combobox.pack(side=Tk.TOP, expand=1)

toolbar = NavigationToolbar2TkAgg(figure_canvas, frame_toolbar)
toolbar.pack(side=Tk.LEFT)
toolbar.update()

# create the one and only subplot in the figure
subplot1 = my_figure.add_subplot(111)
subplot1.axes.get_xaxis().set_visible(False)
subplot1.axes.get_yaxis().set_visible(False)
subplot1.patch.set_visible(False)
subplot1.axis('off')
figure_canvas.show()

# initialize Pmw (creates on-hover hints)
Pmw.initialise(root)

# we this sort function for sorting out filenames
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

# colormap is for now defined here
# TODO: make that as a selectable option in the gui
# colormap = "bone_r"
# colormap = "gnuplot"

# user can switch off generating pngs
autogenerate_png_view = Tk.IntVar()
autogenerate_png_load = Tk.IntVar()
autogenerate_csv_load = Tk.IntVar()

# user can switch on/off showing of hidden and favorite images
show_hidden_var = Tk.IntVar()
show_globus_var = Tk.IntVar()
show_favorite_var = Tk.IntVar()
hide_without_data_var = Tk.IntVar()
show_only_without_data_var = Tk.IntVar()
hide_housekeeping_var = Tk.IntVar()

# user can mark image as favorite or hidden
image_is_hidden = Tk.IntVar()

# preload and sort file names from "images_bin" directories
global file_names
list_files = loadFiles()

frame_list = Tk.Frame(frame_left);
frame_list.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

frame_list2 = Tk.Frame(frame_list);
frame_list2.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=1)

# is used to trigger of detecting key presses when file dialog is opened
global listbox_focus
listbox_focus = 0

# global loaded_image
global loaded_image
global loaded_image_idx
loaded_image_idx = 0
loaded_image = []

#{ LISTBOX (+SCROLLBAR) and its CALLBACK

#{ def onSelect(evt): callback function for showing the image after clicking the listbox
def onSelect(evt):

    global file_names
    global loaded_image_idx

    w = evt.widget

    if len(w.curselection()) == 0:
        return

    # extract the index of the selected item
    index = int(w.curselection()[0])

    loaded_image_idx = index

    reloadData(index, 1)
#}

scrollbar = Tk.Scrollbar(master=frame_list2, orient=Tk.VERTICAL)
listbox = Tk.Listbox(master=frame_list2, yscrollcommand=scrollbar.set, selectmode=Tk.SINGLE)
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=Tk.LEFT, fill=Tk.Y, expand=0)
listbox.pack(side=Tk.LEFT, fill=Tk.Y, expand=0)
# fill the listbox
for item in list_files:
    listbox.insert(Tk.END, item)

# select the last item in the listbox
listbox.after(10, lambda: listbox.focus_force())
listbox.after(10, lambda: listbox.selection_set("end"))
listbox.after(10, lambda: listbox.see(Tk.END))
# really we want the scrollabar to be down
listbox.after(500, lambda: listbox.see(Tk.END))

# autoselect the last item in the listbox after start
# and show the metadata and the image
if len(file_names) > 0:

    file_name = file_names[-1]
    if file_name[-5] == 'h':
        housekeeping = loadHouseKeeping(file_name)
        loaded_image = housekeeping
        showHouseKeeping(housekeeping)
    else:
        image = loadImage(file_names[-1])
        if image != 0:

            loaded_image = image
            loaded_image_idx = len(file_names)-1

            showImage(image, 1)

# bind onSelect() callback function to listbox
listbox.bind('<<ListboxSelect>>', onSelect)
#}

#{ BUTTON for loading new images and its CALLBACK

#{ loadNewImages() callback for loading new images from a text file
def loadNewImages():

    if sys.version_info[0] < 3:
        file_name = tkFileDialog.askopenfilename(initialdir = "./orbital_data/")
    else:
        file_name = tkinter.filedialog.askopenfilename(initialdir = "./orbital_data/")

    if file_name == "":
        return

    if not parseInputFile(file_name, v, root, autogenerate_csv_load.get()):
        return
    else:
        print("Successfully parsed the file \"{}\"".format(file_name))

    list_files = loadFiles()

    listbox.delete(0, Tk.END)

    v.set("Saving new png images")

    for item in list_files:
        listbox.insert(Tk.END, item)

    # generate pngs
    if autogenerate_png_load.get() == 1:
        idx=0
        for item in list_files:

            # generate pngs from
            image_filename='images_png/{}.png'.format(item)

            listbox.selection_clear(0, "end")
            listbox.selection_set(idx)
            listbox.see(idx)

            if item[-2] != 'h':
                try:
                    with open(image_filename) as file:
                        pass
                except IOError as e:
                    reloadData(idx, 0)

            idx += 1

    # listbox.selection_clear()
    listbox.after(10, lambda: listbox.selection_set("end"))
    listbox.after(500, lambda: listbox.see(Tk.END))

    global file_names
    # autoselect the last item in the listbox after start
    if len(file_names) > 0:
        file_name = file_names[-1]
        global loaded_image
        if file_name[-5] == 'h':
            housekeeping = loadHouseKeeping(file_name)
            loaded_image = housekeeping
            showHouseKeeping(housekeeping)
        else:
            image = loadImage(file_name)
            if image != 0:

                loaded_image = image
                showImage(image, 1)

    v.set("All images loaded")
#}

# spawn button for loading new images
load_button = Tk.Button(master=frame_list, text='Load new images', command=loadNewImages)
load_button.pack(side=Tk.TOP)

#}

#{ CHECKBOX for autogenerate_png_load

autogenerate_checkbox3 = Tk.Checkbutton(master=frame_list, text="export csv while loading", variable=autogenerate_csv_load)
autogenerate_checkbox3.pack(side=Tk.TOP)
# autogenerate_checkbox3.toggle()

autogenerate_checkbox2 = Tk.Checkbutton(master=frame_list, text="export pngs while loading", variable=autogenerate_png_load)
autogenerate_checkbox2.pack(side=Tk.TOP)
# autogenerate_checkbox2.toggle()

balloon2 = Pmw.Balloon(master=root);
balloon2.bind(autogenerate_checkbox2, "When checked, png images will generated (if they don't already exist) while importing new data.")

#}

#{ BUTTON for quitting the program and its CALLBACK

def close_window():
    root.withdraw()
    root.quit()
    root.destroy()
    # sys.exit()

def win_deleted():
    print("Closed from outside...");
    close_window();

# spawn quit button
button = Tk.Button(master=frame_left, text='Quit', command=close_window)
button.pack(side=Tk.BOTTOM)
#}

#{ CHECKBOX for autogenerate_png_view

def autogenerateCheckboxCallback():
    reloadList(int(listbox.curselection()[0]))

autogenerate_checkbox = Tk.Checkbutton(master=frame_list, text="export pngs while viewing", variable=autogenerate_png_view, command=autogenerateCheckboxCallback)
autogenerate_checkbox.pack(side=Tk.BOTTOM)

balloon = Pmw.Balloon(master=root);
balloon.bind(autogenerate_checkbox, "When checked, png images will be re-exported every time you click on an image.")

#}

#{ CHECKBOXES for showing and hiding images

show_globus = Tk.Checkbutton(master=frame_left, text="show globus", variable=show_globus_var, command=reloadCurrentImage)
show_globus.pack(side=Tk.BOTTOM)
# show_globus.toggle()

show_hidden = Tk.Checkbutton(master=frame_left, text="show hidden images", variable=show_hidden_var, command=reloadList)
show_hidden.pack(side=Tk.BOTTOM)

show_favorite_only = Tk.Checkbutton(master=frame_left, text="show only favorite", variable=show_favorite_var, command=reloadList)
show_favorite_only.pack(side=Tk.BOTTOM)

show_only_without_data = Tk.Checkbutton(master=frame_left, text="show only without data", variable=show_only_without_data_var, command=reloadList)
show_only_without_data.pack(side=Tk.BOTTOM)

hide_without_data = Tk.Checkbutton(master=frame_left, text="hide images without data", variable=hide_without_data_var, command=reloadList)
hide_without_data.pack(side=Tk.BOTTOM)

hide_housekeeping = Tk.Checkbutton(master=frame_left, text="hide housekeeping", variable=hide_housekeeping_var, command=reloadList)
hide_housekeeping.pack(side=Tk.BOTTOM)

#}

#{ KEYPRESS catching and respective CALLBACKS
# callback for detecting keypresses

#{ LISTBOX manipulation

def listbox_move_up():

    global loaded_image_idx

    try:
        index = int(listbox.curselection()[0])-1
        if index >= 0:
            listbox.selection_clear(0, "end")
            listbox.selection_set(index)
            listbox.see(index)
            loaded_image_idx = index
            reloadData(index, 1)
    except:
        return

def listbox_move_down():

    global loaded_image_idx

    try:
        index = int(listbox.curselection()[0])+1
        if index <= (listbox.size()-1):
            listbox.selection_clear(0, "end")
            listbox.selection_set(index)
            listbox.see(index)
            loaded_image_idx = index
            reloadData(index, 1)
    except:
        return
#}

def on_key_event(event):

    global listbox_focus
    if listbox_focus == 1:

        if event.char == 'j':
            listbox_move_down()

        if event.char == 'k':
            listbox_move_up()

        if event.char == 'o':
            loadNewImages()

        if event.char == 'g':
            show_globus.toggle()
            reloadCurrentImage()

        if event.char == 'h':
            marked_as_hidden_var.set(not marked_as_hidden_var.get())
            markHiddenCallback()

        if event.char == 'f':
            marked_as_favorite_var.set(not marked_as_favorite_var.get())
            markFavoriteCallback()

        if event.char == 'H':
            show_hidden_var.set(not show_hidden_var.get())
            reloadList()

        if event.char == 'F':
            show_favorite_var.set(not show_favorite_var.get())
            reloadList()

        if event.char == 'a':
            autogenerate_checkbox.toggle()

        if event.char == 'A':
            autogenerate_checkbox2.toggle()

listbox.bind_all('<Key>', on_key_event)

def listboxFocusIn(event):

    global listbox_focus
    listbox_focus = 1

def listboxFocusOut(event):

    global listbox_focus
    listbox_focus = 0

listbox.bind('<FocusIn>', listboxFocusIn)
listbox.bind('<FocusOut>', listboxFocusOut)
#}

root.protocol("WM_DELETE_WINDOW", win_deleted)
root.mainloop()
print("Exitting")
sys.exit()
