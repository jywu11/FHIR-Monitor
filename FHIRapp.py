import tkinter as tk
import tkinter.ttk as ttk
from time import sleep
import threading
import requests
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from datetime import datetime
import matplotlib.animation as animation
import random



class Publisher(ABC):
    def __init__(self):
        """
        Create a set of subscribers(observers) who want to be notified on data change
        """
        self.observers = set()

    def attach(self, observer):
        """
        register an observer(a Patient object) to be notified
        :param observer: object to add to the Publishers set to be notified
        :return: none
        """
        self.observers.add(observer)

    def detach(self, observer):
        """
        deregister observer from being notified
        :param observer: object to remove from the Publisher set
        :return:none
        """
        self.observers.discard(observer)

    def notify_observers(self):
        """
        Traverse the Publishers set notifying all observer objects that they must update.
        :return:none
        """
        for observer in self.observers:
            observer.update()


class Observer(ABC):
    @abstractmethod
    def update(self):
        """
        Once the subject has notified the observers that they should be updated, this method will execute.
        :return:none
        """
        pass


class Model:
    """
    Class responsible for the management of business logic within the system
    """
    def return_patient(self, patient_values):
        """
        Takes in some values found for a patient, and returns a new Patient object with those values attached to the
        Patient
        :param patient_values: values to be assigned to a new Patient object
        :return: A Patient object with the given values attached
        """
        patient_name = patient_values[0]
        patient_total_chol = patient_values[1][0]
        patient_time = patient_values[1][1]
        patient_systolic = patient_values[1][2]
        patient_diastolic = patient_values[1][3]
        patient_blood_pressure_time = patient_values[1][4]
        patient_city = patient_values[1][5]
        patient_state = patient_values[1][6]
        patient_country = patient_values[1][7]
        patient_id = patient_values[1][8]
        patient_gender = patient_values[1][9]
        patient_birth_date = patient_values[1][10]
        patient = Patient(patient_name, patient_total_chol, patient_systolic, patient_diastolic, patient_blood_pressure_time, patient_time, patient_city, patient_state, patient_country,
                          patient_id, patient_gender, patient_birth_date)
        return patient

    def chol_average(self, patient_dict):
        """
        Given a dictionary, will traverse the patients inside and calculate the corresponding average cholesterol
        :param patient_dict: dictionary containing patients
        :return: float, average of all cholesterol's
        """
        chol_values = []

        for patient_id in patient_dict:
            if patient_dict[patient_id]._total_chol != '-':
                chol_values.append(float(patient_dict[patient_id]._total_chol))

        if chol_values:
            return sum(chol_values) / len(chol_values)
        else:
            return 0.0


class View:
    """
    Class that manages the retrieval and display of information for the application.
    """
    def __init__(self, root, model):
        """
        Initiate the View objects canvas, frame, treeviews, buttons, labels and entries
        :param root: tk object describing the application context to place onto
        :param model: model object necessary to calculate variables
        """
        self.model = model
        self.root = root
        self.canvas = tk.Canvas(self.root, height=600, width=900)
        self.canvas.pack()

        # used to map the font colours to the treeview entries
        self.style = ttk.Style()
        self.frame = tk.Frame(self.root)
        self.frame.place(relheight=0.65, relwidth=0.9, relx=0.03, rely=0.03, anchor="nw")

        self.patient_list = PatientList(self.frame)
        self.monitored_patients = MonitoredList(self.frame)

        self.add_patient_to_monitor = tk.Button(self.frame, text="Add Patient To Monitor")
        self.add_patient_cholesterol_to_monitor = tk.Button(self.frame, text="Add Patient Cholesterol To Monitor")
        self.add_patient_blood_pressure_to_monitor = tk.Button(self.frame, text="Add Patient Blood Pressure To Monitor")
        self.remove_patient = tk.Button(self.frame, text="Remove Patient From Monitor")
        self.remove_patient_cholesterol = tk.Button(self.frame, text="Remove Patient Cholesterol From Monitor")
        self.remove_patient_blood_pressure = tk.Button(self.frame, text="Remove Patient Blood Pressure From Monitor")
        self.graph_patient = tk.Button(self.frame, text="Graph Monitored Patients")
        self.update_period_entry = tk.Entry(self.frame, width=50, font=24)
        self.id_button = tk.Button(self.frame, text="Retrieve Patient List (Enter ID)")
        self.update_button = tk.Button(self.frame, text="Set Update Period (sec)")
        self.systolic_bp_entry = tk.Entry(self.frame, width=50, font=24)
        self.systolic_bp_button = tk.Button(self.frame, text="Set X (Systolic BP)")
        self.diastolic_bp_entry = tk.Entry(self.frame, width=50, font=24)
        self.diastolic_bp_button = tk.Button(self.frame, text="Set Y (Diastolic BP)")
        self.id_entry = tk.Entry(self.frame, width=50, font=24)
        self.patient_info_title_label = tk.Label(self.root, anchor="w", padx=2, text="Patient Information:")
        self.patient_name_label = tk.Label(self.root, anchor="w", padx=2, text="")
        self.patient_gender_label = tk.Label(self.root, anchor="w", padx=2, text="")
        self.patient_address_label = tk.Label(self.root, anchor="w", padx=2, text="")

        self.id_entry.place(relheight=0.05, relwidth=0.325)
        self.id_button.place(relheight=0.05, relwidth=0.325, relx=0.33)
        self.update_period_entry.place(relheight=0.05, relwidth=0.325, rely=0.05)
        self.update_button.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.05)
        self.systolic_bp_entry.place(relheight=0.05, relwidth=0.325, rely=0.1)
        self.systolic_bp_button.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.1)
        self.diastolic_bp_entry.place(relheight=0.05, relwidth=0.325, rely=0.15)
        self.diastolic_bp_button.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.15)
        self.add_patient_cholesterol_to_monitor.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.37, anchor="w")
        self.add_patient_blood_pressure_to_monitor.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.25,
                                                         anchor="w")
        self.add_patient_to_monitor.place(relheight=0.05, relwidth=0.325, relx=0.0, rely=0.25, anchor="w")
        self.remove_patient.place(relheight=0.05, relwidth=0.325, relx=0, rely=0.31, anchor="w")
        self.remove_patient_cholesterol.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.43, anchor="w")
        self.remove_patient_blood_pressure.place(relheight=0.05, relwidth=0.325, relx=0.33, rely=0.31, anchor="w")
        self.graph_patient.place(relheight=0.05, relwidth=0.325, relx=0.66, rely=0.25, anchor="w")
        self.patient_info_title_label.place(relheight=0.03, relwidth=0.5, relx=0.325, rely=0.8, anchor="w")
        self.patient_name_label.place(relheight=0.03, relwidth=0.5, relx=0.48, rely=0.77, anchor="w")
        self.patient_gender_label.place(relheight=0.03, relwidth=0.5, relx=0.48, rely=0.8, anchor="w")
        self.patient_address_label.place(relheight=0.03, relwidth=0.5, relx=0.48, rely=0.83, anchor="w")

    def get_patient_all(self):
        """
        get patient selected from the list of all patients, and pass patient values back to controller
        :return: tuple of the patients name, values and item number within the treeview
        """
        item = self.patient_list.patient_tree.selection()
        patient_values = None
        if len(item) is not 0:
            item = item[0]
            patient_values = (
                self.patient_list.patient_tree.item(item, "text"), self.patient_list.patient_tree.item(item, "values"),
                item)
        return patient_values

    def change_font_colour(self, option):
        """
        Change the font colour of particular entries with a specific identifier specified by the option argument
        :param option: foreground or background tag
        :return: list of objects for the style object to map colours to
        """
        # tkinter font colour changing for treeview is a known bug: https://core.tcl-lang.org/tk/info/509cafafae
        # Workaround through the code provided in the above link. Also: https://bugs.python.org/issue36468
        return [item for item in self.style.map('Treeview', query_opt=option) if
                item[:2] != ('!disabled', '!selected')]

    def create_graph(self):
        # """
        # Create a bar graph from the monitored patients, using their blood pressure as the Y and names as the X axis
        # :return: none
        # """

        # Resetting plot if already exists
        while(True):
            self.root.update_idletasks()
            self.root.update()

            plt.axes().clear()
            patient_name_axis = []
            patient_chol_axis = []

            ## Retrieve Data from Monitored Patient List
            for item in self.monitored_patients.patient_tree.get_children():
                # search through all items in the monitor list, add the cholesterol values to the chol axis array.
                patient_values = (self.monitored_patients.patient_tree.item(item, "text"),
                                  self.monitored_patients.patient_tree.item(item, "values"), item)
                patient = self.model.return_patient(patient_values)
                if patient._total_chol != '-':
                    monitored_patient_names = (self.monitored_patients.patient_tree.item(item, "text"))
                    patient_name_axis.append(monitored_patient_names)

                    ## Add Data into Y-Axis Array
                    patient_chol_axis.append(float(patient._total_chol))

            ## Add Data into X-Axis Array
            graph_x_axis_patients = patient_name_axis

            x_pos = [i for i, _ in enumerate(graph_x_axis_patients)]

            plt.ion()

            plt.bar(x_pos, patient_chol_axis, color='green')

            ## Add the values on top of each bar.
            for index, data in enumerate(patient_chol_axis):
                plt.text(x=index, y=data + 1, s=f"{data}", fontdict=dict(fontsize=8), va='center',ha='center')

            plt.xlabel("Patient Names")
            plt.ylabel("Cholesterol (mg/dL)")
            plt.title("Monitored Patients Cholesterol Level")
            plt.rc('font', size=12)
            plt.xticks(x_pos, graph_x_axis_patients,fontsize=10,rotation=85)

            plt.tight_layout()
            plt.draw()
            plt.pause(0.1)


    def add_monitor(self, systolic_limit, diastolic_limit, cholestrol, bp):
        """
        Add a patient to the monitor treeview
        :param patient_id: the specified patient id to add to the monitor treeview
        :return: none
        """
        patient_values = self.get_patient_all()
        if patient_values is not None:
            patient = self.model.return_patient(patient_values)
            # print(patient._name)
            # add to monitor patient list if not there already
            if patient._id not in self.monitored_patients.patient_dict:
                self.monitored_patients.patient_dict[patient._id] = patient

                tag_above = "above"
                tag_below = "below"
                avg_chol = self.model.chol_average(self.monitored_patients.patient_dict)
                # insert the patient into the monitor list
                if (cholestrol == True) and (bp == True):
                    self.monitored_patients.patient_tree.insert("", "end", text=patient._name, values=(patient._total_chol,
                                                                                                       patient._last_update,
                                                                                                       patient._systolic,
                                                                                                       patient._diastolic,
                                                                                                       patient._blood_pressure_time,
                                                                                                  patient._city,
                                                                                                  patient._state,
                                                                                                  patient._country,
                                                                                                  patient._id,
                                                                                                  patient._gender,
                                                                                                  patient._birth_date))
                elif (cholestrol == True) and (bp == False):
                    self.monitored_patients.patient_tree.insert("", "end", text=patient._name, values=(patient._total_chol,
                                                                                                       patient._last_update,
                                                                                                       '-',
                                                                                                       '-',
                                                                                                       '-',
                                                                                                  patient._city,
                                                                                                  patient._state,
                                                                                                  patient._country,
                                                                                                  patient._id,
                                                                                                  patient._gender,
                                                                                                  patient._birth_date))
                elif (cholestrol == False) and (bp == True):
                    self.monitored_patients.patient_tree.insert("", "end", text=patient._name, values=('-',
                                                                                                       '-',
                                                                                                       patient._systolic,
                                                                                                       patient._diastolic,
                                                                                                       patient._blood_pressure_time,
                                                                                                  patient._city,
                                                                                                  patient._state,
                                                                                                  patient._country,
                                                                                                  patient._id,
                                                                                                  patient._gender,
                                                                                                  patient._birth_date))
                # check which entries left in the monitored patient list have above average cholesterol and change their
                # colour based on that
                self.check_children_chol(systolic_limit, diastolic_limit, avg_chol, tag_above, tag_below)
                # process the colours assigned to the tags
                self.style.map("Treeview", foreground=self.change_font_colour("foreground"))
            else:

                # Create list of 'id's
                list_of_entries_in_tree_view = self.monitored_patients.patient_tree.get_children()
                item = None
                for each in list_of_entries_in_tree_view:
                    patient_id = self.monitored_patients.patient_tree.item(each, "values")[8]
                    if patient._id == patient_id:
                        item = each
                        break

                patient_values = list(self.monitored_patients.patient_tree.item(item, "values"))

                if (cholestrol == False) and (bp == True):
                    patient_values[2] = patient._systolic
                    patient_values[3] = patient._diastolic
                    patient_values[4] = patient._blood_pressure_time

                    self.monitored_patients.patient_tree.item(item, values=tuple(patient_values))

                elif (cholestrol == True) and (bp == False):
                    patient_values[0] = patient._total_chol
                    patient_values[1] = patient._last_update
                    self.monitored_patients.patient_tree.item(item, values=tuple(patient_values))

                tag_above = "above"
                tag_below = "below"
                if len(self.monitored_patients.patient_dict) >= 1:
                    # only need to change font colour if there are patients in the monitor list.
                    # calculate new cholesterol average now that an item has been popped from the dictionary
                    avg_chol = self.model.chol_average(self.monitored_patients.patient_dict)
                    # check which entries left in the monitored patient list have above average cholesterol and change their
                    # colour based on that
                    self.check_children_chol(systolic_limit, diastolic_limit, avg_chol, tag_above, tag_below)
                    # process the colours assigned to the tags
                    self.style.map("Treeview", foreground=self.change_font_colour("foreground"))

    def remove_specific_monitor(self, systolic_limit, diastolic_limit, cholestrol, bp):

        if len(self.monitored_patients.patient_tree.selection()) > 0:
            # check if an item has been selected
            item = self.monitored_patients.patient_tree.selection()[0]

            patient_values = list(self.monitored_patients.patient_tree.item(item, "values"))

            if (cholestrol == True) and (bp == False):
                patient_values[2] = '-'
                patient_values[3] = '-'
                patient_values[4] = '-'

                self.monitored_patients.patient_tree.item(item, values=tuple(patient_values))

            elif (cholestrol == False) and (bp == True):
                patient_values[0] = '-'
                patient_values[1] = '-'
                self.monitored_patients.patient_tree.item(item, values=tuple(patient_values))

            tag_above = "above"
            tag_below = "below"
            if len(self.monitored_patients.patient_dict) >= 1:
                # only need to change font colour if there are patients in the monitor list.
                # calculate new cholesterol average now that an item has been popped from the dictionary
                avg_chol = self.model.chol_average(self.monitored_patients.patient_dict)
                # check which entries left in the monitored patient list have above average cholesterol and change their
                # colour based on that
                self.check_children_chol(systolic_limit, diastolic_limit, avg_chol, tag_above, tag_below)
                # process the colours assigned to the tags
                self.style.map("Treeview", foreground=self.change_font_colour("foreground"))

    def remove_monitor(self, systolic_limit, diastolic_limit):
        """
        Remove a specific patient from the monitor list.
        :return: none
        """
        # remove patient from the monitored patient list, not destroying any patient objects in the patient_list,
        # just the treeview entry
        if len(self.monitored_patients.patient_tree.selection()) > 0:
            # check if an item has been selected
            item = self.monitored_patients.patient_tree.selection()[0]
            patient_id = self.monitored_patients.patient_tree.item(item, "values")[8]

            self.monitored_patients.patient_tree.delete(item)
            self.monitored_patients.patient_dict.pop(patient_id)
            # tags for above avg cholesterol and below avg
            tag_above = "above"
            tag_below = "below"
            if len(self.monitored_patients.patient_dict) >= 1:
                # only need to change font colour if there are patients in the monitor list.
                # calculate new cholesterol average now that an item has been popped from the dictionary
                avg_chol = self.model.chol_average(self.monitored_patients.patient_dict)
                # check which entries left in the monitored patient list have above average cholesterol and change their
                # colour based on that
                self.check_children_chol(systolic_limit, diastolic_limit, avg_chol, tag_above, tag_below)
                # process the colours assigned to the tags
                self.style.map("Treeview", foreground=self.change_font_colour("foreground"))

    def check_children_chol(self, systolic_limit, diastolic_limit, avg_chol, tag_above, tag_below):
        """
        Traverse through the monitored patient list, checking if the cholesterol value attached to the patient object
        is above the calculated average of all patients in the monitor treeview
        :param avg_chol: the average cholesterol of all patients in the monitor treeview
        :param tag_above: tag used to denote if a patient has above the average cholesterol in the treeview
        :param tag_below: tag used to denote if a patient has below the average cholesterol in the treeview
        :param systolic_limit: tag used to denote if a patient has below the average cholesterol in the treeview
        :param diastolic_limit: tag used to denote if a patient has below the average cholesterol in the treeview


        :return: none
        """

        for item in self.monitored_patients.patient_tree.get_children():

            patient_values = (self.monitored_patients.patient_tree.item(item, "text"),
                              self.monitored_patients.patient_tree.item(item, "values"), item)
            patient = self.model.return_patient(patient_values)


            #Perform the Cholesterol Checks and BP Checks, change color accordingly
            #Show red foreground if patient's total chol above avg chol
            #Show Light Salmon background if either patient systolic or diastolic above set parameters

            self.monitored_patients.patient_tree.tag_configure(tag_below, foreground='black')

            if patient._systolic == '-':
                self.monitored_patients.patient_tree.item(item, tags=tag_below)
                self.monitored_patients.patient_tree.tag_configure(tag_below, foreground='black')
            else:
                if systolic_limit and diastolic_limit:
                    if int(patient._systolic) > systolic_limit or int(patient._diastolic) > diastolic_limit:
                        self.monitored_patients.patient_tree.item(item, tags=tag_above)
                        self.monitored_patients.patient_tree.tag_configure(tag_above,background="light salmon", foreground="black")
                    else:
                        self.monitored_patients.patient_tree.item(item, tags=tag_below)
                        self.monitored_patients.patient_tree.tag_configure(tag_below, foreground='black')

            # go through the elements in the monitor list, checking if their cholesterol value is higher than the average
            # calculated for the monitor list

            if patient._total_chol == '-':
                self.monitored_patients.patient_tree.item(item, tags=tag_below)
                self.monitored_patients.patient_tree.tag_configure(tag_below, foreground='black')
            else:
                if float(patient._total_chol) > avg_chol:
                    self.monitored_patients.patient_tree.item(item, tags=tag_above)
                    self.monitored_patients.patient_tree.tag_configure(tag_above, foreground='red')
                else:
                    self.monitored_patients.patient_tree.item(item, tags=tag_below)
                    self.monitored_patients.patient_tree.tag_configure(tag_below, foreground='black')


    def insert_patients(self):
        """
        Insert patients into the patient_list treeview, that is, the treeview that will display all patients found from
        the server call that have a total cholesterol value reported for them.
        :return: none
        """
        # runs after completion of server contacting, inserts all patients found on server into the
        # patient_list treeview
        self.clear_tree(self.patient_list.patient_tree)
        self.clear_tree(self.monitored_patients.patient_tree)
        self.monitored_patients.patient_dict = {}

        for patient_id in self.patient_list.patient_dict:
            patient = self.patient_list.patient_dict[patient_id]
            self.patient_list.patient_tree.insert("", "end", text=patient._name, values=(patient._total_chol,
                                                                                         patient._last_update,
                                                                                         patient._systolic,
                                                                                         patient._diastolic,
                                                                                         patient._blood_pressure_time,
                                                                                    patient._city, patient._state,
                                                                                    patient._country, patient._id,
                                                                                    patient._gender,
                                                                                    patient._birth_date))

    def clear_tree(self, treeview):
        """
        Delete all children within the specified treeview
        :param treeview: the treeview for which to clear all children off of.
        :return: none
        """
        if len(treeview.get_children()) > 0:
            # unpacking the children list returned from the treeview
            treeview.delete(*treeview.get_children())


    def get_id_entry(self):
        """
        Get the user input from the practitioner identifier field
        :return: string of the user input
        """
        return self.id_entry.get()

    def get_update_period_entry(self):
        """
        Get the user inputted update period
        :return: string of the desired period in seconds
        """
        return self.update_period_entry.get()

    def show_selected_patient_info(self):
        """
        Displayed the highlighted patients information from the monitor treeview (birth date, gender and address)
        :return: none
        """
        if len(self.monitored_patients.patient_tree.selection()) > 0:

            item = self.monitored_patients.patient_tree.selection()[0]
            selected_patient_values = self.monitored_patients.patient_tree.item(item, "values")
            selected_patient_id = selected_patient_values[8]
            selected_patient_name = self.patient_list.patient_dict[selected_patient_id]._birth_date
            selected_patient_gender = self.patient_list.patient_dict[selected_patient_id]._gender
            selected_patient_country = self.patient_list.patient_dict[selected_patient_id]._country
            selected_patient_state = self.patient_list.patient_dict[selected_patient_id]._state
            selected_patient_city = self.patient_list.patient_dict[selected_patient_id]._city
            selected_patient_full_address = selected_patient_city + "," + selected_patient_state + "," + selected_patient_country
            test_selected_name = selected_patient_values = self.monitored_patients.patient_tree.item(item, "text")


            self.patient_name_label['text'] = "Birthdate: " + selected_patient_name
            self.patient_gender_label['text'] = "Gender: " + selected_patient_gender
            self.patient_address_label['text'] = "Address: " + selected_patient_full_address

            print(self.patient_name_label['text'], self.patient_gender_label['text'], self.patient_address_label['text'])
            # print(test_selected_name)




class Controller(Publisher):
    """
    Class responsible for the interpretation of user inputs, and the management of the behaviour for
    those inputs by informing the model and/or view classes.
    """
    def __init__(self):
        """
        Initialise the controller object, and super call the publisher class, which creates a set for future observers
        to be placed in. Bind all buttons and clicks to be handled within the controller class.
        """
        super().__init__()
        self.period = 0
        self.systolic_limit = None
        self.diastolic_limit = None

        self.thread = None
        self.graph_thread = None
        self.root = tk.Tk()
        self.model = Model()
        self.view = View(self.root, self.model)
        self.server = Server(self.model)

        # bind buttons to functionality defined in the controller.
        # also bind the mouse release on the monitored patient list to run functionality in the view class which
        # display the selected patients information.

        self.view.graph_patient.bind('<Button>', lambda event, result=(): self.add_patient_graph())

        self.view.add_patient_to_monitor.bind('<Button>', lambda event, result=(
            self.view.patient_list, self.view.monitored_patients): self.add_patient_monitor())

        self.view.add_patient_cholesterol_to_monitor.bind('<Button>', lambda event, result=(
            self.view.patient_list, self.view.monitored_patients): self.add_patient_cholestrol_monitor())

        self.view.add_patient_blood_pressure_to_monitor.bind('<Button>', lambda event, result=(
            self.view.patient_list, self.view.monitored_patients): self.add_patient_bp_monitor())

        self.view.remove_patient.bind('<Button>', lambda event, result=(
            self.view.patient_list, self.view.monitored_patients): self.remove_patient_monitor())

        self.view.remove_patient_cholesterol.bind('<Button>', lambda event, result=(
            self.view.patient_list, self.view.monitored_patients): self.remove_patient_cholestrol_monitor())

        self.view.remove_patient_blood_pressure.bind('<Button>', lambda event, result=(
            self.view.patient_list, self.view.monitored_patients): self.remove_patient_bp_monitor())

        self.view.id_button.bind('<Button>', lambda event, result=(): self.contact_server())
        self.view.update_button.bind('<Button>', lambda event, result=(): self.update_period())

        self.view.systolic_bp_button.bind('<Button>', lambda event, result=(): self.set_systolic_limit())
        self.view.diastolic_bp_button.bind('<Button>', lambda event, result=(): self.set_diastolic_limit())

        self.view.monitored_patients.patient_tree.bind('<ButtonRelease-1>',
                                                       lambda event, result=(): self.view.show_selected_patient_info())

    def run(self):
        """
        Responsible for launching the tkinter mainloop, and the creation of the application to the user.
        :return: none
        """


        self.root.title("FHIR Monitor")
        self.root.mainloop()


    def add_patient_monitor(self):
        """
        Once the add patient button has been clicked, this function will execute. Launches the associated view function
        for handling a patient being added to the monitor treeview
        :return: none
        """
        self.view.add_monitor(self.systolic_limit, self.diastolic_limit, cholestrol=True, bp=True)

    def add_patient_cholestrol_monitor(self):
        """
        Once the add patient button has been clicked, this function will execute. Launches the associated view function
        for handling a patient being added to the monitor treeview
        :return: none
        """
        self.view.add_monitor(self.systolic_limit, self.diastolic_limit, cholestrol=True, bp=False)

    def add_patient_bp_monitor(self):
        """
        Once the add patient button has been clicked, this function will execute. Launches the associated view function
        for handling a patient being added to the monitor treeview
        :return: none
        """
        self.view.add_monitor(self.systolic_limit, self.diastolic_limit, cholestrol=False, bp=True)

    def remove_patient_monitor(self):
        """
        Launches once the remove patient button is pressed, responsible for notifying the view that some behn
        :return: none
        """
        self.view.remove_monitor(self.systolic_limit, self.diastolic_limit)

    def remove_patient_cholestrol_monitor(self):
        """
        Launches once the remove patient button is pressed, responsible for notifying the view that some behn
        :return: none
        """
        self.view.remove_specific_monitor(self.systolic_limit, self.diastolic_limit, cholestrol=False, bp=True)

    def remove_patient_bp_monitor(self):
        """
        Launches once the remove patient button is pressed, responsible for notifying the view that some behn
        :return: none
        """
        self.view.remove_specific_monitor(self.systolic_limit, self.diastolic_limit, cholestrol=True, bp=False)

    def add_patient_graph(self):
        """
        Launches once the create patient graph button is pressed, responsible for notifying the view that some behn
        :return: none
        """

        self.view.create_graph()

    def contact_server(self):
        """
        Contact the server to retrieve all patients for a particular practitioners identifier. Launched once the
        id_button is clicked. Will notify the view to insert all patients into the patient_list treeview
        :return: none
        """
        practitioner_id = self.view.get_id_entry()
        # contact server and be returned a dictionary with all patients that have a 'total cholesterol' field attached
        # to their report
        self.view.patient_list.patient_dict = self.server.get_patients(practitioner_id)
        # attach the patients to the dashboardcontroller so that they may be updated through the observer pattern
        for patient in self.view.patient_list.patient_dict:
            self.attach(self.view.patient_list.patient_dict[patient])

        self.view.insert_patients()

    def set_systolic_limit(self):
        try:
            self.systolic_limit = int(self.view.systolic_bp_entry.get())
        except:
            return

    def set_diastolic_limit(self):
        try:
            self.diastolic_limit = int(self.view.diastolic_bp_entry.get())
        except:
            return

    def update_period(self):
        """
        Executed once the update period has been entered and the update button has been pressed. Will create a new
        thread, on which the function update_patients will continually launch itself asynchronously.
        :return:
        """
        try:
            self.period = int(self.view.get_update_period_entry())
        except:
            return

        # Create a new thread if one has not been started, only want one thread
        if self.thread is None and len(self.view.patient_list.patient_dict) > 0:
            # update the patients information through another thread from the main ui thread. lets users interact with
            # system while patients are being updated. This is completed through the threading library, and specifically,
            # completed through a Thread object at first, then using the time library to place the system in sleep for a
            # set period of time inside the update_patients function.
            self.thread = threading.Thread(target=self.update_patients, args=(self.root,))
            self.thread.start()

    # def update_graph(self, root):
    #     """
    #     Repeats itself once launched until the program has been stopped. The function will sleep for a specified period
    #     of time through the update_period_entry, then notify the observers attached to the controller that they must
    #     update, which contacts the server to update themselves. Completed asynchronously.
    #     :param root: The context of which thread to launch itself onto.
    #     :return: none
    #     """
    #
    #     # while True:
    #         # sleep for the same period of time before updating the patients again
    #     sleep(self.period)
    #     print("updating graph")
    #     self.notify_observers()
    #     self.view.create_graph()
    #
    #     # root.after(200, self.update_graph(root))

    def update_patients(self, root):
        """
        Repeats itself once launched until the program has been stopped. The function will sleep for a specified period
        of time through the update_period_entry, then notify the observers attached to the controller that they must
        update, which contacts the server to update themselves. Completed asynchronously.
        :param root: The context of which thread to launch itself onto.
        :return: none
        """
        while True:
            # sleep for the same period of time before updating the patients again
            sleep(self.period)

            print("updating.......")
            self.notify_observers()
            # root.after(self.period * 1000, lambda: loop.run_until_complete(self.update_patients(root)))
            root.after(200, self.update_patients(root))




class TreeView(ABC):
    """
    Generalisation of the TreeView objects to be placed into the applications frame. Contains the initialisation of the
    TreeView object, the creation of a new column(multiple columns if specified at creation) and placement of the
    vertical scrollbar.
    """
    def __init__(self, frame, *args):
        """
        Initialise the new ttk.TreeView object with a reference of the frame specified.
        :param frame: The frame on which to place the TreeView object
        :param args: the list of strings that represent the desired column headings.
        """
        # # https://docs.python.org/3/library/tkinter.ttk.html
        self.patient_dict = {}
        if len(args) >= 1:
            # if columns are specified, convert the list of them into a tuple and place into the
            # treeview creation function
            self.patient_tree = ttk.Treeview(frame, columns=tuple(args))
        else:
            self.patient_tree = ttk.Treeview(frame)

        self.patient_tree.heading("#0", text="Name", anchor="w")
        self.patient_tree.column("#0", minwidth=10, width=75)
        self.patient_tree.bind("<<TreeviewSelect>>")
        # place scroll bar on right hand side of treeview
        vertical_scroll_bar = ttk.Scrollbar(self.patient_tree, orient="vertical", command=self.patient_tree.yview)
        vertical_scroll_bar.pack(side='right', fill='y')
        self.patient_tree.configure(yscrollcommand=vertical_scroll_bar.set)


class MonitoredList(TreeView):
    """
    Implementation of the TreeView abstract class. Will specify column dimensions and text, and relative positioning
    within the frame.
    """
    def __init__(self, entry_frame):
        """
        Initialise the monitor TreeView. Includes a super call to the TreeView class in order to place columns
        and create the TreeView itself.
        :param entry_frame: the frame on which to place the TreeView
        """
        super().__init__(entry_frame, "Total Cholesterol", "Time", "Systolic Blood Pressure", "Diastolic Blood Pressure", "Time")
        self.patient_tree.heading("#1", text="Total Cholesterol", anchor="w")
        self.patient_tree.column("#1", minwidth=10, width=75)
        self.patient_tree.heading("#2", text="Time", anchor="w")
        self.patient_tree.column("#2", minwidth=10, width=75)
        self.patient_tree.heading("#3", text="Systolic Blood Pressure", anchor="w")
        self.patient_tree.column("#3", minwidth=10, width=75)
        self.patient_tree.heading("#4", text="Diastolic Blood Pressure", anchor="w")
        self.patient_tree.column("#4", minwidth=10, width=75)
        self.patient_tree.heading("#5", text="Time", anchor="w")
        self.patient_tree.column("#5", minwidth=10, width=75)
        self.patient_tree.place(relheight=0.6, relwidth=0.8, relx=0.20, rely=0.48)


class PatientList(TreeView):
    """
    Implementation of the TreeView abstract class that displays all patients returned from a server call. Will specify
    column dimensions and text, and relative positioning within the frame.
    """
    def __init__(self, entry_frame):
        """
        Initialise the patient_list TreeView. Includes a super call to the TreeView in order to create the
        TreeView itself.
        :param entry_frame: the frame on which to place the TreeView
        """
        # super call to place default column and create treeview
        super().__init__(entry_frame)
        self.patient_tree.place(relheight=0.6, relwidth=0.25, relx=0, rely=0.48)


class Patient(Observer):
    """
    Implementation of the Observer class. Represents a single patient for a particular practitioner. This class then
    implements the update method, specifying functionality desired for when a patient needs updating.
    """
    def __init__(self, new_name, new_total_chol, new_systolic, new_diastolic, blood_pressure_time, new_time, new_city, new_state,
                 new_country, id, gender, birth_date):
        """
        Initialise the patient object with values
        :param new_name: name of the patient
        :param new_total_chol: total reported cholesterol for the patient
        :param new_time: date the cholesterol value was issued on
        :param new_city: patients current city
        :param new_state: patients current state
        :param new_country: patients current country
        :param id: patients assigned ID within the server
        :param gender: patients gender
        :param birth_date: patients birth date as a datetime object
        """
        # making the variables hinted at internal use, python doesnt support full private variables and methods
        super().__init__()
        self._name = new_name
        self._total_chol = new_total_chol
        self._systolic = new_systolic
        self._diastolic = new_diastolic
        self._blood_pressure_time = blood_pressure_time
        self._last_update = new_time
        self._city = new_city
        self._state = new_state
        self._country = new_country
        self._id = id
        self._gender = gender
        self._birth_date = birth_date

    def set_systolic(self, systolic_val):
        self._systolic = systolic_val

    def set_diastolic(self, diastolic_val):
        self._diastolic = diastolic_val

    def set_blood_pressure_time(self, time_obj):
        self._blood_pressure_time = time_obj

    def get_blood_pressure_time(self):
        return self._blood_pressure_time

    def get_last_update(self):
        """
        Return the datetime object explaining the last time the total cholesterol value was updated
        :return: datetime object, with the date of cholesterol measurement.
        """
        return self._last_update

    def update(self):
        """
        Implements the method defined in the abstract Observer class. Contacts the server to check whether this patient
        has any new diagnostic reports, and whether these reports include a recorded value for total cholesterol.
        Patient information is updated within the server class, as a reference of this object is passed through.
        :return: none
        """
        # initialise new server instance just for updating.
        # passes a reference of itself(patient) so that values can be changed
        Server.update_patient(Server(Model), self)
        print("patient " + self._name + "  got updated: " + self._id + "  Cholestrol: " + str(self._total_chol))




class Server(threading.Thread):
    """
    Class responsible for the contacting of the Monash FHIR hosting service.
    """
    def __init__(self, model):
        """
        Initialise by calling the initialisation method of the threading.Thread class, which allows this class to be
        executed asynchronously .
        :param model: the model class responsible for the handling of business logic.
        """
        super().__init__()
        self.root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
        self.model = model

    def get_patients(self, practitioner_id):
        """
        Returns all patients for a particular practitioner identifier that have a total cholesterol value report
        attached to their file on the server.
        :param practitioner_id: Practitioner identifier string that conforms to the "http://hl7.org/fhir/sid/us-npi|"
        :return: patient_dict: dictionary with Patient objects that represent patients in the system who have the
                            practitioner as their recorded doctor, and have a report on their file that includes
                            the total cholesterol.
        """
        # get first page
        encounters_url = self.root_url + "Encounter?participant.identifier=http://hl7.org/fhir/sid/us-npi|" + \
                         practitioner_id + "&_include=Encounter.participant.individual&_include=Encounter.patient"

        monitored_patients = []
        patient_names = []
        patient_dict = {}
        next_page = True
        next_url = encounters_url

        while next_page:
            # Collect all encounters for the practitioner, all patient IDs and their names
            next_page = False
            print(next_url)
            all_encounters_practitioner = requests.get(url=next_url).json()
            links = all_encounters_practitioner['link']
            all_encounter_data = all_encounters_practitioner['entry']
            for item in links:
                if item["relation"] == "next":
                    # check if the page has a next page accessible
                    next_page = True
                    next_url = item["url"]

            for entry in all_encounter_data:
                item = entry['resource']
                patient = item['subject']['reference']
                patient_name = item['subject']['display']
                # get rid of digits in their names
                patient_id = patient.split('/')[1]
                # Minimising the amount of requests sent to the server is the next stage by doing this check here.
                if patient_id not in monitored_patients:
                    # check whether the patient has already been found in an encounter. Dont care about getting the
                    # latest encounter, because the diagnostic report is the only date we care about.
                    patient_names.append(''.join(i for i in patient_name if not i.isdigit()))
                    monitored_patients.append(patient_id)

        # Go through all patients found for all encounters, checking whether the diagnostic reports for those patients
        for i in range(len(monitored_patients)):
            patient_id = monitored_patients[i]
            dReport_url = self.root_url + "DiagnosticReport/?patient=" + patient_id
            dReports = requests.get(url=dReport_url).json()
            # Extract data
            try:
                entry = dReports['entry']
            except:
                continue
                # no entry

            for en in entry:
                results = en['resource']['result']

                # Check whether this observation is on cholesterol or not.
                for result in results:
                    if result['display'] == 'Total Cholesterol':
                        temp_patient_info_url = self.root_url + "Patient/" + patient_id
                        temp_patient_info = requests.get(url=temp_patient_info_url).json()
                        birth_date = temp_patient_info["birthDate"]
                        city = temp_patient_info["address"][0]["city"]
                        state = temp_patient_info["address"][0]["state"]
                        country = temp_patient_info["address"][0]["country"]
                        gender = temp_patient_info["gender"]
                        name = patient_names[i]

                        issued = en['resource']['issued'][:len('2008-10-14')]
                        date = datetime.strptime(issued, '%Y-%m-%d').date()
                        observation_ref = result['reference']
                        observation_data = requests.get(url=self.root_url + observation_ref).json()
                        value = observation_data['valueQuantity']['value']

                        systolic = 0
                        diastolic = 0
                        blood_pressure_time = '-'

                        patient_values = (name,(value, date, systolic, diastolic, blood_pressure_time, city, state, country, patient_id, gender, birth_date))
                        temp_patient = self.model.return_patient(patient_values)

                        # temp_patient = Patient(name, value, date, city, state, country, patient_id, gender, birth_date)
                        if patient_id in patient_dict:
                            # patient has been previously recorded with cholesterol data
                            if patient_dict[patient_id].get_last_update() < temp_patient.get_last_update():
                                # newer data available than in the dictionary, so put in there
                                patient_dict[patient_id] = temp_patient
                        else:
                            # no patient has been recorded with cholesterol data yet
                            patient_dict[patient_id] = temp_patient

                        patient_array = []
                        patient_array.append(patient_id)
                        patient_array.append(value)
                        patient_array.append(systolic)
                        patient_array.append(diastolic)
                        patient_array.append(date)
                        # this prints the cholesterol data of the patients of a particular practitioner
                        print(patient_array)

            findBPUrl = self.root_url + "Observation?patient=" + patient_id + "&code=55284-4&_sort=date&_count=13"
            patientBP = requests.get(url=findBPUrl).json()
            try:
                BPData = patientBP['entry']
            except:
                continue
                # no entry
            # here we get all cholesterol values recorded for the particular patient
            for entry2 in BPData:
                issued = entry2['resource']['issued'][:len('2008-10-14')]
                date_issued = datetime.strptime(issued, '%Y-%m-%d').date()

                diastolic_val = entry2['resource']['component'][0]['valueQuantity']['value']
                systolic_val = entry2['resource']['component'][1]['valueQuantity']['value']

                if patient_dict[patient_id].get_blood_pressure_time() == '-':
                    # newer data available than in the dictionary, so put in there
                    patient_dict[patient_id].set_blood_pressure_time(date_issued)
                    patient_dict[patient_id].set_systolic(systolic_val)
                    patient_dict[patient_id].set_diastolic(diastolic_val)

                elif patient_dict[patient_id].get_blood_pressure_time() < date_issued:
                    patient_dict[patient_id].set_blood_pressure_time(date_issued)
                    patient_dict[patient_id].set_systolic(systolic_val)
                    patient_dict[patient_id].set_diastolic(diastolic_val)

        return patient_dict

    async def update_patient(self, patient):
        """
        Asynchronous calling of the server over a period of N seconds, defined and controlled in the Controller class.
        Looks at the patient specified in the system, and checks if any new diagnostic reports have been entered that
        have the total cholesterol field given.
        :param patient: Patient object for which to check if any new reports are available, and to change the data if
                        necessary
        :return: none
        """
        diag_url = self.root_url + "DiagnosticReport?patient=" + patient._id
        diag_report = requests.get(url=diag_url).json()
        # check if the patient id has any reports to their file
        try:
            entry = diag_report['entry']
        except:
            return

        for en in entry:
            results = en['resource']['result']
            issued = en['resource']['issued'][:len('2008-10-14')]
            report_issued = datetime.strptime(issued, '%Y-%m-%d').date()

            # Check whether this observation is on cholesterol or not, only contact server for the actual cholesterol
            # data if its available, and if the observation was issued after the issued cholesterol value on file
            # for the patient
            if report_issued > patient.get_last_update():
                for result in results:
                    if result['display'] == 'Total Cholesterol':
                        temp_patient_info_url = self.root_url + "Patient/" + patient._id
                        temp_patient_info = requests.get(url=temp_patient_info_url).json()
                        # patient object passed to function, so change directly within this function.
                        patient._birth_date = temp_patient_info["birthDate"]
                        patient._city = temp_patient_info["address"][0]["city"]
                        patient._state = temp_patient_info["address"][0]["state"]
                        patient._country = temp_patient_info["address"][0]["country"]
                        patient._gender = temp_patient_info["gender"]
                        patient._name = patient._name

                        observation_ref = result['reference']
                        observation_data = requests.get(url=self.root_url + observation_ref).json()
                        patient._total_chol = observation_data['valueQuantity']['value']

        findBPUrl = self.root_url + "Observation?patient=" + patient._id + "&code=55284-4&_sort=date&_count=13"
        patientBP = requests.get(url=findBPUrl).json()
        try:
            BPData = patientBP['entry']
        except:
            return
            # no entry
        # here we get all cholesterol values recorded for the particular patient
        for entry2 in BPData:
            issued = entry2['resource']['issued'][:len('2008-10-14')]
            date_issued = datetime.strptime(issued, '%Y-%m-%d').date()

            diastolic_val = entry2['resource']['component'][0]['valueQuantity']['value']
            systolic_val = entry2['resource']['component'][1]['valueQuantity']['value']

            if date_issued > patient.get_blood_pressure_time():
                patient._blood_pressure_time = date_issued
                patient._systolic = systolic_val
                patient._diastolic = diastolic_val


if __name__ == "__main__":
    dashboard = Controller()
    dashboard.run()
