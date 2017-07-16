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
from src.loadHouseKeeping import loadHouseKeeping
from src.parseInputFile import parseInputFile

# imports that depend on the python version
if sys.version_info[0] < 3:
    import Tkinter as Tk
    import tkFileDialog
else:
    import tkinter as Tk
    import tkinter.filedialog

#}

# core methods

#{ def reloadData(index): reloads and shows metadata and image for a particular index in the listbox
def reloadData(index, manual):

    file_name = file_names[index]
    if file_name[-5] == 'h':
        housekeeping = loadHouseKeeping(file_names[index])
        showHouseKeeping(housekeeping)
    else:
        image = loadImage(file_names[index])

        # if the file could not been opened, return
        if image == 0:
            return

        showImage(image, manual)
#}

#{ def loadFiles(): inspects "images_bin" folders and prepares the content for the listbox
def loadFiles():

    # updated the filename list
    global file_names
    file_names = os.listdir("images_bin")

    file_names = sorted(file_names, key=numericalSort)

    list_files = []

    # create the list of files for the listbox
    for file in file_names:

        if file[-5] == 'h':

            housekeeeping = loadHouseKeeping(file)

            if housekeeeping != 0:
                list_files.append(str(housekeeeping.images_taken)+"_"+str(housekeeeping.time_since_boot)+"s_hk")
            else:
                print("could not open file "+file)

        else:

            image = loadImage(file)

            if image != 0:
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
#}

#{ def showImage(image): resets and shows the image
def showImage(image, manual):

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

        human_readible_time = datetime.datetime.fromtimestamp(image.time).strftime('%Y-%m-%d %H:%M:%S')
        metadatas_var[19].set(human_readible_time)

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

            im = subplot1.imshow(image.data, interpolation='none', cmap=colormap)
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

        if ((manual == 1 and autogenerate_png.get() == 1) or (manual == 0)) and image.got_data == 1:

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

# AFTER LAUNCH

#{ create directories
if not os.path.exists("images_bin"):
    os.makedirs("images_bin")

if not os.path.exists("images_csv"):
    os.makedirs("images_csv")

if not os.path.exists("images_png"):
    os.makedirs("images_png")
#}

# create the root window
root = Tk.Tk()
root.resizable(width=1, height=1)
root.geometry('{}x{}'.format(1300, 650))
root.wm_title("VZLUSAT-1 X-Ray data decoder")

# create the main Frame in the root window
frame_main = Tk.Frame(root);
frame_main.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# create the figure
my_figure = Figure(facecolor='none', figsize=(8, 6), dpi=100)
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
frame_middle.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0, padx=10, pady=30)

#{ create the labels for metadatas and their respective control variables
metadatas = []
metadatas_var = []
text_labels = []
text_labels_var = []
for i in range(0, len(Image.metadata_labels)): #Rows

    # labels on the left containing the "labels"
    text_labels_var.append(Tk.StringVar())
    text_labels.append(Tk.Label(frame_middle, textvariable=text_labels_var[i]).grid(row=i, column=0, sticky=Tk.E))

    # lables on the right containing the "values"
    metadatas_var.append(Tk.StringVar())
    metadatas.append(Tk.Label(frame_middle, textvariable=metadatas_var[i]).grid(row=i, column=1, sticky=Tk.W))

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

# create the toolbar for the figure
frame_toolbar = Tk.Frame(frame_figure);
frame_toolbar.pack(side=Tk.BOTTOM, fill=Tk.Y, expand=1)

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
colormap = "bone_r"

# this variable is bound to the "autogenerate" checkbox
autogenerate_png = Tk.IntVar()

# preload and sort file names from "images_bin" directories
global file_names
list_files = loadFiles()

frame_list = Tk.Frame(frame_left);
frame_list.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

frame_list2 = Tk.Frame(frame_list);
frame_list2.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=1)

#{ LISTBOX (+SCROLLBAR) and its CALLBACK

#{ def onSelect(evt): callback function for showing the image after clicking the listbox
def onSelect(evt):

    global file_names

    w = evt.widget

    if len(w.curselection()) == 0:
        return

    # extract the index of the selected item
    index = int(w.curselection()[0])

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
listbox.after(100, lambda: listbox.see(Tk.END))

# autoselect the last item in the listbox after start
# and show the metadata and the image
if len(file_names) > 0:
    file_name = file_names[-1]
    if file_name[-5] == 'h':
        print("HK selected")
    else:
        image = loadImage(file_names[-1])
        if image != 0:
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

    if not parseInputFile(file_name, v, root):
        return
    else:
        print("Successfully opened the file \"{}\"".format(file_name))

    list_files = loadFiles()

    listbox.delete(0, Tk.END)

    v.set("Saving new png images")

    for item in list_files:
        listbox.insert(Tk.END, item)

    idx=0
    for item in list_files:

        # generate pngs from
        image_filename='images_png/{}.png'.format(item)

        try:
            with open(image_filename) as file:
                pass
        except IOError as e:
            reloadData(idx, 0)

        idx += 1

    # listbox.selection_clear()
    listbox.after(10, lambda: listbox.selection_set("end"))
    listbox.after(10, lambda: listbox.see(Tk.END))

    # autoselect the last item in the listbox after start
    if len(file_names) > 0:
        file_name = file_names[-1]
        if file_name[-5] == 'h':
            print("HK selected")
        else:
            image = loadImage(file_names[-1])
            if image != 0:
                showImage(image, 0)

    v.set("All images loaded")
#}

# spawn button for loading new images
load_button = Tk.Button(master=frame_list, text='Load new images', command=loadNewImages)
load_button.pack(side=Tk.TOP)

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

#{ CHECKBOX for autogenerate_png

autogenerate_checkbox = Tk.Checkbutton(master=frame_left, text="autogenerate png", variable=autogenerate_png)
autogenerate_checkbox.pack(side=Tk.BOTTOM)

balloon = Pmw.Balloon(master=root);
balloon.bind(autogenerate_checkbox, "When checked, png images will be re-exported every time you click on an image.")

#}

#{ KEYPRESS catching and respective CALLBACKS
# callback for detecting keypresses

#{ LISTBOX manipulation

def listbox_move_up():

    index = int(listbox.curselection()[0])-1
    if index >= 0:
        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        reloadData(index, 1)

def listbox_move_down():

    index = int(listbox.curselection()[0])+1
    if index <= (listbox.size()-1):
        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        reloadData(index, 1)
#}

def on_key_event(event):

    # if event.char == 'q':
    #     button.invoke()

    if event.char == 'j':
        listbox_move_down()

    if event.char == 'k':
        listbox_move_up()

    if event.char == 'o':
        loadNewImages()

    if event.char == 'a':
        autogenerate_checkbox.toggle()

root.bind_all('<Key>', on_key_event)
#}

root.protocol("WM_DELETE_WINDOW", win_deleted)
root.mainloop()
print("Exitting")
sys.exit()
