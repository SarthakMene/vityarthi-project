import csv
import os


STUDENT_FILE = 'students.csv'
COMPANY_FILE = 'companies.csv'
PLACEMENT_FILE = 'placements.csv'

class Student:
    """Represents a single student and their eligibility criteria."""
    def __init__(self, roll_no, name, dept, cGPA, backlogs=0, status="Active"):
        self.roll_no = roll_no
        self.name = name
        self.dept = dept
        self.cGPA = float(cGPA)
        self.backlogs = int(backlogs)
        self.status = status 

    def is_eligible(self, min_gpa, max_backlogs):
        """Checks if the student meets basic criteria."""
        return (self.cGPA >= min_gpa) and (self.backlogs <= max_backlogs)

    def to_dict(self):
        """Returns student data as a dictionary for saving."""
        return {
            'roll_no': self.roll_no,
            'name': self.name,
            'dept': self.dept,
            'cGPA': self.cGPA,
            'backlogs': self.backlogs,
            'status': self.status
        }

class Company:
    """Represents a recruiting company and its job criteria."""
    def __init__(self, name, role, salary, min_gpa, max_backlogs, slots):
        self.name = name
        self.role = role
        self.salary = float(salary)
        self.min_gpa = float(min_gpa)
        self.max_backlogs = int(max_backlogs)
        self.slots = int(slots)
        self.placed_count = 0

    def has_slots(self):
        """Checks if the company still has open slots."""
        return self.placed_count < self.slots

    def to_dict(self):
        """Returns company data as a dictionary for saving."""
        return {
            'name': self.name,
            'role': self.role,
            'salary': self.salary,
            'min_gpa': self.min_gpa,
            'max_backlogs': self.max_backlogs,
            'slots': self.slots
        }

class PlacementManager:
    """Manages all student, company, and placement records."""
    def __init__(self):
        self.students = {} 
        self.companies = {} 
        self.placements = []
        self._load_data()

    def _load_data(self):
        """Loads data from CSV files."""
       
        def load_csv(filename, obj_class, key_field):
            if not os.path.exists(filename):
                return {}
            data = {}
            with open(filename, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    
                    data[row[key_field]] = obj_class(**row)
            return data

       
        loaded_students = load_csv(STUDENT_FILE, Student, 'roll_no')
        for roll, student_obj in loaded_students.items():
            self.students[roll] = student_obj

       
        loaded_companies = load_csv(COMPANY_FILE, Company, 'name')
        for name, company_obj in loaded_companies.items():
            self.companies[name] = company_obj

       
        if os.path.exists(PLACEMENT_FILE):
            with open(PLACEMENT_FILE, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.placements.append(row)
                   
                    if row['roll_no'] in self.students:
                        self.students[row['roll_no']].status = "Placed"
                    if row['company'] in self.companies:
                        self.companies[row['company']].placed_count += 1
                        
    def _save_data(self):
        """Saves current data back to CSV files."""
       
        def save_csv(filename, data_list, fieldnames):
            with open(filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_list)

       
        student_data = [s.to_dict() for s in self.students.values()]
        save_csv(STUDENT_FILE, student_data, list(Student('0','n','d',0,0).to_dict().keys()))

        
        company_data = [c.to_dict() for c in self.companies.values()]
        save_csv(COMPANY_FILE, company_data, list(Company('n','r',0,0,0,0).to_dict().keys()))

      
        save_csv(PLACEMENT_FILE, self.placements, ['roll_no', 'company', 'role', 'salary'])


    def register_student(self, roll_no, name, dept, cgpa, backlogs):
        """Adds a new student to the system."""
        if roll_no in self.students:
            print(f"Error: Student {roll_no} already registered.")
            return
        student = Student(roll_no, name, dept, cgpa, backlogs)
        self.students[roll_no] = student
        self._save_data()
        print(f"Success: Student {name} ({roll_no}) registered.")

    def register_company(self, name, role, salary, min_gpa, max_backlogs, slots):
        """Adds a new company drive."""
        if name in self.companies:
            print(f"Error: Company {name} already registered.")
            return
        company = Company(name, role, salary, min_gpa, max_backlogs, slots)
        self.companies[name] = company
        self._save_data()
        print(f"Success: Company {name} registered for role {role}.")

    def get_eligible_students(self, company_name):
        """Lists all students eligible for a specific company drive."""
        company = self.companies.get(company_name)
        if not company:
            print(f"Error: Company {company_name} not found.")
            return []

        eligible_list = []
        for student in self.students.values():
            if student.status == "Active" and student.is_eligible(company.min_gpa, company.max_backlogs):
                eligible_list.append(student)

        print(f"\n--- Eligible Students for {company_name} ({company.role}) ---")
        for s in eligible_list:
            print(f"  {s.roll_no}: {s.name}, GPA: {s.cGPA}")
        return eligible_list

    def place_student(self, roll_no, company_name):
        """Records a successful placement."""
        student = self.students.get(roll_no)
        company = self.companies.get(company_name)

        if not student or not company:
            print("Error: Student or Company not found.")
            return

        if student.status == "Placed":
            print(f"Error: Student {student.name} is already placed.")
            return

        if not company.has_slots():
            print(f"Error: Company {company_name} has filled all {company.slots} slots.")
            return

      
        student.status = "Placed"
        company.placed_count += 1
        placement_record = {
            'roll_no': roll_no,
            'company': company.name,
            'role': company.role,
            'salary': company.salary
        }
        self.placements.append(placement_record)

        self._save_data()
        print(f"\nPlacement Success: {student.name} placed at {company.name} as {company.role}.")

    def generate_placement_report(self):
        """Prints a summary of placements."""
        total_students = len(self.students)
        placed_students = sum(1 for s in self.students.values() if s.status == "Placed")
        placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0

        print("\n--- Placement System Summary Report ---")
        print(f"Total Registered Students: {total_students}")
        print(f"Total Placed Students: {placed_students}")
        print(f"Placement Rate: {placement_rate:.2f}%")
        print("\nPlacement Records:")
        for p in self.placements:
            print(f"  {p['roll_no']} placed at {p['company']} ({p['role']})")



if __name__ == "__main__":
    
   
    system = PlacementManager()
    
   
    system.register_student("CS001", "Alice Johnson", "CS", 8.5, 0)
    system.register_student("EC002", "Bob Smith", "EC", 7.2, 1)
    system.register_student("CS003", "Charlie Brown", "CS", 6.8, 0)
    system.register_student("ME004", "David Lee", "ME", 9.1, 0)
    
   
    system.register_company("TechCorp", "Software Engineer", 12.5, 8.0, 0, 2)
   
    system.register_company("DataSolutions", "Analyst", 6.5, 7.0, 1, 1)

   
    print("\n--- Eligibility Check: TechCorp ---")
    eligible_techcorp = system.get_eligible_students("TechCorp")
    
    print("\n--- Eligibility Check: DataSolutions ---")
    eligible_datasolutions = system.get_eligible_students("DataSolutions")

   
    
    if any(s.roll_no == "CS001" for s in eligible_techcorp):
        system.place_student("CS001", "TechCorp")
        
   
    if any(s.roll_no == "EC002" for s in eligible_datasolutions):
        system.place_student("EC002", "DataSolutions")
        
    
    system.place_student("ME004", "TechCorp")
    
    
    system.place_student("CS003", "TechCorp")

   
    system.generate_placement_report()

