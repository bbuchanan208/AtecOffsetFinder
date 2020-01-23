import os
from os.path import isfile, join
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.filedialog import askopenfile, asksaveasfile
import matplotlib.pyplot as plt
import pygame
import scipy.io.wavfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from statistics import mean
import numpy as np


class ConvertToWav:

    def __init__(self, mp4_file_loc, save_file_directory, unix=True):
        self.unix = unix
        self.mp4_file_loc = self._convert_string_to_unix_acceptable(mp4_file_loc)
        self.wav_file_name = self._convert_string_to_unix_acceptable(save_file_directory) + "temp.wav"

    def exe_ffmpeg_script(self):
        os.system(self._construct_console_script())
        return self._convert_to_reg_file_path(self.wav_file_name)

    def _construct_console_script(self):
        base = "./ffmpeg -i MP4_HERE -ar 16000 -ac 1 -t 4.5 FILE_OUTNAME"
        base = base.replace("MP4_HERE", self.mp4_file_loc)
        base = base.replace("FILE_OUTNAME", self.wav_file_name)
        return base

    def _convert_string_to_unix_acceptable(self, string_in):
        if self.unix is True:
            return str(string_in).replace(" ", "\ ")

    def _convert_to_reg_file_path(self, string_in):
        if self.unix:
            return str(string_in).replace("\ ", " ")


class OffsetFinder:

    def __init__(self, wav_file_loc, task_num=20, first_peak_user_input='auto'):
        self.rate, self.data = scipy.io.wavfile.read(wav_file_loc)
        self.task_num = task_num
        self.user_first_peak = None
        self._cleanse_first_peak(first_peak_user_input)
        self.first_peak_original_loc = None
        self.sec_peak_original_loc = None  # value was 11345
        self.third_peak_original_loc = None  # value was 12341
        self.fourth_peak_original_loc = None  # Value was 32299
        self._ref_wave_file_loc = None
        self._update_peaks_and_ref_wav_file()
        self.first_peak_input_vid = None
        self.sec_peak_input_vid = None
        self.third_peak_input_vid = None
        self.fourth_peak_input_vid = None
        self.peak_start_guesses = [10000, 21000, 39000, 55000]
        self.ms_offset = None

    def get_input_to_ref_vol_percent(self):
        input_max = abs(max(self.data, key=abs))
        ref_max = abs(max(self.get_original_vid_data(), key=abs))
        return float(round(ref_max / input_max, 3))

    def get_ref_wav_file_loc(self):
        return self._ref_wave_file_loc

    def _get_peaks_given_task_num(self, task_num):
        task_num = int(task_num)
        ten = [28450, 42848, 57718, 72327]
        eleven = [24298, 34285, 44260, 53419]
        twelve = [28450, 42848, 57718, 72327]
        thirteen = [28450, 42848, 57718, 72327]
        fourteen = [28450, 42848, 57718, 72327]
        fifteen = [28450, 42848, 57718, 72327]
        sixteen = [9829, 23453, 39037, 54203]
        seventeen = [5554, 19381, 34762, 49992]
        eighteen = [27840, 41464, 56963, 72475]
        nineteen = [15195, 29022, 44318, 59506]
        twenty = [9829, 23655, 38952, 54265]
        twentyOne = [9829, 23453, 38952, 54266]
        if task_num is 10:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/10.wav'
            return ten
        elif task_num is 11:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/11.wav'
            return eleven
        elif task_num is 12:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/12.wav'
            return twelve
        elif task_num is 13:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/13.wav'
            return thirteen
        elif task_num is 14:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/14.wav'
            return fourteen
        elif task_num is 15:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/15.wav'
            return fifteen
        elif task_num is 16:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/16.wav'
            return sixteen
        elif task_num is 17:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/17.wav'
            return seventeen
        elif task_num is 18:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/18.wav'
            return eighteen
        elif task_num is 19:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/19.wav'
            return nineteen
        elif task_num is 20:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/20.wav'
            return twenty
        elif task_num is 21:
            self._ref_wave_file_loc = 'AudioSourcesForSegments/21.wav'
            return twentyOne
        else:
            print("Task number: " + str(task_num))
            raise Exception("Task number is incompatible")

    def _update_peaks_and_ref_wav_file(self):
        peaks = self._get_peaks_given_task_num(self.task_num)
        self.first_peak_original_loc = peaks[0]
        self.sec_peak_original_loc = peaks[1]
        self.third_peak_original_loc = peaks[2]
        self.fourth_peak_original_loc = peaks[3]

    def _cleanse_first_peak(self, first_peak_user_input):
        acceptable_inputs = ['1', 'one', 1, '2', 'two', 2, '3', 'three', 3, 'go']
        if str(first_peak_user_input).lower() in acceptable_inputs:
            if str(first_peak_user_input).lower() in acceptable_inputs[0:3]:
                self.user_first_peak = 1
            elif str(first_peak_user_input).lower() in acceptable_inputs[3:6]:
                self.user_first_peak = 2
            elif str(first_peak_user_input).lower() in acceptable_inputs[6:9]:
                self.user_first_peak = 3
            else:
                self.user_first_peak = 4

    def _find_max_given_start(self, starting_index, duration=10000):
        current_max = 0
        max_loc = 0
        for current_index in range(starting_index, starting_index + duration):
            # if the video is higher quality, the data will contain tuples
            # comp = max(abs(data[e][0]), abs(data[e][1]))
            comp = abs(self.data[current_index])
            if comp > current_max:
                current_max = comp
                max_loc = current_index
        return max_loc

    def _find_and_fill_all_peaks(self):
        max_locations = []
        for starting_index in self.peak_start_guesses:
            max_locations.append(self._find_max_given_start(starting_index))
        self.first_peak_input_vid = max_locations[0]
        self.sec_peak_input_vid = max_locations[1]
        self.third_peak_input_vid = max_locations[2]
        self.fourth_peak_input_vid = max_locations[3]

    def auto_get_offset(self):
        self._find_and_fill_all_peaks()
        return self._get_offset_using_auto_approach()

    def user_input_get_offset(self):
        '''
        A negative offset means the original video should start first
        A positive offset means that the input video should start first
        :return:
        '''
        self.first_peak_input_vid = self._find_first_peak_location()
        original_peak_location = self._get_user_provided_first_peak_reference()
        frame_differance = self.first_peak_input_vid - original_peak_location
        # print("og ref peak" + str(original_peak_location))
        # print("vid rate" + str(self.rate))
        self.ms_offset = float(round(frame_differance / self.rate, 3))
        return self.ms_offset

    def _get_user_provided_first_peak_reference(self):
        if self.user_first_peak == 1:
            return self.first_peak_original_loc
        elif self.user_first_peak == 2:
            return self.sec_peak_original_loc
        elif self.user_first_peak == 3:
            return self.third_peak_original_loc
        elif self.user_first_peak == 4:
            return self.fourth_peak_original_loc
        else:
            raise Exception("self.user_first_peak was not recognized in _get_user_provided_first_peak_reference in "
                            "OffsetFinder class")

    def _get_offset_using_auto_approach(self):
        peaks = []
        peaks.append(self.first_peak_input_vid - self.first_peak_original_loc)
        peaks.append(self.sec_peak_input_vid - self.sec_peak_original_loc)
        peaks.append(self.third_peak_input_vid - self.third_peak_original_loc)
        peaks.append(self.fourth_peak_input_vid - self.fourth_peak_original_loc)
        # return (round(int(mean(peaks)) / self.rate, 3))
        self.ms_offset = float(round((mean(peaks)) / self.rate, 3))
        return self.ms_offset

    def show_graph(self):
        plt.plot(self.data[56000:60000])
        plt.show()

    def compare_graphs(self, ms_offset=0):
        temp_rate, original_ref_data = scipy.io.wavfile.read(self._ref_wave_file_loc)
        foo = plt.plot(original_ref_data, 'g,')  # markersize=2, color='green', linewidth=1, linestyle='dashed')
        foo.plot(self.shift_data_by_x_ms(ms_offset), ",")
        return foo

    def shift_data_by_x_ms(self, x):
        temp = []
        shift_amount = int(x * self.rate)
        if shift_amount >= 0.0:
            for index in range(len(self.data) - shift_amount):
                temp.append(self.data[index + shift_amount])
        else:
            for index in range(len(self.data)):
                if index + shift_amount >= 0:
                    data_index = index - shift_amount
                    if data_index < len(self.data):
                        temp.append(self.data[data_index])
        return temp

    def get_original_vid_data(self):
        temp_rate, original_ref_data = scipy.io.wavfile.read(self._ref_wave_file_loc)
        return original_ref_data

    def _get_start_stop_of_peaks(self):
        '''
        PRetty broke, don't use
        :return:

        smoothed_data = plt.plot(savgol_filter(self.data, 5, 3))
        smoothed_data = smoothed_data[0].get_ydata()
        data_mean = mean(smoothed_data)
        data_threshold = int(data_mean * 2)
        data_threshold = 5000
        #print("data t hold: " + str(data_threshold))
        inside_a_peak = False
        list_of_peak_locs = []
        start_peak_index = 0
        for index in range(len(smoothed_data)):
            if abs(smoothed_data[index]) > data_threshold:
                if inside_a_peak is False:
                    inside_a_peak = True
                    start_peak_index = index
            else:
                if inside_a_peak is True and abs(smoothed_data[index] < data_threshold):
                    inside_a_peak = False
                    list_of_peak_locs.append((start_peak_index, index))
        if list_of_peak_locs[-1][0] != start_peak_index:
            list_of_peak_locs.append((start_peak_index, len(smoothed_data) - 1))
        print(len(list_of_peak_locs))
        print(smoothed_data[8173:8200])
        return list_of_peak_locs
        '''

    def _peak_finding_using_local_maxes(self):
        '''
        Broken don't use
        :return:
        '''
        maxes = []
        top_maxes = []
        for i in range(0, len(self.data), 1000):
            maxes.append(max(self.data[i: i + 1000], key=abs))
        print(maxes)
        for i in range(0, 4):
            cur_max = max(maxes, key=abs)
            max_index = maxes.index(cur_max)
            top_maxes.append(max_index)
            maxes[max_index] = 0
            maxes = self._zero_out_space_surrounding_local_max(maxes, max_index)
        print(maxes)
        print(sorted(top_maxes))

    def _find_first_peak_location(self, debug=False):
        maxes = []
        first_peak_tuple = None
        for i in range(0, len(self.data), 1000):
            maxes.append(int(abs(max(self.data[i: i + 1000], key=abs))))
        min_intensity_thold = int(mean((sorted(maxes))[-5:]) / 2.3)
        starting_index = None
        for index in range(0, len(maxes)):
            if abs(maxes[index]) > min_intensity_thold:
                if starting_index is None:
                    starting_index = index * 1000
            else:
                if starting_index is not None:
                    first_peak_tuple = (starting_index, index * 1000)
                    break
        if first_peak_tuple is not None:
            if debug:
                print("first peak tuple")
                print(first_peak_tuple)
            return self._find_max_given_start(first_peak_tuple[0], duration=first_peak_tuple[1] - first_peak_tuple[0])
        else:
            Exception("_find_first_peak_location failed and caused this exception")

    def _zero_out_space_surrounding_local_max(self, max_list, index_of_max, num_of_entries_before=2,
                                              num_of_entries_after=4):
        max_list = self._zero_out_entries_after(max_list, index_of_max, num_of_entries_after)
        max_list = self._zero_out_entries_before(max_list, index_of_max, num_of_entries_before)
        return max_list

    def _zero_out_entries_after(self, max_list, index_of_max, num_entries_after):
        counter, starting_index_to_zero = 0, index_of_max + 1
        while counter < num_entries_after and starting_index_to_zero < len(max_list):
            max_list[starting_index_to_zero] = 0
            starting_index_to_zero += 1
            counter += 1
        return max_list

    def _zero_out_entries_before(self, max_list, index_of_max, num_entries_before):
        counter = 0
        start_index_to_zero = index_of_max - 1
        while counter < num_entries_before and start_index_to_zero >= 0:
            max_list[start_index_to_zero] = 0
            start_index_to_zero -= 1
            counter += 1
        return max_list


class gui:

    def __init__(self):
        self.gui_window = tk.Tk()
        self.gui_window.configure(background="light green")
        self.gui_window.title("Offset Finder")
        self.gui_window.geometry("960x800")
        self.constant_ms_addition = 0.050

        self.button_textbox_width = int(50)
        self.button_height = int(2)
        self.textbox_height = int(3)
        self.arrow_modifier = float(0.002)
        self.extensions = ['/10', '/11', '/12', '/13', '/14', '/15', '/16', '/17', '/18', '/19', '/20', '/21']

        self.radio_button_input_variable = IntVar()
        self.file_location = None
        self.file_directory = None
        self.file_loaded = False
        self.offset_finder_class = None
        self.offset = None
        self.manual_button_pressed = False
        self.first_word_pressed = False
        self._input_wave_file_loc = None
        self._ref_wave_file_loc = None
        self.canvas = None
        self.directory = None
        self.task_num = 10
        self.input_to_org_multiplier = 1.0
        self.fig = plt.figure()

        self.save_text_array = []

        pygame.mixer.init(frequency=16000,
                          buffer=10)  # The freqency must match the FFMPEG conversion and the buffer must be small otherwise lag with occur

        self._build_initial_display()

        self.gui_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.gui_window.mainloop()

    def show_graph(self, offset=0.0):
        if self.first_word_pressed is False:
            self.canvas = FigureCanvasTkAgg(master=self.gui_window, figure=self.fig)
            self.canvas.get_tk_widget().pack()
            self._build_post_graph_display()
            self._update_graph(offset)
            self._update_texthelper_with_message("Use the arrows and the Play Comparison Audio button to fine tune the "
                                                 "offset, you should only hear 'one, two, three, go' once. "
                                                 "Then press the confirm and reset button once the offset is found")
            self.first_word_pressed = True

    def _update_graph(self, offset, normalize=False):
        plt.clf()
        plt.plot(self.offset_finder_class.get_original_vid_data(), 'g,', label='green=reference video')
        if normalize:
            plt.plot([(e * self.input_to_org_multiplier) for e in
                      self.offset_finder_class.shift_data_by_x_ms(float(offset))], ',', label="blue=input video")
        else:
            plt.plot(self.offset_finder_class.shift_data_by_x_ms(float(offset)), ',', label="blue=input video")
        plt.gcf().canvas.draw()

    def _arrow_press(self, increment=0.005):
        self.offset = float(round(float(self.offset) + increment, 3))
        self._update_graph(self.offset)
        self._update_offset_display(self.offset)

    def _build_initial_display(self):
        self.file_selector_save_results_frame = Frame(self.gui_window)
        self.file_selector_save_results_frame.pack()
        self.file_selector_button = tk.Button(self.file_selector_save_results_frame, text='Select MP4 file',
                                              width=int(self.button_textbox_width / 3), height=self.button_height,
                                              command=lambda: self.load_file(), fg='red')
        self.file_selector_button.pack(side=LEFT)

        self.save_results_button = tk.Button(self.file_selector_save_results_frame, text='Save results to file',
                                             width=int(self.button_textbox_width / 3), height=self.button_height,
                                             command=lambda: self._save_file())
        self.save_results_button.pack(side=LEFT)

        self.load_folder = tk.Button(self.file_selector_save_results_frame, text='Load Folder',
                                     width=int(self.button_textbox_width / 3), height=self.button_height,
                                     command=lambda: self._load_folder())
        self.load_folder.pack(side=LEFT)

        self.radio_button_reset = tk.Button(self.file_selector_save_results_frame, text='Reset tasks',
                                            width=int(self.button_textbox_width / 4), height=self.button_height,
                                            command=lambda: self._radio_button_reset_function())
        self.radio_button_reset.pack(side=RIGHT)

        self.text_display_helper = tk.Text(self.gui_window, width=int(self.button_textbox_width + 10),
                                           height=self.textbox_height, wrap=WORD)
        self.text_display_helper.pack()

        self.radio_button_frame = Frame(self.gui_window)
        self.radio_button_frame.pack()
        self.r10 = Radiobutton(self.radio_button_frame, text="10", variable=self.radio_button_input_variable, value=10,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Ball Drop to the Beat - Slow"), fg='red')
        self.r10.pack(side=LEFT)
        self.r11 = Radiobutton(self.radio_button_frame, text="11", variable=self.radio_button_input_variable, value=11,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Ball Drop to the Beat - Fast"), fg='red')
        self.r11.pack(side=LEFT)
        self.r12 = Radiobutton(self.radio_button_frame, text="12", variable=self.radio_button_input_variable, value=12,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Red/Green Light - Slow"), fg='red')
        self.r12.pack(side=LEFT)
        self.r13 = Radiobutton(self.radio_button_frame, text="13", variable=self.radio_button_input_variable, value=13,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Red/Green Light - Fast"), fg='red')
        self.r13.pack(side=LEFT)
        self.r14 = Radiobutton(self.radio_button_frame, text="14", variable=self.radio_button_input_variable, value=14,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Red/Green/Yellow Light - Slow"), fg='red')
        self.r14.pack(side=LEFT)
        self.r15 = Radiobutton(self.radio_button_frame, text="15", variable=self.radio_button_input_variable, value=15,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Red/Green/Yellow Light - Fast"), fg='red')
        self.r15.pack(side=LEFT)
        self.r16 = Radiobutton(self.radio_button_frame, text="16", variable=self.radio_button_input_variable, value=16,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Traffic Lights - Slow"), fg='red')
        self.r16.pack(side=LEFT)
        self.r17 = Radiobutton(self.radio_button_frame, text="17", variable=self.radio_button_input_variable, value=17,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Traffic Lights - Fast"), fg='red')
        self.r17.pack(side=LEFT)
        self.r18 = Radiobutton(self.radio_button_frame, text="18", variable=self.radio_button_input_variable, value=18,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Traffic Lights - Yellow- Slow"), fg='red')
        self.r18.pack(side=LEFT)
        self.r19 = Radiobutton(self.radio_button_frame, text="19", variable=self.radio_button_input_variable, value=19,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Traffic Lights - Yellow- Fast"), fg='red')
        self.r19.pack(side=LEFT)
        self.r20 = Radiobutton(self.radio_button_frame, text="20", variable=self.radio_button_input_variable, value=20,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Sailor Step - Slow"), fg='red')
        self.r20.pack(side=LEFT)
        self.r21 = Radiobutton(self.radio_button_frame, text="21", variable=self.radio_button_input_variable, value=21,
                               command=lambda: self._update_texthelper_with_message(
                                   "You selected Sailor Step - Slow"), fg='red')
        self.r21.pack(side=LEFT)

        self._update_texthelper_with_message("Please select a file")
        self.auto_manual_frame = Frame(self.gui_window)
        self.auto_manual_frame.pack()
        # self.auto_button = tk.Button(self.auto_manual_frame, text='Automatic offset finder', width=int(self.button_textbox_width/2), height=self.button_height, command=lambda: self._get_offset_and_display_graph(auto=True))
        # self.auto_button.pack(side=LEFT)
        self.manual_button = tk.Button(self.auto_manual_frame, text='Manual offset finder',
                                       width=int(self.button_textbox_width / 2), height=self.button_height,
                                       command=lambda: self._build_manual_display(), fg='red')
        self.manual_button.pack(side=RIGHT)

        self.folder_offset_finder_button = tk.Button(self.auto_manual_frame, text='Folder offset finder',
                                                     width=int(self.button_textbox_width / 3),
                                                     height=self.button_height,
                                                     command=lambda: self._reset_GUI_and_get_next_video(), fg='red')
        self.folder_offset_finder_button.pack(side=RIGHT)

    def _set_radio_variable(self, var_in):
        self.radio_button_input_variable = int(var_in)

    def _radio_button_reset_function(self):
        if messagebox.askyesno("Reset Task Buttons", "Are you sure you want to reset the task buttons? "
                                                     "This should only be done when all buttons are green."):
            self.r10.config(fg='red')
            self.r11.config(fg='red')
            self.r12.config(fg='red')
            self.r13.config(fg='red')
            self.r14.config(fg='red')
            self.r15.config(fg='red')
            self.r16.config(fg='red')
            self.r17.config(fg='red')
            self.r18.config(fg='red')
            self.r19.config(fg='red')
            self.r20.config(fg='red')
            self.r20.config(fg='red')

    def _build_manual_display(self):
        if self.radio_button_input_variable.get() == 0:
            self._update_texthelper_with_message("Please select the task number")
        if self.file_loaded is False:
            self._update_texthelper_with_message("Please select a file")
        if self.manual_button_pressed is False and self.radio_button_input_variable.get() != 0 and self.file_loaded:
            self.manual_button_pressed = True
            self.manual_button.config(fg='green')
            self.play_input_audio_button = tk.Button(self.gui_window, text='Play input audio',
                                                     width=int(self.button_textbox_width), height=self.button_height,
                                                     command=lambda: self._play_original_audio())
            self.play_input_audio_button.pack()
            self.peak_selector_frame = Frame(self.gui_window)
            self.peak_selector_frame.pack()
            self.one_button = tk.Button(self.peak_selector_frame, text='1', width=int(self.button_textbox_width / 5),
                                        height=self.button_height, command=lambda: self._manual_button_selected(1))
            self.one_button.pack(side=LEFT)
            self.two_button = tk.Button(self.peak_selector_frame, text='2', width=int(self.button_textbox_width / 5),
                                        height=self.button_height, command=lambda: self._manual_button_selected(2))
            self.two_button.pack(side=LEFT)
            self.three_button = tk.Button(self.peak_selector_frame, text='3', width=int(self.button_textbox_width / 5),
                                          height=self.button_height, command=lambda: self._manual_button_selected(3))
            self.three_button.pack(side=LEFT)
            self.go_button = tk.Button(self.peak_selector_frame, text='Go', width=int(self.button_textbox_width / 5),
                                       height=self.button_height, command=lambda: self._manual_button_selected('go'))
            self.go_button.pack(side=LEFT)
            self.other_button = tk.Button(self.peak_selector_frame, text='Other',
                                          width=int(self.button_textbox_width / 5), height=self.button_height,
                                          command=lambda: self._manual_button_selected('auto'))
            self.other_button.pack(side=LEFT)
            self._update_texthelper_with_message("Using the buttons below,"
                                                 " select the first word you hear in the input audio.")

    def _build_post_graph_display(self):
        self.arrow_frame = Frame(self.gui_window)
        self.arrow_frame.pack()
        self.left_arrow = tk.Button(self.arrow_frame, text='<--', width=int(self.button_textbox_width / 4),
                                    height=self.button_height, command=lambda: self._arrow_press(0.005))
        self.left_arrow.pack(side=LEFT)
        self.offset_display = tk.Entry(self.arrow_frame, )
        self.offset_display.pack(side=LEFT)
        self.jump_offset = tk.Button(self.arrow_frame, text='Jump to offset', width=int(self.button_textbox_width / 4),
                                     height=self.button_height, command=lambda: self._jump_offset())
        self.jump_offset.pack(side=RIGHT)
        self.right_arrow = tk.Button(self.arrow_frame, text='-->', width=int(self.button_textbox_width / 4),
                                     height=self.button_height, command=lambda: self._arrow_press(-0.005))
        self.right_arrow.pack(side=RIGHT)
        self.play_comp_audio = tk.Button(self.gui_window, text='Play comparison audio',
                                         width=int(self.button_textbox_width), height=self.button_height,
                                         command=lambda: self._play_comparison_audio())
        self.play_comp_audio.pack()
        self.offset_frame = Frame(self.gui_window)
        self.offset_frame.pack()
        self.confirm_offset = tk.Button(self.offset_frame, text='Confirm offset & reset',
                                        width=int(self.button_textbox_width / 2), height=self.button_height,
                                        command=lambda: self._reset_GUI())
        self.confirm_offset.pack(side=LEFT)
        self.confirm_offset_next_vid = tk.Button(self.offset_frame, text='Confirm offset and get next video in folder',
                                                 width=int(self.button_textbox_width / 1.5), height=self.button_height,
                                                 command=lambda: self._reset_GUI_and_get_next_video())
        self.confirm_offset_next_vid.pack(side=RIGHT)

    def _jump_offset(self):
        try:
            float(self.offset_display.get())
            if abs(float(self.offset_display.get())) < 3.00:
                self.offset = float(round(float(self.offset_display.get()), 3))
                self._update_graph(self.offset)
                self._update_offset_display(self.offset)
        except:
            pass

    def _load_folder(self):
        self.directory = filedialog.askdirectory()
        # Assume that the first task will be task 10
        self.task_num = 10
        if not self._all_video_files_are_present():
            messagebox.showinfo("Error", "The folder chosen is incorrect")
        else:
            self.load_folder.config(fg='green')
            self._auto_load_file(self._get_file_loc_based_on_directory_and_task_num())
            self.radio_button_input_variable.set(10)
            self._build_manual_display()

    def _auto_load_file(self, potenial_file):
        if self._input_wave_file_loc is not None:
            self._delete_wave_file()
        if potenial_file is not None:
            self.file_loaded = True
            self.file_location = potenial_file
            self._update_texthelper_with_message("Selected file " + str(self.file_location))
            self._update_save_file_directory(potenial_file)
            self._input_wave_file_loc = ConvertToWav(self.file_location, self.file_directory).exe_ffmpeg_script()
            self.file_selector_button.config(fg='green')

    def _get_video_inside_folder(self, directory):
        onlyfiles = [f for f in os.listdir(directory) if isfile(join(directory, f))]
        for possible_mp4 in onlyfiles:
            if str(possible_mp4[-4:]).lower() == '.mp4':
                return str(possible_mp4)
        return False

    def _all_video_files_are_present(self):
        for ex in self.extensions:
            if not os.path.isdir(self.directory + ex) or not (self._get_video_inside_folder(self.directory + ex)):
                return False
        return True

    def _play_comparison_audio(self, debug=False):
        input_volume = 100.0
        ref_volume = (100.0 / self.input_to_org_multiplier) * 10
        if debug:
            print("Input, Ref")
            print(input_volume, ref_volume)
        if float(self.offset) >= 0.0:
            pygame.mixer.Channel(0).set_volume(input_volume)
            pygame.mixer.Channel(1).set_volume(ref_volume)
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(self._input_wave_file_loc))
            time.sleep(float(self.offset))
            pygame.mixer.Channel(1).play(pygame.mixer.Sound(self._ref_wave_file_loc))
        else:
            pygame.mixer.Channel(0).set_volume(ref_volume)
            pygame.mixer.Channel(1).set_volume(input_volume)
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(self._ref_wave_file_loc))
            time.sleep(float(self.offset * -1))
            pygame.mixer.Channel(1).play(pygame.mixer.Sound(self._input_wave_file_loc))

    def _play_original_audio(self):
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(self._input_wave_file_loc))

    def load_file(self, debug=False):
        if self._input_wave_file_loc is not None:
            self._delete_wave_file()
        if debug is False:
            filename = askopenfile(filetypes=(("MP4 files", "*.mp4"),
                                              ("All files", "*.*")), initialdir=(os.path.expanduser('~/')))
        else:
            filename = '/Users/benjaminbuchanan/sub5v2_test.mp4'
            raise Exception('Check line above, update filename and delete this exception')
        if filename is not None:
            self.file_loaded = True
            if debug:
                self.file_location = '/Users/benjaminbuchanan/sub5v2_test.mp4'
                raise Exception('Check line above, update filename and delete this exception')
            else:
                self.file_location = filename.name
            self._update_texthelper_with_message("Selected file " + str(self.file_location))
            self._update_save_file_directory(self.file_location)
            self._input_wave_file_loc = ConvertToWav(self.file_location, self.file_directory).exe_ffmpeg_script()
            self.file_selector_button.config(fg='green')

    def _manual_button_selected(self, button_selected):
        self.offset_finder_class = OffsetFinder(self._input_wave_file_loc,
                                                task_num=self.radio_button_input_variable.get(),
                                                first_peak_user_input=button_selected)
        self._get_offset_and_display_graph(manual=True)
        self._ref_wave_file_loc = self.offset_finder_class.get_ref_wav_file_loc()

    def _update_texthelper_with_message(self, message):
        self.text_display_helper.delete("1.0", tk.END)
        self.text_display_helper.insert(tk.END, message)

    def _update_offset_display(self, offset_to_be_displayed):
        self.offset_display.delete(0, tk.END)
        self.offset_display.insert(tk.END,
                                   str(round(float(offset_to_be_displayed) + float(self.constant_ms_addition), 3)))

    def _update_save_file_directory(self, filename):
        self.file_directory = filename[:filename.rfind("/") + 1]

    def _get_offset_and_display_graph(self, auto=False, manual=False):
        if self.file_loaded:
            if auto:
                self.offset = self.offset_finder_class.auto_get_offset()
            elif manual:
                self.offset = self.offset_finder_class.user_input_get_offset()
            else:
                raise Exception('Offset selection in _get_offset_and_display_graph not selected')
            self.input_to_org_multiplier = self.offset_finder_class.get_input_to_ref_vol_percent()
            self._update_texthelper_with_message(str(self.offset))
            self.show_graph(offset=float(self.offset))
            self._update_offset_display(str(self.offset))
        else:
            raise Exception("File not loaded")

    def _save_file(self):
        # print(self.save_text_array)
        for e in self.save_text_array:
            print(e)
        '''
        f = asksaveasfile(mode='w', defaultextension=".txt")
        print(f.name)
        if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        self._build_text_files(f.name, self.save_text_array)
        '''

    def _build_text_files(self, text_file_path, list_in):
        file_object = open(text_file_path, "w+")
        for e in list_in:
            file_object.write(e + "\n")
        file_object.close()

    def _get_file_loc_based_on_directory_and_task_num(self):
        try:
            extension = self.extensions[int(self.task_num) - 10]
            new_diretory = str(self.directory) + str(extension)
            return new_diretory + '/' + self._get_video_inside_folder(new_diretory)
        except:
            Exception("Task number is invalid")

    def on_closing(self):
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        self._delete_wave_file()
        self.gui_window.destroy()
        self.gui_window.quit()

    def _delete_wave_file(self):
        if self._input_wave_file_loc is not None:
            try:
                os.remove(self._input_wave_file_loc)
            except Exception as e:
                print(e)

    def _get_video_name(self):
        return self.file_location[int(self.file_location.rfind("/") + 1):]

    def _color_radio_button(self):
        if self.radio_button_input_variable.get() == 10:
            self.r10.config(fg='green')
        elif self.radio_button_input_variable.get() == 11:
            self.r11.config(fg='green')
        elif self.radio_button_input_variable.get() == 12:
            self.r12.config(fg='green')
        elif self.radio_button_input_variable.get() == 13:
            self.r13.config(fg='green')
        elif self.radio_button_input_variable.get() == 14:
            self.r14.config(fg='green')
        elif self.radio_button_input_variable.get() == 15:
            self.r15.config(fg='green')
        elif self.radio_button_input_variable.get() == 16:
            self.r16.config(fg='green')
        elif self.radio_button_input_variable.get() == 17:
            self.r17.config(fg='green')
        elif self.radio_button_input_variable.get() == 18:
            self.r18.config(fg='green')
        elif self.radio_button_input_variable.get() == 19:
            self.r19.config(fg='green')
        elif self.radio_button_input_variable.get() == 20:
            self.r20.config(fg='green')
        elif self.radio_button_input_variable.get() == 21:
            self.r21.config(fg='green')
        else:
            Exception('Tried to reset a radio button that does not exist')

    def _reset_GUI_and_get_next_video(self):
        print("Here")

        self.save_text_array.append(str(self._get_video_name()) + " " +
                                    str(round(self.offset + self.constant_ms_addition, 3)) +
                                    " Task Number:" + str(self.radio_button_input_variable.get()))

        # Delete the temp wave file
        self._delete_wave_file()

        # destroy the buttons
        self.arrow_frame.destroy()
        self.left_arrow.destroy()
        self.offset_display.destroy()
        self.right_arrow.destroy()
        self.play_comp_audio.destroy()
        self.offset_frame.destroy()
        self.canvas.get_tk_widget().destroy()
        self.play_input_audio_button.destroy()
        self.peak_selector_frame.destroy()
        self.confirm_offset_next_vid.destroy()

        # Update the text helper display
        # self._update_texthelper_with_message("Please select an audio file or choose the save results button")

        # Reset the class init variables
        self.file_location = None
        self.file_loaded = False
        self.offset_finder_class = None
        self.offset = None
        self.manual_button_pressed = False
        self.first_word_pressed = False
        self._input_wave_file_loc = None
        self.canvas = None
        self.input_to_org_multiplier = None
        self.fig = plt.figure()
        self._color_radio_button()

        self._load_next_video()
        self._build_manual_display()

    def _load_next_video(self):
        self.radio_button_input_variable.set(int(self.radio_button_input_variable.get() + 1))
        self.task_num += 1
        new_file_loc = self._get_file_loc_based_on_directory_and_task_num()
        self._auto_load_file(new_file_loc)

    def _reset_GUI(self):
        self.save_text_array.append(str(self._get_video_name()) + " " +
                                    str(round(self.offset + self.constant_ms_addition, 3)) +
                                    " Task Number:" + str(self.radio_button_input_variable.get()))

        # Delete the temp wave file
        self._delete_wave_file()

        # destroy the buttons
        self.arrow_frame.destroy()
        self.left_arrow.destroy()
        self.offset_display.destroy()
        self.right_arrow.destroy()
        self.play_comp_audio.destroy()
        self.offset_frame.destroy()
        self.canvas.get_tk_widget().destroy()
        self.play_input_audio_button.destroy()
        self.peak_selector_frame.destroy()
        self.confirm_offset_next_vid.destroy()

        # Update the text helper display
        self._update_texthelper_with_message("Please select an audio file or choose the save results button")

        # Reset the class init variables
        self.file_location = None
        self.file_directory = None
        self.file_loaded = False
        self.offset_finder_class = None
        self.offset = None
        self.manual_button_pressed = False
        self.first_word_pressed = False
        self._input_wave_file_loc = None
        self.canvas = None
        self.input_to_org_multiplier = None
        self.fig = plt.figure()
        self._color_radio_button()
        self.radio_button_input_variable.set(0)

        # reset the colors
        self.file_selector_button.config(fg='red')
        self.manual_button.config(fg='red')


def array_diff(a1, a2, current_min):
    if len(a1) != len(a2):
        Exception('Lengths of arrays are not the same')
    total = 0
    for index in range(len(a1)):
        total += abs(a1[index] - a2[index])
        if total > current_min:
            return total
    return total


def shift_array(a_in, shift_amount):
    new_array = []
    if shift_amount >= 0:
        for e in range(shift_amount):
            new_array.append(0)
        for e in range(len(a_in) - shift_amount):
            new_array.append(a_in[e])
    else:
        for e in range(abs(shift_amount), len(a_in)):
            new_array.append(a_in[e])
        while len(new_array) < len(a_in):
            new_array.append(0)
    return new_array


def find_opt_shift_amount(a_in, b_in, range_start, range_stop, step_amount):
    if len(a_in) != len(b_in):
        Exception("Input array vary in size")
    min_shift_amount = 0
    min_shift_differnce = array_diff(a_in, b_in)
    for shift_amount in range(range_start, range_stop, step_amount):
        print(shift_amount)
        new_shift_difference = array_diff(a_in, shift_array(b_in, shift_amount))
        if new_shift_difference < min_shift_differnce:
            print("new shift diff found")
            min_shift_differnce = new_shift_difference
            min_shift_amount = shift_amount
    return min_shift_amount


def alt_find_opt_fit_location(long_input_array, array_to_find, range_start, range_stop, step_amount):
    optimal_index = 0
    min_difference_value = 99999999999999999999999
    seach_array_len = len(array_to_find)
    if range_stop > len(long_input_array) - len(array_to_find):
        range_stop = len(long_input_array) - len(array_to_find)
    for start_index in range(range_start, range_stop, step_amount):
        frame_diff_val = array_diff(array_to_find, long_input_array[start_index: start_index + seach_array_len],
                                    min_difference_value)
        if frame_diff_val < min_difference_value:
            print(start_index, frame_diff_val)
            min_difference_value = frame_diff_val
            optimal_index = start_index
    return optimal_index


def efficient_find_shift_amount(a, b):
    _1000_shift_result = find_opt_shift_amount(a, b, int(-1 * (len(a) / 4)), int(1 * (len(a) / 4)), 1000)
    print("1000 SR:" + str(_1000_shift_result))
    _100_shift_result = find_opt_shift_amount(a, b, _1000_shift_result - 1000, _1000_shift_result + 1000, 100)
    print("100 SR:" + str(_100_shift_result))
    _10_shift_result = find_opt_shift_amount(a, b, _100_shift_result - 100, _100_shift_result + 100, 10)
    print("final")
    return _10_shift_result


def normalize(array_in):
    a_max = max(array_in)
    a_min = min(array_in)
    print(a_max, a_min)
    r_l = []
    for e in array_in:
        r_l.append((e - a_min) / (a_max - a_min))
    return r_l


def get_array_of_peaks(non_fft_array_in, real=True, interval_size=400):
    fft_array = np.fft.fft(non_fft_array_in)
    starting_index = 0
    return_list = []
    while starting_index + interval_size < len(fft_array) - 1:
        ending_index = starting_index + interval_size
        if real:
            return_list.append(int(round(max(fft_array[starting_index:ending_index].real ** 2), 0)))
        starting_index += interval_size
    return return_list


def get_list_difference(og_list, input_list, interval_size=400):
    difference_list = []
    for inde in range(len(og_list)):
        difference_list.append(given_value_find_lowest_difference((inde, og_list[inde]), input_list))
    return difference_list


def given_value_find_lowest_difference(value_tuple, list_in):
    min = (0, 9999999999999999999999)
    for e in range(len(list_in)):
        if abs(value_tuple[1] - list_in[e]) < min[1]:
            min = (e, abs(value_tuple[1] - list_in[e]))
    return min[0]


if __name__ == "__main__":
    gui()
