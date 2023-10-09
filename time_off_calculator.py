import datetime
import re
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk
from tkinter import scrolledtext

import holidays
from tkcalendar import DateEntry

global YEAR
global holiday_list

additionals_list = []
checkbox_list = []
date_format = r"(.*) - (\d+)/(\d+)/(\d+)"


def get_top_time_off(year, processed_days, vacation_days=10, top_n=5):
    all_days_off = set(processed_days.keys())
    for d in get_weekends(year):
        all_days_off.add(d)
    sorted_days_off = sorted(list(all_days_off))
    periods = []
    for start_idx, start_date in enumerate(sorted_days_off):
        vacation_needed = 0
        end_date = start_date
        for potential_end in sorted_days_off[start_idx + 1 :]:
            if potential_end - end_date > timedelta(days=1):
                days_between = (potential_end - end_date).days - 1
                vacation_needed += days_between
            if vacation_needed > vacation_days:
                break
            end_date = potential_end
        duration = end_date - start_date + timedelta(days=1)
        periods.append((start_date, end_date, duration))
    periods = sorted(periods, key=lambda x: x[2], reverse=True)[:top_n]
    results = []
    for period in periods:
        start, end, duration = period
        included_weekends = sum(1 for d in get_weekends(year) if start <= d <= end)
        included_holidays = [
            holiday for day, holiday in processed_days.items() if start <= day <= end
        ]
        results.append((start, end, duration, included_weekends, included_holidays))
    return results


def get_weekends(year):
    weekends = []
    current_date = date(year, 1, 1)
    while current_date.weekday() != 5 and current_date.year == year:
        current_date += timedelta(days=1)
    while current_date.year == year:
        weekends.append(current_date)
        if current_date + timedelta(days=1) < date(year + 1, 1, 1):
            weekends.append(current_date + timedelta(days=1))
        current_date += timedelta(days=7)
    return weekends


def set_year():
    global YEAR, holiday_list
    try:
        YEAR = int(year_entry.get())
    except Exception as e:
        YEAR = datetime.datetime.now().year
        year_entry.insert(0, YEAR)
    holiday_list = {
        date: name
        for date, name in holidays.UnitedStates(years=YEAR).items()
        if "Observed" not in name
    }
    for i, (date, name) in enumerate(sorted(holiday_list.items())):
        var = tk.BooleanVar(root, False)
        checkbox = ttk.Checkbutton(
            root, text="{} - {}".format(name, date.strftime("%m/%d/%Y")), variable=var
        )
        checkbox.grid(row=6 + i, column=1, padx=10, pady=5)
        checkbox_list.append(checkbox)
    cal_button = ttk.Button(root, text="Calculate", command=calculate)
    cal_button.grid(row=6 + len(holiday_list), column=1, padx=10, pady=5)


def calculate():
    vacation_days = int(vacation_days_entry.get())
    num_results = int(num_results_entry.get())
    process_days = {}
    for checkbox in checkbox_list:
        match = re.search(date_format, checkbox.cget("text"))
        if match:
            day_text = match.groups()[0]
            month = int(match.groups()[1])
            day = int(match.groups()[2])
            year = int(match.groups()[3])
            add_date = date(year, month, day)
            process_days[add_date] = day_text

    for additional_day in additionals_list:
        match = re.search(date_format, additional_day)
        if match:
            day_text = match.groups()[0]
            month = int(match.groups()[1])
            day = int(match.groups()[2])
            year = int(match.groups()[3])
            add_date = date(year, month, day)
            process_days[add_date] = day_text

    top_periods = get_top_time_off(year, process_days, vacation_days, num_results)
    output_lines = []
    for i, (start, end, duration, weekends, holidays_included) in enumerate(
        top_periods, 1
    ):
        days_off = duration.days
        holiday_list = ", ".join(holidays_included)
        output_lines.append(f"#{i}: From {start} to {end}, which is {days_off} days.\n")
        output_lines.append(
            f"  Includes {int(weekends / 2)} weekends and the following holidays: {holiday_list}\n\n"
        )
    popup = tk.Toplevel(root)
    popup.geometry("1000x500")
    popup.title(f"Results for {year}")

    textbox = scrolledtext.ScrolledText(popup, wrap=tk.WORD, width=1000, height=500)
    textbox.pack(pady=20, padx=20)

    for line in output_lines:
        textbox.insert(tk.END, line)


def add_date():
    additional_day_text = additional_day_off_entry.get()
    if additional_day_text != "":
        listbox_entry = (
            additional_day_text + " - " + add.get_date().strftime("%m/%d/%Y")
        )
        additional_day_off_entry.delete(0, tk.END)
        listbox.insert(tk.END, listbox_entry)
        additionals_list.append(listbox_entry)


def delete_selected_note(event):
    index = listbox.curselection()
    if index:
        index = index[0]
        listbox.delete(index)
        if event.keysym == "BackSpace":
            listbox.selection_set(index - 1)
        if event.keysym == "Delete":
            listbox.selection_set(index)
        additionals_list.pop(index)


root = tk.Tk()
root.title("Time Off Calculator")

year_label = ttk.Label(root, text="Year:")
year_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

year_entry = ttk.Entry(root, width=50)
year_entry.grid(row=0, column=1, padx=10, pady=5)

add_button = ttk.Button(root, text="Set Year", command=set_year)
add_button.grid(row=0, column=2, padx=10, pady=5)

vacation_days_label = ttk.Label(root, text="Vacation Days:")
vacation_days_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

vacation_days_entry = ttk.Entry(root, width=50)
vacation_days_entry.grid(row=1, column=1, padx=10, pady=5)

num_results_label = ttk.Label(root, text="Number of Results:")
num_results_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

num_results_entry = ttk.Entry(root, width=50)
num_results_entry.grid(row=2, column=1, padx=10, pady=5)

additional_day_off_label = ttk.Label(root, text="Additional Day Off:")
additional_day_off_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

additional_day_off_entry = ttk.Entry(root, width=50)
additional_day_off_entry.grid(row=3, column=1, padx=10, pady=5)

add = DateEntry(
    root, width=12, background="darkblue", foreground="white", borderwidth=2
)
add.grid(row=3, column=2, sticky="e")

add_button = ttk.Button(root, text="Add", command=add_date)
add_button.grid(row=3, column=3, padx=10, pady=5)

listbox = tk.Listbox(root, width=50, height=10)
listbox.grid(row=5, column=1, padx=10, pady=5)
listbox.bind("<Delete>", delete_selected_note)
listbox.bind("<BackSpace>", delete_selected_note)

root.mainloop()
