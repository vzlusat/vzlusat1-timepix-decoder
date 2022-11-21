#!/usr/bin/python

# #{ def installAndImport(package):
def installAndImport(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)
# #}

# #{ IMPORTS

installAndImport('matplotlib')
installAndImport('Pmw')

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.patches as patches # for plotting rectangles in the custom histogram
from matplotlib.figure import Figure

# to fix the colorbar's position
from mpl_toolkits.axes_grid1 import make_axes_locatable

import os
import numpy
import datetime
import re
import time
import sys

# import module which handles settings across other our modules
import src.settings as settings
settings.initSettings()

# for plotting the globe
if settings.use_globus:
  from mpl_toolkits.basemap import Basemap

if settings.calculate_tle:
  installAndImport('ephem')

# my custom functions
from src.Image import Image
from src.HouseKeeping import HouseKeeping
from src.loadImage import loadImage
from src.saveImage import saveImage
from src.saveHouseKeeping import saveHouseKeeping
from src.loadHouseKeeping import loadHouseKeeping
from src.parseInputFile import parseInputFile
from src.exportMethods import exportCsv
from src.exportMethods import exportImageForPixet
from src.exportMethods import exportInfoFileLine
from src.baseMethods import getPngFileName
from src.tle import *

tle1, tle2, tle_time = parseTLE("tle.txt")

# imports that depend on the python version
if sys.version_info[0] < 3:
    import Tkinter as Tk
    import tkFileDialog
    import ttk
    import tkFont
else:
    import tkinter as Tk
    import tkinter.filedialog
    from tkinter import ttk
    import tkinter.font as tkFont

# for showing commentary of the images
import src.comments as comments
comments.parseComments()

# for marking favorite images
import src.favorites as favorites
favorites.loadFavorites()

# #}

# core methods

# #{ def reloadData(index): reloads and shows metadata and image for a particular index in the listbox
def reloadData(index, manual):

    # list_files = loadFiles()
    global file_names
    try:
        file_name = file_names[index]
    except:
        file_name = file_names[-1]

    global loaded_image

    if file_name[-5] == 'h':
        housekeeping = loadHouseKeeping(file_name)
        loaded_image = housekeeping
        showHouseKeeping(housekeeping)
    else:
        image = loadImage(file_name)

        # if the file could not been opened, return
        if image == 0:
            print("file_could_not_be_opened")
            return

        loaded_image = image

        showImage(image, manual)
# #}

# #{ def loadFiles(): inspects "images_bin" folders and prepares the content for the listbox
def loadFiles():

    print("Reloading file list")

    # updated the filename list
    global file_names
    file_names = os.listdir("images_bin")

    file_names2 = sorted(file_names, key=numericalSort)
    file_names = []

    list_files = []

    previous_image = []
    image = []

    # create the list of files for the listbox
    for file in file_names2:

        if file[-5] == 'h':

            housekeeeping = loadHouseKeeping(file)

            if housekeeeping != 0:

                if hide_housekeeping_var.get():
                    pass
                elif (show_favorite_var.get() and not favorites.isFavorite(housekeeeping)):
                    pass
                # elif ((not show_hidden_var.get()) and (housekeeeping.hidden)):
                #     pass
                else:
                    file_names.append(file)
                    list_files.append(str(housekeeeping.images_taken)+"_"+str(housekeeeping.boot_count)+"_"+str(housekeeeping.time_since_boot)+"s_hk")
            else:
                print("could not open file "+file)

        else:

            previous_image = image
            image = loadImage(file)

            if image != 0:

                try:
                    from_id = int(from_id_var.get())
                    if from_id_var.get() != "" and image.id < from_id:
                        continue
                except:
                    pass

                try:
                    to_id = int(to_id_var.get())
                    if to_id_var.get() != "" and image.id > to_id:
                        continue
                except:
                    pass

                if (hide_with_metadata_var.get() and (image.got_metadata)):
                    pass
                elif (hide_without_data_var.get() and (not image.got_data)):
                    pass
                elif (show_only_without_data_var.get() and image.got_data):
                    pass
                elif (show_favorite_var.get() and not favorites.isFavorite(image)):
                    pass
                elif (show_nolearn_var.get() and not comments.isNolearn(image.id)):
                    pass
                elif (hide_nolearn_var.get() and comments.isNolearn(image.id)):
                    pass
                elif (show_adrenalin_var.get() and not comments.isAdrenalin(image.id)):
                    pass
                elif (show_xrb_var.get() and not comments.isXrb(image.id)):
                    pass
                elif (show_fullresdos_var.get() and not comments.isFullresDos(image.id)):
                    pass
                elif (show_saa_belts_var.get() and not comments.isSaaBelts(image.id)):
                    pass
                # elif ((not show_hidden_var.get()) and (image.hidden)):
                #     pass
                elif (just_fullres_var.get() and image.type > 1):
                    pass
                else:
                    if (first_image_type_var.get()):
                        if (image.type >= 2 and image.type <= 8) and not (isinstance(previous_image, Image) and previous_image.type >= 2 and previous_image.type <= 8):
                            pass
                        elif image.type == 1:
                            pass
                        else:
                            continue
                    file_names.append(file)
                    list_files.append(str(image.id)+"_"+str(image.type))
            else:
                print("could not open file "+file)

    print("File list reloaded, {} files in total".format(len(file_names)))

    return list_files
# #}

# #{ def showHouseKeeping(housekeeping): resets and shows housekeeping data
def showHouseKeeping(housekeeping):

    my_figure.clf()
    subplot1 = my_figure.add_subplot(111)
    subplot1.text(0.5, 0.5, 'No data', horizontalalignment='center',verticalalignment='center', transform = subplot1.transAxes)
    subplot1.axes.get_xaxis().set_visible(False)
    subplot1.axes.get_yaxis().set_visible(False)
    subplot1.patch.set_visible(False)
    subplot1.axis('off')

    figure_canvas.draw()

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
    human_readable_time = datetime.datetime.utcfromtimestamp(housekeeping.time)
    metadatas_var[16].set(human_readable_time)

    # marked_as_hidden_var.set(housekeeping.hidden)
    marked_as_favorite_var.set(favorites.isFavorite(housekeeping))

    if settings.use_globus:
      if show_globus_var.get():
          latitude, longitude, tle_date = getLatLong(housekeeping.time, tle1, tle2, tle_time)
          globus_label_var.set("{}, {}\nTLE: {}".format(latitude, longitude, tle_date))

          redrawMap(latitude, longitude, human_readable_time)
      else:
          clearMap()

    statusLine.set('')
# #}

# #{ def showImage(image): resets and shows the image
def showImage(image, manual):

    # marked_as_hidden_var.set(image.hidden)
    marked_as_favorite_var.set(favorites.isFavorite(image))

    marked_as_nolearn_var.set(comments.isNolearn(image.id))

    if manual == 0 and image.got_data == 0:
        return

    # Clear the previous metadata
    for i in range(0, 21):
        metadatas_var[i].set("")

    metadatas_var[0].set(str(image.id))

    if image.type == 1:
        img_type = "Full resolution"
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

    # #{ METADATA
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
            mode = "MPX"
        else:
            mode = "TOT"

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
        metadatas_var[7].set(image.original_pixels)
        metadatas_var[8].set(image.filtered_pixels)
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

        human_readable_time = datetime.datetime.utcfromtimestamp(image.time)
        metadatas_var[19].set(human_readable_time)

        if settings.use_globus:
          if show_globus_var.get():
              latitude, longitude, tle_date = getLatLong(image.time, tle1, tle2, tle_time)
              globus_label_var.set("{}, {}\nTLE: {}".format(latitude, longitude, tle_date))

              redrawMap(latitude, longitude, human_readable_time)
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

    # #}

    # #{ IMAGE
    if (image.got_data == 1 or image.original_pixels == 0) and dont_redraw_var.get() == 0:

        if image.type >= 1 and image.type <= 8:

            # print("numpy.count_nonzero(image.data): {}".format(numpy.count_nonzero(image.data)))

            # plot the image
            my_figure.clf()
            subplot1 = my_figure.add_subplot(111)

            subplot1.set_xlabel("Column (pixel)")
            subplot1.set_ylabel("Row (pixel)")

            human_readable_time = datetime.datetime.utcfromtimestamp(image.time)

            if image.got_metadata == 1:
                subplot1.set_title(img_type+" n.{0}, {1} s exposure, ".format(image.id, exposure)+mode+" mode, {}".format(human_readable_time), fontsize=13, y=1.02)
            else:
                subplot1.set_title(img_type+" n.{0}, ??? s exposure, ".format(image.id)+"??? mode", fontsize=13, y=1.02)

            # show the image
            im = []
            try:
                im = subplot1.imshow(image.data, interpolation='none', cmap=colormap_variable.get())
            except:
                print("Desired colormap '{}' does not exist, using 'nipy_spectral_r' instead!".format(colormap_variable.get()))
                im = subplot1.imshow(image.data, interpolation='none', cmap="nipy_spectral_r")

            # create the colormap bar and place it in the correct place
            divider = make_axes_locatable(my_figure.gca())
            cax = divider.append_axes("right", size="5%", pad=0.2)
            cbar = my_figure.colorbar(im, cax=cax)

            cbar.ax.get_yaxis().labelpad = 20
            if image.type == 1:
                if image.mode == 0:
                    if image.got_metadata == 0:
                        cbar.ax.set_ylabel('?counts?', rotation=270)
                    else:
                        cbar.ax.set_ylabel('counts', rotation=270)
                else:
                    cbar.ax.set_ylabel('keV/pixel', rotation=270)
            else:
                cbar.ax.set_ylabel('active pixels in the bin', rotation=270)

            my_figure.tight_layout(pad=1)
        # #}

        # #{ SUMS
        elif image.type == 16 and dont_redraw_var.get() == 0:

            my_figure.clf()
            a1 = my_figure.add_subplot(211)
            a2 = my_figure.add_subplot(212)

            x = numpy.linspace(1, 256, 256)

            a1.plot(x, image.data[0, :])
            a2.plot(x, image.data[1, :])
            a1.axis([1, 256, numpy.min(image.data[0, :]), numpy.max(image.data[0, :])])
            a2.axis([1, 256, numpy.min(image.data[1, :]), numpy.max(image.data[1, :])])

            human_readable_time = datetime.datetime.utcfromtimestamp(image.time)

            if image.got_metadata == 1:
                a1.set_title("Row summs n.{0}, {1} s exposure, {2}".format(image.id, exposure, human_readable_time), fontsize=13, y=1.02)
            else:
                a1.set_title("Row summs n.{0}, ??? s exposure ".format(image.id), fontsize=13, y=1.02)
            a1.set_xlabel("Row (pixel)")
            a1.set_ylabel("Active pixel count (-)")

            if image.got_metadata == 1:
                a2.set_title("Column summs n.{0}, {1} s exposure, {2}".format(image.id, exposure, human_readable_time), fontsize=13, y=1.02)
            else:
                a2.set_title("Column summs n.{0}, ??? s exposure ".format(image.id), fontsize=13, y=1.02)
            a2.set_xlabel("Column (pixel)")
            a2.set_ylabel("Active pixel count (-)")

            my_figure.tight_layout(pad=2)
        # #}

        # #{ HISTOGRAM
        elif image.type == 32 and dont_redraw_var.get() == 0:

            my_figure.clf()
            subplot1 = my_figure.add_subplot(111)

            x = [2.9807, 4.2275, 6.4308, 10.3875, 16.6394, 24.7081, 33.7833, 43.3679, 53.2233, 63.2344, 73.3415, 83.5115, 93.7248, 103.9691, 114.2361, 124.5204, 134.8182]

            for i in range(0, 16):

                # rectangle('Position', [x(i), 0, x(i+1)-x(i), image.data(i)], 'FaceColor', [0 0.5 0.5], 'EdgeColor', 'b','LineWidth',1);
                try:
                    subplot1.add_patch(
                        patches.Rectangle(
                            (x[i], 0),            # (x,y)
                            x[i+1]-x[i],          # width
                            image.data[0, i],                  # height
                        )
                    )
                except:
                    pass

            # subplot1.plot(x, image.data[0, :])

            subplot1.relim()
            subplot1.autoscale_view()

            if image.got_metadata == 1:
                if image.mode == 0:
                    subplot1.set_xlabel("Particle counts (-)")
                else:
                    subplot1.set_xlabel("Energy (keV)")
            else:
                subplot1.set_xlabel("Pixel values (-)")

            subplot1.set_ylabel("Counts (-)")

            human_readable_time = datetime.datetime.utcfromtimestamp(image.time)

            if image.got_metadata == 1:
                subplot1.set_title("Image histogram n.{0}, {1} s exposure, ".format(image.id, exposure)+mode+" mode, {}".format(human_readable_time), fontsize=13, y=1.02)
            else:
                subplot1.set_title("Image histogram n.{0}, ??? s exposure, ".format(image.id)+"??? mode", fontsize=13, y=1.02)

            my_figure.tight_layout(pad=1)
        # #}

        if ((manual == 1 and autogenerate_png_view.get() == 1) or (manual == 0)) and image.got_data == 1:

            my_figure.savefig(getPngFileName(image.id, image.type), dpi=250, bbox_inches='tight', transparent=True)

            if settings.use_globus and show_globus_var.get():
                image_globus_filename='images_png/{}_map.png'.format(image.id)
                my_figure2.savefig(image_globus_filename, dpi=150, bbox_inches='tight', transparent=True)

    else: # we have not data to show

        my_figure.clf()
        subplot1 = my_figure.add_subplot(111)
        if dont_redraw_var.get() == 0:
            subplot1.text(0.5, 0.5, 'No data', horizontalalignment='center',verticalalignment='center', transform = subplot1.transAxes)
        else:
            subplot1.text(0.5, 0.5, 'Plotting disabled', horizontalalignment='center',verticalalignment='center', transform = subplot1.transAxes)
        subplot1.axes.get_xaxis().set_visible(False)
        subplot1.axes.get_yaxis().set_visible(False)
        subplot1.patch.set_visible(False)
        subplot1.axis('off')

    figure_canvas.draw()

    id_baloon.bind(label, comments.getComment(image.id))
    statusLine.set(comments.getComment(image.id))
# #}

# callback for marking hidden/favorite checkboxex

# def markHiddenCallback():

#     global loaded_image
#     loaded_image.hidden = marked_as_hidden_var.get()

#     if isinstance(loaded_image, Image):
#         saveImage(loaded_image)
#     elif isinstance(loaded_image, HouseKeeping):
#         saveHouseKeeping(loaded_image)

#     reloadList(int(listbox.curselection()[0]))

def markFavoriteCallback():

    global loaded_image
    # loaded_image.favorite = marked_as_favorite_var.get()

    favorites.setFavorite(loaded_image, marked_as_favorite_var.get())

    # if isinstance(loaded_image, Image):
    #     saveImage(loaded_image)
    # elif isinstance(loaded_image, HouseKeeping):
    #     saveHouseKeeping(loaded_image)

    reloadList(int(listbox.curselection()[0]))

def markNolearnCallback():

    global loaded_image
    global loaded_image_idx
    # loaded_image.favorite = marked_as_favorite_var.get()

    print("marked_as_nolearn_var.get(): {}".format(marked_as_nolearn_var.get()))

    if marked_as_nolearn_var.get():
      comments.addTag(loaded_image.id, "#nolearn")
    else:
      comments.removeTag(loaded_image.id, "#nolearn")

    # if isinstance(loaded_image, Image):
    #     saveImage(loaded_image)
    # elif isinstance(loaded_image, HouseKeeping):
    #     saveHouseKeeping(loaded_image)

    # reloadList(int(listbox.curselection()[0]))
    reloadData(loaded_image_idx, 1)

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

# #{ create directories
if not os.path.exists("images_bin"):
    os.makedirs("images_bin")

if not os.path.exists("images_csv"):
    os.makedirs("images_csv")

if not os.path.exists("images_png"):
    os.makedirs("images_png")
# #}

# Load TLE
if settings.calculate_tle:
  from src.tle import *
  parseTLE()

# create the root window
root = Tk.Tk()

import src.statusLine as statusLine

if settings.gpd_enabled:
    customfont = tkFont.Font(family="Arial", size=8)
else:
    customfont = tkFont.Font(family="Arial", size=12)

if not settings.gpd_enabled:
    settings.scale = 1.0
    settings.window_width = 1380
    settings.window_height = 750

root.tk.call('tk', 'scaling', settings.scale)
root.resizable(width=1, height=1)
import platform
if platform.system() == "Windows":
    root.geometry('{}x{}'.format(1380, 900))
else:
    root.geometry('{}x{}'.format(settings.window_width, settings.window_height))
root.wm_title("VZLUSAT-1 X-Ray data decoder")

# create the main Frame in the root window
frame_main = Tk.Frame(root);
frame_main.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# create the figure
if not settings.gpd_enabled:
    my_figure = Figure(facecolor='none', figsize=(8.2, 6.8), dpi=90)
else:
    my_figure = Figure(facecolor='none', figsize=(8.2, 6.8), dpi=120)
my_figure.clf()

statusLine.init(root, customfont)

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

# initialize Pmw (creates on-hover hints)
Pmw.initialise(root)

# #{ create the labels for metadatas and their respective control variables
metadatas = []
metadatas_var = []
text_labels = []
text_labels_var = []
for i in range(0, len(Image.metadata_labels)): #Rows

    # labels on the left containing the "labels"
    text_labels_var.append(Tk.StringVar())
    label = Tk.Label(frame_mid_top, textvariable=text_labels_var[i], font=customfont)
    text_labels.append((label).grid(row=i, column=0, sticky=Tk.E))

    # lables on the right containing the "values"
    metadatas_var.append(Tk.StringVar())
    metadatas.append(Tk.Label(frame_mid_top, textvariable=metadatas_var[i], font=customfont).grid(row=i, column=1, sticky=Tk.W))

    # filtration
    if i == 0:
        id_baloon = Pmw.Balloon(master=root);
        id_baloon.bind(label, "Unique ID of the image. The first orbital image was 385.")

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
# marked_as_hidden_var = Tk.IntVar()
# metadatas.append(Tk.Checkbutton(frame_mid_top, text="", variable=marked_as_hidden_var, command=markHiddenCallback).grid(row=len(Image.metadata_labels)-2, column=1, sticky=Tk.W))

marked_as_favorite_var = Tk.IntVar()
metadatas.append(Tk.Checkbutton(frame_mid_top, text="", variable=marked_as_favorite_var, command=markFavoriteCallback).grid(row=len(Image.metadata_labels)-2, column=1, sticky=Tk.W))

marked_as_nolearn_var = Tk.IntVar()
metadatas.append(Tk.Checkbutton(frame_mid_top, text="", variable=marked_as_nolearn_var, command=markNolearnCallback).grid(row=len(Image.metadata_labels)-1, column=1, sticky=Tk.W))

housekeeping_values = []
housekeeping_labels = []
# #}

# create the subframe for the figure
frame_figure = Tk.Frame(frame_right);
frame_figure.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=0, padx=5, pady=5)

# create the matplotlib's figure canvas
figure_canvas = FigureCanvasTkAgg(my_figure, master=frame_figure)
figure_canvas.draw()
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

if settings.use_globus:

  globus_label_var = Tk.StringVar()
  globus_label = Tk.Label(frame_mid_bottom, anchor=Tk.S, justify=Tk.CENTER,  textvariable=globus_label_var, font=customfont)
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
    globus_canvas.draw()
    globus_label_var.set("")

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

    globus_canvas.draw()

# create the toolbar for the figure
frame_toolbar = Tk.Frame(frame_figure);
frame_toolbar.pack(side=Tk.TOP, expand=0)

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
toolbar.pack(side=Tk.TOP)
toolbar.update()

# create the one and only subplot in the figure
subplot1 = my_figure.add_subplot(111)
subplot1.axes.get_xaxis().set_visible(False)
subplot1.axes.get_yaxis().set_visible(False)
subplot1.patch.set_visible(False)
subplot1.axis('off')
figure_canvas.draw()

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
# autogenerate_csv_load = Tk.IntVar()

# user can switch on/off showing of hidden and favorite images
# show_hidden_var = Tk.IntVar()
show_globus_var = Tk.IntVar()
dont_redraw_var = Tk.IntVar()
just_fullres_var = Tk.IntVar()
first_image_type_var = Tk.IntVar()
show_favorite_var = Tk.IntVar()
show_nolearn_var = Tk.IntVar()
hide_nolearn_var = Tk.IntVar()
hide_without_data_var = Tk.IntVar()
hide_with_metadata_var = Tk.IntVar()
show_only_without_data_var = Tk.IntVar()
hide_housekeeping_var = Tk.IntVar()
show_adrenalin_var = Tk.IntVar()
show_xrb_var = Tk.IntVar()
show_fullresdos_var = Tk.IntVar()
show_saa_belts_var = Tk.IntVar()
from_id_var = Tk.StringVar()
to_id_var = Tk.StringVar()

# user can mark image as favorite or hidden
# image_is_hidden = Tk.IntVar()

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

# #{ LISTBOX (+SCROLLBAR) and its CALLBACK

# #{ def onSelect(evt): callback function for showing the image after clicking the listbox
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
# #}

scrollbar = Tk.Scrollbar(master=frame_list2, orient=Tk.VERTICAL)
listbox = Tk.Listbox(master=frame_list2, yscrollcommand=scrollbar.set, selectmode=Tk.SINGLE, font=customfont)
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=Tk.LEFT, fill=Tk.Y, expand=0)
listbox.pack(side=Tk.LEFT, fill=Tk.Y, expand=0)
# fill the listbox
for item in list_files:
    listbox.insert(Tk.END, item)

# select the last item in the listbox
# listbox.after(10, lambda: listbox.focus_force())
listbox.after(10, lambda: listbox.selection_set("end"))
listbox.after(10, lambda: listbox.see(Tk.END))
# really we want the scrollabar to be down
listbox.after(1000, lambda: listbox.see(Tk.END))
listbox.after(1250, lambda: listbox.focus_force())

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
# #}

# #{ BUTTON for loading new images and its CALLBACK

# #{ loadNewImages() callback for loading new images from a text file
def loadNewImages():

    if sys.version_info[0] < 3:
        file_name = tkFileDialog.askopenfilename(initialdir = "./orbital_data/")
    else:
        file_name = tkinter.filedialog.askopenfilename(initialdir = "./orbital_data/")

    print("file_name: {}".format(file_name))

    if file_name == "":
        return

    if not parseInputFile(file_name, root):
        print("could not parse the input file")
        return
    else:
        print("Successfully parsed the file \"{}\"".format(file_name))

    list_files = loadFiles()

    listbox.delete(0, Tk.END)

    statusLine.set("Saving new png images")

    for item in list_files:
        listbox.insert(Tk.END, item)

    # generate pngs
    if autogenerate_png_load.get() == 1:
        print("Generating png images")
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
        print("png images generated")

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

    statusLine.set("All images loaded")
# #}

# #{ exportCsv() callback
def exportCsvData():

    statusLine.set("Exporting images to csv")

    image_iter = 1

    for file_name in file_names:

        if file_name[-5] == 'h':
            housekeeping = loadHouseKeeping(file_name)
            exportCsv(housekeeping)
            statusLine.set("Exporting HK")
        else:
            image = loadImage(file_name)
            exportCsv(image)
            statusLine.set("Exporting image {}".format(image.id))

    statusLine.set("Images exported")

# #}

# #{ exportRaw() callback
def exportRawFullresData():

    statusLine.set("Exporting fullres images for analysis")

    image_iter = 1

    with open("images_csv/info.txt", "w") as info_file:

        for file_name in file_names:

            image = loadImage(file_name)

            if isinstance(image, Image):

                if image.type == 1 and image.got_data and image.got_metadata:

                    exportImageForPixet(image, image_iter)

                    if image_iter == 1:
                        first = True
                    else:
                        first = False

                    if first:
                        info_line = exportInfoFileLine(image, first)
                        info_file.write("# ordinar image ID, original image ID, {}\r\n".format(info_line))

                    info_line = exportInfoFileLine(image, False)
                    info_file.write("{}, {}, {}\r\n".format(image_iter, image.id, info_line))

                    image_iter += 1
                    statusLine.set("Exporting image {}".format(image.id))

        statusLine.set("Images exported")

# #{ exportRaw() callback
def exportRawNonfullresData():

    statusLine.set("Exporting non-fullres images for analysis")

    image_iter = 0
    prev_id = 0

    with open("images_csv/info.txt", "w") as info_file:

        for file_name in file_names:

            image = loadImage(file_name)

            if isinstance(image, Image):

                if image.type >= 1 and image.got_data and image.got_metadata:

                    if image.id != prev_id:
                        image_iter += 1
                        prev_id = image.id

                    exportImageForPixet(image, image_iter)

                    if image_iter == 1:
                        first = True
                    else:
                        first = False

                    if first:
                        info_line = exportInfoFileLine(image, first)
                        info_file.write("# ordinar image ID, original image ID, {}\r\n".format(info_line))

                    info_line = exportInfoFileLine(image, False)
                    info_file.write("{}, {}, {}\r\n".format(image_iter, image.id, info_line))

                    statusLine.set("Exporting image {}".format(image.id))

        statusLine.set("Images exported")

# #}

# #{ exportRawForPublic() callback
def exportRawForPublic():

    statusLine.set("Exporting raw images for public")

    image_iter = 0
    prev_id = 0

    with open("images_csv/info.txt", "w") as info_file:

        for file_name in file_names:

            image = loadImage(file_name)

            if isinstance(image, Image):

                # atempt to reconstruct the TLE
                latitude, longitude, tle_date = getLatLong(image.time, tle1, tle2, tle_time)

                if image.type == 1 and image.got_data and image.got_metadata and not comments.isNolearn(image.id) and not image.filtering:

                    if latitude != 0 and longitude != 0:

                        if image.id != prev_id:
                            image_iter += 1
                            prev_id = image.id

                        exportImageForPixet(image, image_iter)

                        if image_iter == 1:
                            first = True
                        else:
                            first = False

                        if first:
                            info_line = exportInfoFileLine(image, first)
                            info_file.write("# ordinar image ID, original image ID, {}\r\n".format(info_line))

                        info_line = exportInfoFileLine(image, False)
                        info_file.write("{}, {}, {}\r\n".format(image_iter, image.id, info_line))

                        statusLine.set("Exporting image {}".format(image.id))

                    else:

                        print("skipping image {}, tle could not be reconstructed", image.id)

        statusLine.set("Images exported")

# #}

# spawn button for loading new images
load_button = Tk.Button(master=frame_list, text='Load new images', command=loadNewImages, font=customfont)
load_button.pack(side=Tk.TOP)

autogenerate_checkbox2 = Tk.Checkbutton(master=frame_list, text="export pngs while loading (E)", variable=autogenerate_png_load, font=customfont)
autogenerate_checkbox2.pack(side=Tk.TOP)
# autogenerate_checkbox2.toggle()

balloon2 = Pmw.Balloon(master=root);
balloon2.bind(autogenerate_checkbox2, "When checked, png images will generated (if they don't already exist) while importing new data.")

# #}

# #{ BUTTON for quitting the program and its CALLBACK

def close_window():
    root.withdraw()
    root.quit()
    root.destroy()
    # sys.exit()

def win_deleted():
    print("Closed from outside...");
    close_window();

# spawn quit button
button = Tk.Button(master=frame_left, text='Quit', command=close_window, font=customfont)
button.pack(side=Tk.BOTTOM)
# #}

# #{ CHECKBOX for autogenerate_png_view

def autogenerateCheckboxCallback():
    reloadList(int(listbox.curselection()[0]))

# spawn button for exporting csv
export_csv_button = Tk.Button(master=frame_list, text='Export CSV', command=exportCsvData, font=customfont)
export_csv_button.pack(side=Tk.BOTTOM)

export_raw_button = Tk.Button(master=frame_list, text='Export RAW fullres', command=exportRawFullresData, font=customfont)
export_raw_button.pack(side=Tk.BOTTOM)

export_raw_button = Tk.Button(master=frame_list, text='Export RAW other', command=exportRawNonfullresData, font=customfont)
export_raw_button.pack(side=Tk.BOTTOM)

export_public_button = Tk.Button(master=frame_list, text='Export data for public use', command=exportRawForPublic, font=customfont)
export_public_button.pack(side=Tk.BOTTOM)

autogenerate_checkbox = Tk.Checkbutton(master=frame_list, text="export pngs while viewing (e)", variable=autogenerate_png_view, command=autogenerateCheckboxCallback, font=customfont)
autogenerate_checkbox.pack(side=Tk.BOTTOM)

balloon = Pmw.Balloon(master=root);
balloon.bind(autogenerate_checkbox, "When checked, png images will be re-exported every time you click on an image.")

# #}

# #{ CHECKBOXES for showing and hiding images

if settings.use_globus:
  show_globus = Tk.Checkbutton(master=frame_left, text="show globus (gt)", variable=show_globus_var, command=reloadCurrentImage, font=customfont)
  show_globus.pack(side=Tk.BOTTOM)
# show_globus.toggle()

just_metadata = Tk.Checkbutton(master=frame_left, text="Show just metadata (m)", variable=dont_redraw_var, command=reloadCurrentImage, font=customfont)
just_metadata.pack(side=Tk.BOTTOM)

just_fullres = Tk.Checkbutton(master=frame_left, text="Show just fullres (1)", variable=just_fullres_var, command=reloadList, font=customfont)
just_fullres.pack(side=Tk.BOTTOM)

first_image_type = Tk.Checkbutton(master=frame_left, text="Show first image type (i)", variable=first_image_type_var, command=reloadList, font=customfont)
first_image_type.pack(side=Tk.BOTTOM)

# temp_baloon = Pmw.Balloon(master=root);
# temp_baloon.bind(just_fullres, "hotkey: 1")

# show_hidden = Tk.Checkbutton(master=frame_left, text="show hidden images", variable=show_hidden_var, command=reloadList, font=customfont)
# show_hidden.pack(side=Tk.BOTTOM)

show_adrenalin = Tk.Checkbutton(master=frame_left, text="show only adrenalin (a)", variable=show_adrenalin_var, command=reloadList, font=customfont)
show_adrenalin.pack(side=Tk.BOTTOM)

show_xrb = Tk.Checkbutton(master=frame_left, text="show only XRB (x)", variable=show_xrb_var, command=reloadList, font=customfont)
show_xrb.pack(side=Tk.BOTTOM)

show_fullresdos = Tk.Checkbutton(master=frame_left, text="show only FullRes dosimetry", variable=show_fullresdos_var, command=reloadList, font=customfont)
show_fullresdos.pack(side=Tk.BOTTOM)

show_saa_belts = Tk.Checkbutton(master=frame_left, text="show only SAA and belt scanning", variable=show_saa_belts_var, command=reloadList, font=customfont)
show_saa_belts.pack(side=Tk.BOTTOM)

show_favorite_only = Tk.Checkbutton(master=frame_left, text="show only favorite (f)", variable=show_favorite_var, command=reloadList, font=customfont)
show_favorite_only.pack(side=Tk.BOTTOM)

show_nolearn_only = Tk.Checkbutton(master=frame_left, text="show only nolearn (N)", variable=show_nolearn_var, command=reloadList, font=customfont)
show_nolearn_only.pack(side=Tk.BOTTOM)

hide_nolearn = Tk.Checkbutton(master=frame_left, text="hide nolearn (n)", variable=hide_nolearn_var, command=reloadList, font=customfont)
hide_nolearn.pack(side=Tk.BOTTOM)

show_only_without_data = Tk.Checkbutton(master=frame_left, text="show only without data (W)", variable=show_only_without_data_var, command=reloadList, font=customfont)
show_only_without_data.pack(side=Tk.BOTTOM)

hide_without_data = Tk.Checkbutton(master=frame_left, text="hide images without data (w)", variable=hide_without_data_var, command=reloadList, font=customfont)
hide_without_data.pack(side=Tk.BOTTOM)

hide_with_metadata = Tk.Checkbutton(master=frame_left, text="show images with missing metadata (M)", variable=hide_with_metadata_var, command=reloadList, font=customfont)
hide_with_metadata.pack(side=Tk.BOTTOM)

hide_housekeeping = Tk.Checkbutton(master=frame_left, text="hide housekeeping (h)", variable=hide_housekeeping_var, command=reloadList, font=customfont)
hide_housekeeping.pack(side=Tk.BOTTOM)

frame_from_to = Tk.Frame(frame_left);
frame_from_to.pack(side=Tk.BOTTOM)

from_id = Tk.Entry(master=frame_from_to, textvariable=from_id_var, width=6)
to_id = Tk.Entry(master=frame_from_to, textvariable=to_id_var, width=6)
reload_but = Tk.Button(master=frame_from_to, text="R", command=reloadList)

from_id.pack(side=Tk.LEFT)
to_id.pack(side=Tk.LEFT)
reload_but.pack(side=Tk.LEFT)

# #}

# #{ KEYPRESS catching and respective CALLBACKS
# callback for detecting keypresses

# #{ LISTBOX manipulation

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
# #}

global previous_key
global current_key
previous_key = []
current_key = []
def on_key_event(event):

    global listbox_focus
    global previous_key
    global current_key
    global loaded_image_idx
    if listbox_focus == 1:

        previous_key = current_key
        current_key = event.char

        if current_key == 'j':
            listbox_move_down()

        if current_key == 'k':
            listbox_move_up()

        if current_key == 'o':
            loadNewImages()

        if settings.use_globus:
            if event.char == 't' and previous_key == 'g':
                current_key = []
                show_globus.toggle()
                reloadCurrentImage()

        if current_key == 'G':
            listbox.selection_clear(0, "end")
            listbox.after(10, lambda: listbox.selection_set("end"))
            listbox.after(500, lambda: listbox.see(Tk.END))
            loaded_image_idx = listbox.size()-1
            reloadData(listbox.size()-1, 1)

        if current_key == 'g':
            if previous_key == 'g':
                current_key = []
                listbox.selection_clear(0, "end")
                listbox.after(10, lambda: listbox.selection_set(0))
                listbox.after(500, lambda: listbox.see(0))
                loaded_image_idx = 0
                reloadData(0, 1)

        if current_key == 'h':
            hide_housekeeping.toggle()
            reloadList()

        if current_key == 'a':
            show_adrenalin.toggle()
            reloadList()

        if current_key == '1':
            just_fullres.toggle()
            reloadList()

        if current_key == 'x':
            show_xrb.toggle()
            reloadList()

        if current_key == 'i':
            first_image_type.toggle()
            reloadList()

        if current_key == 'f':
            if previous_key == 'g':
                current_key = []
                marked_as_favorite_var.set(not marked_as_favorite_var.get())
                markFavoriteCallback()
            else:
                show_favorite_var.set(not show_favorite_var.get())
                reloadList()

        if current_key == 'n':
            if previous_key == 'g':
                current_key = []
                marked_as_nolearn_var.set(not marked_as_nolearn_var.get())
                markNolearnCallback()
            else:
                hide_nolearn_var.set(not hide_nolearn_var.get())
                reloadList()

        if current_key == 'N':
            show_nolearn_var.set(not show_nolearn_var.get())
            reloadList()

        if current_key == 'e':
            autogenerate_checkbox.toggle()

        if current_key == 'E':
            autogenerate_checkbox2.toggle()

        if current_key == 'w':
            hide_without_data.toggle()
            reloadList()

        if current_key == 'm':
            just_metadata.toggle()
            reloadCurrentImage()

        if current_key == 'M':
            hide_with_metadata.toggle()
            reloadList()

        if current_key == 'W':
            show_only_without_data.toggle()
            reloadList()

        if current_key == 'c':
            try:
                colormap_combobox.current(colormap_combobox.current()+1)
                reloadCurrentImage()
            except:
                pass

        if current_key == 'C':
            try:
                colormap_combobox.current(colormap_combobox.current()-1)
                reloadCurrentImage()
            except:
                pass

listbox.bind_all('<Key>', on_key_event)



def listboxFocusIn(event):

    global listbox_focus
    listbox_focus = 1

def listboxFocusOut(event):

    global listbox_focus
    listbox_focus = 0

listbox.bind('<FocusIn>', listboxFocusIn)
listbox.bind('<FocusOut>', listboxFocusOut)
# #}

root.protocol("WM_DELETE_WINDOW", win_deleted)
root.mainloop()
print("Exitting")
sys.exit()
