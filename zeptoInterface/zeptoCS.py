import PySimpleGUI as sg
import datetime
import time

# KEY DEFINITIONS
# _time_ = text field that displays time

# Create the layout
layout = [[sg.Text('Gap_RBV: '), sg.Text('', key='_gap_', size=(20, 1))],
         [sg.Text('Centre_RBV: '), sg.Text('', key='_centre_', size=(20, 1))],
         [sg.Text('Gap_DMD: '), sg.InputText() ],
         [sg.Text('Centre_DMD: '),sg.InputText()],
         [sg.Button('GO'), sg.Button('STOP'), sg.Quit()]]

# Create the window object
window = sg.Window('Simple Clock').Layout(layout)

def getTime():
    return datetime.datetime.now().strftime('%H:%M:%S')

def main(gui_obj):
    # Event loop
    while True:
        event, values = gui_obj.Read(timeout=10)

        time.sleep(0.1)
        # Exits program cleanly if user clicks "X" or "Quit" buttons
        if event in (None,'Quit'):
            break
        if event == 'GO':
            print(f"&2 Q78 = {values[0]}")
            print(f"&2 Q79 = {values[1]}")
            time.sleep(0.1)
            print("&2a")
            time.sleep(0.1)
            print("&2b10r")

        # Update '_time_' key value with return value of getTime()
        print("&2 Q88\r\n")

        print("&2 Q89\r\n")
        gui_obj.FindElement('_gap_').Update(getTime())
        gui_obj.FindElement('_centre_').Update(getTime())

if __name__ == '__main__':
    main(window)
