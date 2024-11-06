
class pageMetrics:

    def __init__(self, visited_travel={}, visited_career={}, visited_hobby={}, total_visited=0, buttons_clicked=0, total_hobby=0, total_career=0, total_travel=0):
        self.visited_travel = visited_travel
        self.visited_career = visited_career
        self.visited_hobby = visited_hobby
        self.buttons_clicked = buttons_clicked
        self.total_visited = total_visited
        self.total_hobby = total_hobby
        self.total_career = total_career
        self.total_travel = total_travel  
    
    def get_visited_travel(self, name):
        if name not in self.visited_travel:
            self.visited_travel[name] = 0
        return self.visited[name]


    def get_visited_hobby(self, name):
        if name not in self.visited_hobby:
            self.visited_hobby[name] = 0
        return self.visited_hobby[name]

    def get_visited_career(self, name):
        if name not in self.visited_career:
            self.visited_career[name] = 0
        return self.visited_career[name]

    def get_total_travel(self):
        return self.total_travel

    def get_total_career(self):
        return self.total_career

    def get_total_hobby(self):
        return self.total_hobby
        
    def get_buttons_clicked(self):
        return self.buttons_clicked

    def add_visit_travel(self, name):
        if name not in visited:
            self.visited[name] = 1
        else:
            self.visited_t[name] += 1
        total_travel += 1
        
    def add_visit_career(self, name):
        if name not in visited_career:
            self.visited_career[name] = 1
        else:
            self.visited_career[name] += 1
        total_career += 1
        
    def add_visit_hobby(self, name):
        if name not in self.visited_hobby:
            self.visited_hobby[name] = 1
        else:
            self.visited_hobby[name] += 1
        self.total_hobby += 1

    def add_click(self):
        self.buttons_clicked +=1

    def find_max_visited(self):
        max_visited = 0
        max_visited_name = ""
        for name, count in self.visited.items():
            if count > max_visited:
                max_visited = count
                max_visited_name = name
        return (max_visited_name, max_visited)
