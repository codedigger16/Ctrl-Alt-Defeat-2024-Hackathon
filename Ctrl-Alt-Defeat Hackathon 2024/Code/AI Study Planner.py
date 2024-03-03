import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import random

# Predefined study materials for each subject
study_materials = {
    "Math": ["Algebra textbook", "Khan Academy - Calculus playlist", "Past exam papers"],
    "Economics": ["Microeconomics textbook", "Crash Course Economics - YouTube series", "Economic Times articles"],
    "Chemistry": ["Chemistry textbook", "MIT OpenCourseWare - General Chemistry", "Chemistry Khan Academy videos"],
    "Physics": ["Physics textbook", "The Feynman Lectures on Physics", "Physics Khan Academy videos"]
}

class StudyPlanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Plan Generator")

        # Initialize subject checkboxes
        self.selected_subjects = []
        self.checkbox_vars = {}
        self.rating_comboboxes = {}
        self.comfort_level_labels = {}
        self.subjects = ["Math", "Economics", "Chemistry", "Physics"]

        for i, subject in enumerate(self.subjects):
            self.checkbox_vars[subject] = tk.BooleanVar()
            self.checkbox_vars[subject].trace_add("write", self.update_dropdown)
            checkbox = ttk.Checkbutton(root, text=subject, variable=self.checkbox_vars[subject])
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")

        # Create input field for number of days
        self.days_label = ttk.Label(root, text="Number of days:")
        self.days_label.grid(row=len(self.subjects), column=0, padx=10, pady=5, sticky="w")
        self.days_entry = ttk.Entry(root, width=10)
        self.days_entry.grid(row=len(self.subjects), column=1, padx=10, pady=5)

        # Generate study schedule button
        self.generate_button = ttk.Button(root, text="Generate Study Schedule", command=self.generate_study_plan)
        self.generate_button.grid(row=len(self.subjects) + 1, column=0, columnspan=2, padx=10, pady=5)

    def update_dropdown(self, *args):
        for i, (subject, var) in enumerate(self.checkbox_vars.items()):
            if var.get():
                if subject not in self.rating_comboboxes:
                    self.create_dropdown(subject, i)

    def create_dropdown(self, subject, row):
        self.comfort_level_labels[subject] = ttk.Label(self.root, text="What's your comfort level, 5 being the highest?")
        self.comfort_level_labels[subject].grid(row=row, column=2, padx=10, pady=2, sticky="w")
        self.rating_comboboxes[subject] = ttk.Combobox(self.root, values=["1", "2", "3", "4", "5"])
        self.rating_comboboxes[subject].grid(row=row, column=3, padx=10, pady=5, sticky="w")

    def generate_study_plan(self):
        try:
            days = int(self.days_entry.get())

            selected_subjects = [subject for subject, var in self.checkbox_vars.items() if var.get()]
            if not selected_subjects:
                messagebox.showerror("Error", "Please select at least one subject")
                return
            if days <= 0:
                messagebox.showerror("Error", "Number of days must be a positive integer")
                return

            subject_ratings = [self.rating_comboboxes[subject].get() for subject in selected_subjects]
            model = self.train_decision_tree(selected_subjects, subject_ratings)
            recommended_materials = self.recommend_materials(model, subject_ratings)
            hours_per_day = self.get_hours_per_day()

            self.display_results(days, recommended_materials, hours_per_day, selected_subjects)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values")

    def train_decision_tree(self, subjects, ratings):
        label_encoder = LabelEncoder()
        ratings_encoded = label_encoder.fit_transform(ratings)

        model = DecisionTreeClassifier()
        model.fit([[rating] for rating in ratings_encoded], subjects)
        return model

    def recommend_materials(self, model, subject_ratings):
        label_encoder = LabelEncoder()
        ratings_encoded = label_encoder.fit_transform(subject_ratings)

        prediction = model.predict([[rating] for rating in ratings_encoded])[0]
        recommended_materials = study_materials[prediction]
        return recommended_materials

    def display_results(self, days, recommended_materials, hours_per_day, selected_subjects):
        result_window = tk.Toplevel(self.root)
        result_window.title("Study Plan Results")

        schedule_label = ttk.Label(result_window, text="Generated Study Schedule:")
        schedule_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tree = ttk.Treeview(result_window, columns=["Subject", "Hours"])
        tree.heading("#0", text="Day Number")
        tree.heading("Subject", text="Subject and Hours")
        tree.grid(row=1, column=0, padx=10, pady=5)

        rest_days = self.calculate_rest_days(selected_subjects, days)
        rest_day_counter = 0
        for day in range(1, days + 1):
            if rest_day_counter == rest_days:
                rest_day_counter = 0
                continue

            daily_schedule = self.generate_daily_schedule(hours_per_day, selected_subjects)
            tree.insert("", "end", text=f"Day {day}", values=daily_schedule)
            rest_day_counter += 1

        materials_label = ttk.Label(result_window, text="Recommended Study Materials:")
        materials_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        materials_text = "\n".join(recommended_materials)
        materials_textbox = tk.Text(result_window, height=5, width=40)
        materials_textbox.insert(tk.END, materials_text)
        materials_textbox.grid(row=3, column=0, padx=10, pady=5)

    def generate_daily_schedule(self, hours_per_day, selected_subjects):
        schedule = {}
        start_hour = 16
        remaining_hours = hours_per_day
        for subject in selected_subjects:
            if remaining_hours <= 0:
                break
            hours = random.randint(0, min(remaining_hours, 4))
            if hours > 0:
                schedule[subject] = f"{hours} hours"
                remaining_hours -= hours
        return ", ".join([f"{subject}: {time}" for subject, time in schedule.items()])

    def get_hours_per_day(self):
        return int(simpledialog.askstring("Hours per Day", "How many hours do you want to study each day?"))

    def calculate_rest_days(self, selected_subjects, total_days):
        comfort_level = sum([int(self.rating_comboboxes[subject].get()) for subject in selected_subjects])
        rest_days = max(2, comfort_level // 5 // 2)  # Ensure at least 2 rest days for every 10 study days
        if rest_days == total_days:
            rest_days -= 1  # Ensure there is at least one day of study
        return rest_days

def main():
    root = tk.Tk()
    app = StudyPlanApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
