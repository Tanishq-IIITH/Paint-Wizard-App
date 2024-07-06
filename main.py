
# Code with width button, selection delete function
import tkinter as tk
from tkinter import colorchooser

from tkinter import filedialog
import xml.etree.ElementTree as ET

try:
    from tkinter import simpledialog  # For Python 3.5+
except ImportError:
    from tkinter import tix  # For Python versions before 3.5



def draw_rounded_rectangle(canvas,x1, y1, x2, y2, radius=25, **kwargs):
    points = (x1+radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1)

    return canvas.create_polygon(points, **kwargs, smooth=True,fill="white")




class ShapeOptionsDialog(tk.Toplevel):
    def __init__(self, master, canvas, selected_items, selection_box):
        super().__init__(master)
        self.canvas = canvas
        self.drag_data = {}
        self.selected_items = selected_items
        self.selection_box = selection_box
        self.title("Shape Options")

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)

        self.move_button = tk.Button(button_frame, text="Move", command=self.move_shape)
        self.move_button.pack(pady=5, fill=tk.X)

        self.copy_button = tk.Button(button_frame, text="Copy", command=lambda: self.copy_shape(selection_box))
        self.copy_button.pack(pady=5, fill=tk.X)

        self.delete_button = tk.Button(button_frame, text="Delete", command=lambda: self.delete_shape(selection_box))
        self.delete_button.pack(pady=5, fill=tk.X)

        self.edit_button = tk.Button(button_frame, text="Edit", command=self.edit_shape)
        self.edit_button.pack(pady=5, fill=tk.X)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<FocusOut>", self.on_focus_out)

        self.original_colors = {}
        for item in self.selected_items:
            self.original_colors[item] = self.canvas.itemcget(item, "fill")
            self.canvas.itemconfig(item, fill="pink")
        
         
    def get_item_properties(self, item_id):
        item_type = self.canvas.type(item_id)
        item_color = self.canvas.itemcget(item_id, "fill")
        item_width = self.canvas.itemcget(item_id, "width")

        if item_type == "line":
            return {"type": "line", "color": item_color, "width": item_width}
        elif item_type == "rectangle":
            item_outline = self.canvas.itemcget(item_id, "outline")
            return {"type": "rectangle", "color": item_outline, "width": item_width}
        elif item_type == "polygon":
            item_outline = self.canvas.itemcget(item_id, "outline")
            return {"type": "polygon", "color": item_outline, "width": item_width}
        
        
    def move_shape(self):
        # Delete the selection box
        if self.selection_box:
            self.canvas.delete(self.selection_box)
        # Destroy the existing dialog box (if any)
        self.destroy()
        # Bind mouse events for drag and drop
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.drop)
        # Disable the move button after the first drag
        # self.move_button.configure(state="disabled")

    def start_drag(self, event):
        # Find the item under the cursor
        item = self.selected_items
        # Record the item being dragged and the starting position
        self.drag_data["item"] = item
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag(self, event):
        # Calculate the distance moved since the last mouse event
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        # Move the item by the same distance
        for item in self.selected_items:
            self.canvas.move(item, dx, dy)
        # Update the starting position for the next drag event
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drop(self, event):
        # Unbind mouse events for drag and drop
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        # Reset the drag data
        for item, color in self.original_colors.items():
            self.canvas.itemconfig(item, fill=color)
            
        self.drag_data["item"] = None
        self.canvas.delete(self.selection_box)
        self.destroy()

    def copy_shape(self,selection_box):
        # Implement copy shape logic here
        for item, color in self.original_colors.items():
            self.canvas.itemconfig(item, fill=color)
        self.canvas.delete(selection_box)
        self.destroy()
        self.master.copy_selected_items()

        # pass
    def delete_shape(self, selection_box):
        for item in self.selected_items:
            self.canvas.delete(item)
        self.destroy()
        self.canvas.delete(selection_box)

    def on_focus_out(self, event):
        print("Focus out event triggered")
        if not self.focus_get():
            print("Dialog lost focus")
            for item, color in self.original_colors.items():
                self.canvas.itemconfig(item, fill=color)
            self.canvas.delete(self.selection_box)
            self.destroy()
    
    def on_closing(self):
        print("Closing event triggered")
        for item, color in self.original_colors.items():
            self.canvas.itemconfig(item, fill=color)
        self.canvas.delete(self.selection_box)
        self.destroy()
        
    def edit_shape(self):
    # try:
        if not self.selected_items:
            return

    # Call on_closing to reset item colors and delete the selection box
        self.on_closing()

        # Get the properties of the first selected item
        print(self.selected_items)
        first_item_id = list(self.selected_items)[0]
        properties = self.get_item_properties(first_item_id)

        # Create a new dialog window with the root window as the parent
        edit_dialog = tk.Toplevel(self.master)  # Pass self.master as the parent window
        edit_dialog.title("Edit Shape Properties")
        edit_dialog.protocol("WM_DELETE_WINDOW", edit_dialog.destroy)  # Set the protocol to destroy the window when closed

        print(properties)
        # Create widgets for editing properties
        if properties["type"] == "line":
            color_label = tk.Label(edit_dialog, text="Line Color:")
            color_label.pack()
            color_button = tk.Button(edit_dialog, bg=properties["color"],
                                    command=lambda: self.choose_color_rgb(edit_dialog, properties))
            color_button.pack()

            # width_label = tk.Label(edit_dialog, text="Line Width:")
            # width_label.pack()
            # width_entry = tk.Entry(edit_dialog)
            # width_entry.insert(0, str(properties["width"]))
            # width_entry.pack()

            apply_button = tk.Button(edit_dialog, text="Apply",
                                    command=lambda: [self.apply_line_properties(properties, color_button["bg"],
                                                                                float(2)),
                                                    edit_dialog.destroy()])
            apply_button.pack()

        elif properties["type"] == "rectangle" or properties["type"] == "polygon":
            color_label = tk.Label(edit_dialog, text="Rectangle Color:")
            color_label.pack()
            color_button = tk.Button(edit_dialog, bg=properties["color"],
                                    command=lambda: self.choose_color_rgb(edit_dialog, properties))
            color_button.pack()

            # width_label = tk.Label(edit_dialog, text="Rectangle Width:")
            # width_label.pack()
            # width_entry = tk.Entry(edit_dialog)
            # width_entry.insert(0, str(properties["width"]))
            # width_entry.pack()

            # Add an option for choosing the corner style
            corner_style_label = tk.Label(edit_dialog, text="Corner Style:")
            corner_style_label.pack()
            corner_style_var = tk.StringVar(value="normal")
            corner_style_menu = tk.OptionMenu(edit_dialog, corner_style_var, "normal", "round")
            corner_style_menu.pack()

            apply_button = tk.Button(edit_dialog, text="Apply",
                                    command=lambda: [self.apply_rect_properties(properties, self.current_color_selected,
                                                                                float(2),
                                                                                corner_style_var.get()),
                                                    edit_dialog.destroy()])
            apply_button.pack()

        edit_dialog.focus_set()
        edit_dialog.grab_set()
    # edit_dialog.wait_window()  # Remove this line
        # except:
        #     pass
        
        
    def choose_color(self, dialog, properties):
        new_color = colorchooser.askcolor(title="Choose Color")[1]
        if new_color:
            properties["color"] = new_color
            dialog.children["!button"].configure(bg=new_color)

    current_color_selected="black"
    
    def set_color(self,dialog,properties, col):
        self.current_color_selected=col
        print(self.current_color_selected)
    
        properties["color"] = self.current_color_selected
        dialog.children["!button"].configure(bg=self.current_color_selected)
        
    choose_color_rgb_one_time_done=False
    
    def choose_color_rgb(self, dialog, properties):
        if(self.choose_color_rgb_one_time_done==False): 
            self.choose_color_rgb_one_time_done=True
        else: 
            return
        # take string input of color from user
        # Enter either color name from black red green blue
        # code pls
        
        # have 4 buttons for each colour red green blue and black 
        # clicking on them changes the colour to that
        red_button = tk.Button(dialog, text="Red", bg="red", command=lambda: self.set_color(dialog,properties,"red"))
        red_button.pack()
        green_button = tk.Button(dialog, text="Green", bg="green", command=lambda: self.set_color(dialog,properties,"green"))
        green_button.pack()
        blue_button = tk.Button(dialog, text="Blue", bg="blue", command=lambda: self.set_color(dialog,properties,"blue"))
        blue_button.pack()
        black_button = tk.Button(dialog, text="Black", bg="black", command=lambda: self.set_color(dialog,properties, "black"))
        black_button.pack()
        
        print(self.current_color_selected)
    
        # properties["color"] = self.current_color_selected
        # dialog.children["!button"].configure(bg=self.current_color_selected)
    def apply_line_properties(self, properties, color, width):
        for item_id in self.selected_items:
            # if color in ["black", "red", "green", "blue"]:
                self.canvas.itemconfig(item_id, fill=self.current_color_selected, width=width)
            # else:
                # self.canvas.itemconfig(item_id, fill="black", width=width)
        

    def apply_rect_properties(self, properties, color, width, corner_style):

        for item_id in self.selected_items:
            if self.canvas.type(item_id) == "rectangle":
                bbox = self.canvas.bbox(item_id)  # Get the bounding box of the rectangle
                x1, y1, x2, y2 = bbox

                # Delete the old rectangle
                if corner_style == "normal":
                    self.canvas.delete(item_id)
                    self.canvas.create_rectangle(x1, y1, x2, y2, width=width, outline=self.current_color_selected)

                elif corner_style == "round":
                    self.canvas.delete(item_id)
                    draw_rounded_rectangle(self.canvas, x1, y1, x2, y2, radius=25, outline=self.current_color_selected, width=width)
            elif self.canvas.type(item_id) == "polygon":
                # change the polygon to rectangle 
                # code pls
                bbox = self.canvas.bbox(item_id)  # Get the bounding box of the rectangle
                x1, y1, x2, y2 = bbox
                if corner_style == "normal":
                    self.canvas.delete(item_id)
                    self.canvas.create_rectangle(x1, y1, x2, y2, width=width, outline=self.current_color_selected)
                elif corner_style == "round":
                    self.canvas.delete(item_id)
                    draw_rounded_rectangle(self.canvas, x1, y1, x2, y2, radius=25, outline=self.current_color_selected, width=width)



class PaintApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paint App")
        self.copied_items = []
        self.coordinate_copy = {}
        self.deleted=[]
        self.grouped_dict = {}
        self.geometry("800x600")

        # Create a frame for the toolbar
        toolbar_frame = tk.Frame(self)
        toolbar_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Pack the buttons inside the toolbar frame
        buttons = [
            ("Draw Line", self.draw_line),
            ("Draw Rectangle", self.draw_rect),
            ("Select", self.select_mode),
            ("Group", self.grouping),
            ("Ungroup", self.un_grouping),
            ("UngroupAll", self.ungroup_all),
            ("Open", self.open_file),
            ("SaveXML", self.save_to_file),
            ("SaveASCII", self.save_to_ASCII),   
        ]

        # Initialize clicked button as None
        self.clicked_button = None

        for text, command in buttons:
            button = tk.Button(toolbar_frame, text=text, command=command)
            button.pack(side="top", padx=5, pady=5, fill=tk.BOTH)
            button.bind("<Button-1>", lambda event, button=button: self.on_button_click(button))

        # Default values
        self.current_color = "black"
        self.stroke_width = 2
        self.x1, self.y1 = None, None
        self.x2, self.y2 = None, None
        self.drawing_line = False
        self.drawing_rect = False
        self.selecting = False
        self.whether_grouping = False
        self.whether_ungrouping = False
        self.ungroupAll = False
        self.index = 0
        self.line_id = None
        self.rect_id = None
        self.selection_box = None
        self.selected_items = set()

        # Canvas bindings
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.bind_all("<Control-v>", self.ctrl_v_paste)

    def on_button_click(self, button):
        # Reset previous clicked button's appearance
        if self.clicked_button:
            self.clicked_button.config(bg=self.clicked_button.master.cget("bg"))  # Reset background to default

        # Change appearance of clicked button
        button.config(bg="lightblue")  # Change background color
        self.clicked_button = button

    def draw_line(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.drawing_line = True
        self.drawing_rect = False
        self.selecting = False
        self.whether_grouping = False
        self.whether_ungrouping = False
        self.ungroupAll = False

    def draw_rect(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.drawing_line = False
        self.drawing_rect = True
        self.selecting = False
        self.whether_grouping = False
        self.whether_ungrouping = False
        self.ungroupAll = False

    def choose_color(self):
        new_color = colorchooser.askcolor(title="Choose Color")[1]
        if new_color:
            self.current_color = new_color
            self.color_sample.configure(bg=new_color)

    def choose_width(self):
        try:
            new_width = simpledialog.askinteger("Change Width", "Enter new stroke width:", parent=self, minvalue=1,
                                                initialvalue=self.stroke_width)
        except AttributeError:
            new_width = tix.Tk().simpledialog().askinteger("Change Width", "Enter new stroke width:",
                                                           initialvalue=self.stroke_width)
        if new_width:
            self.stroke_width = new_width

            self.width_button.configure(text="Width: " + str(self.stroke_width))

    def start_draw(self, event):
        self.x1, self.y1 = event.x, event.y
        if self.drawing_line:
            self.line_id = self.canvas.create_line(self.x1, self.y1, self.x1, self.y1, capstyle=tk.ROUND, smooth=True,
                                                   width=self.stroke_width, fill=self.current_color)
        elif self.drawing_rect:
            self.rect_id = self.canvas.create_rectangle(self.x1, self.y1, self.x1, self.y1, width=self.stroke_width,
                                                        outline=self.current_color)
        elif self.selecting:
            self.selection_box = self.canvas.create_rectangle(self.x1, self.y1, self.x1, self.y1, outline="blue",
                                                              width=2, dash=(10, 10))
        elif self.whether_grouping:
            self.selection_box = self.canvas.create_rectangle(self.x1, self.y1, self.x1, self.y1, outline="blue",
                                                              width=2, dash=(10, 10))
        elif self.whether_ungrouping:
            self.selection_box = self.canvas.create_rectangle(self.x1, self.y1, self.x1, self.y1, outline="blue",
                                                              width=2, dash=(10, 10))
        elif self.ungroupAll:
            self.selection_box = self.canvas.create_rectangle(self.x1, self.y1, self.x1, self.y1, outline="blue",
                                                              width=2, dash=(10, 10))

    def draw_motion(self, event):
        self.x2, self.y2 = event.x, event.y
        if self.drawing_line:
            self.canvas.coords(self.line_id, self.x1, self.y1, self.x2, self.y2)
        elif self.drawing_rect:
            self.canvas.coords(self.rect_id, self.x1, self.y1, self.x2, self.y2)
        elif self.selecting:
            self.canvas.coords(self.selection_box, self.x1, self.y1, self.x2, self.y2)
        elif self.whether_grouping:
            self.canvas.coords(self.selection_box, self.x1, self.y1, self.x2, self.y2)
        elif self.whether_ungrouping:
            self.canvas.coords(self.selection_box, self.x1, self.y1, self.x2, self.y2)
        elif self.ungroupAll:
            self.canvas.coords(self.selection_box, self.x1, self.y1, self.x2, self.y2)

    def end_draw(self, event):
        if self.drawing_line:
            if self.line_id:
                self.canvas.delete(self.line_id)
            self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill=self.current_color,
                                    width=self.stroke_width)
        elif self.drawing_rect:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, width=self.stroke_width,
                                         outline=self.current_color)
        elif self.selecting:
            self.select_items(self.x1, self.y1, self.x2, self.y2)
            self.selection_box = None

        elif self.whether_grouping:
            self.select_items(self.x1, self.y1, self.x2, self.y2)
            self.selection_box = None
            
        elif self.whether_ungrouping:
            self.select_items(self.x1, self.y1, self.x2, self.y2)
            self.selection_box = None
            
        elif self.ungroupAll:
            self.select_items(self.x1, self.y1, self.x2, self.y2)
            self.selection_box = None

        self.x1, self.y1 = None, None
        self.x2, self.y2 = None, None
        self.line_id = None
        self.rect_id = None

    def select_items(self, x1, y1, x2, y2):

        self.selected_items = set(self.canvas.find_enclosed(x1, y1, x2, y2))
        self.canvas.addtag_enclosed("selected", x1, y1, x2, y2)

        # Show shape options dialog
        if self.selecting:
            temp = []  # Initialize temp list outside the loop
            print(self.selected_items)
            print(self.grouped_dict)
            for item in self.selected_items:
                for key, value_set in self.grouped_dict.items():  # Iterate over key-value pairs
                    if item in value_set:  # Check if item is in the set
                        for value in value_set:  # Iterate over the values in the set
                            if value not in temp:
                                temp.append(value)

            self.selected_items.update(temp)  # Convert temp to list before extending
            self.show_shape_options_dialog()
            
        elif self.whether_grouping:            
            temp=list(self.selected_items)
            if self.select_items:
                for num in self.selected_items:
                     for key, value_set in self.grouped_dict.items():
                        if num in value_set:
                            for value in value_set:
                                if value not in temp:
                                    temp.append(value) 
                if len(temp) == 0:
                    temp = self.selected_items
                    
                     
                for key, value_set in self.grouped_dict.items():
                   if set(temp)== set(value_set):
                       temp=[]
                       break
                if len(temp) > 0:
                    self.grouped_dict[self.index] = temp
                    self.index = self.index + 1
            self.canvas.delete(self.selection_box)
            self.selection_box = None
            print(self.grouped_dict)
            
        elif self.whether_ungrouping:
            temp=[]
            ans=0
            for key, value_set in self.grouped_dict.items():
                # check if selected items is subset of value_set of largest size
                if set(self.selected_items).issubset(value_set):
                    if(len(value_set) > len(temp)):
                        temp = value_set
                        ans=key
                        print("temp", temp)
            del self.grouped_dict[ans]
            
            self.canvas.delete(self.selection_box)
            self.selection_box = None
            
        elif self.ungroupAll:
            # check if value_set and selected_items intersecion is not null, then store in temp and then later delete it from grouped_dict
            temp=[]
            ans=0
            for key, value_set in self.grouped_dict.items():
                # check if selected items is subset of value_set of largest size
                if set(self.selected_items).issubset(value_set):
                    if(len(value_set) > len(temp)):
                        temp = value_set
                        ans=key
                        print("temp", temp)
            print(temp)
            finalans=[]
            for key, value_set in self.grouped_dict.items():
                if set(value_set).intersection(set(temp)):
                    finalans.append(key)
            print("finalans", finalans)
            for key in finalans:
                del self.grouped_dict[key]
            
            
            
            
            self.canvas.delete(self.selection_box)
            self.selection_box = None

    def show_shape_options_dialog(self):
        if self.selected_items:
            dialog = ShapeOptionsDialog(self, self.canvas, self.selected_items, self.selection_box)
        else:
            self.canvas.delete(self.selection_box)
            self.selection_box = None

    def select_mode(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.drawing_line = False
        self.drawing_rect = False
        self.whether_grouping = False
        self.whether_ungrouping = False
        self.ungroupAll = False
        self.selecting = True

    def ctrl_v_paste(self, event):
        if self.copied_items and (event.state & 0x4) != 0 and (event.keysym == "v" or event.keysym == "V"):
            self.paste_items()
            
    def copy_selected_items(self):
        self.copied_items = list(self.selected_items)
        print("copied items", self.copied_items)    
        # find center of the selected item box
        x1, y1, x2, y2 = self.canvas.bbox("selected")
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        self.coordinate_copy["x"] = center_x
        self.coordinate_copy["y"] = center_y
        
    def paste_items(self):
        mouse_x, mouse_y = self.winfo_pointerx() - self.winfo_rootx(), self.winfo_pointery() - self.winfo_rooty()
        for item in self.copied_items:
            # print("coppied item", copied_item)
            item_type = self.canvas.type(item)

            if item_type == "line":
                coords = self.canvas.coords(item)
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                delta_x = mouse_x  - self.coordinate_copy["x"]
                delta_y = mouse_y  - self.coordinate_copy["y"]
                self.canvas.create_line(x1 + delta_x, y1 + delta_y, x2 + delta_x, y2 + delta_y, fill=self.current_color, width=self.stroke_width)
            elif item_type == "rectangle":
                coords = self.canvas.coords(item)
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                delta_x = mouse_x  - self.coordinate_copy["x"]
                delta_y = mouse_y  - self.coordinate_copy["y"]
                self.canvas.create_rectangle(x1 + delta_x, y1 + delta_y, x2 + delta_x, y2 + delta_y, outline=self.current_color, width=self.stroke_width)
            elif item_type == "polygon":
                coords = self.canvas.coords(item)
                # print(coords)
                # x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                # center_x = (x1 + x2) / 2
                # center_y = (y1 + y2) / 2
                delta_x = mouse_x  - self.coordinate_copy["x"]
                delta_y = mouse_y  - self.coordinate_copy["y"]
                # draw rounded 
                x1=coords[-2]
                y1=coords[1]
                x2=coords[4]
                y2=coords[11]
                draw_rounded_rectangle(self.canvas, x1 + delta_x, y1 + delta_y, x2 + delta_x, y2 + delta_y, radius=25, outline=self.current_color, width=self.stroke_width)
                
    def grouping(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.drawing_line = False
        self.drawing_rect = False
        self.selecting = False
        self.whether_grouping = True
        self.whether_ungrouping = False
        self.ungroupAll = False
        
    def un_grouping(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.drawing_line = False
        self.drawing_rect = False
        self.selecting = False
        self.whether_grouping = False
        self.whether_ungrouping = True
        self.ungroupAll = False
        
    def ungroup_all(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.drawing_line = False
        self.drawing_rect = False
        self.selecting = False
        self.whether_grouping = False
        self.whether_ungrouping = False
        self.ungroupAll = True
        
    def find_color(self,color):
        if color=="k":
            return "black"
        elif color=="r":
            return "red"
        elif color=="g":
            return "green"
        elif color=="b":
            return "blue"
    
    def open_with_txt(self,file_path):
        with open(file_path, 'r') as file:
                    lines = file.readlines()
                    group_stack = []  # Stack to track nested groups
                    grp_arr = []
                    grp_stack=[]
                    num_begin=0
                    for line in lines:
                        line = line.strip()
                        if line.startswith("line"):
                            coordinates = line.split()[1:]
                            print(coordinates)
                            x1, y1, x2, y2 = map(float, coordinates[:4])
                            color = coordinates[-1]
                            color=self.find_color(color)
                            line_id=self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.stroke_width)
                            grp_arr.append(line_id)
                        elif line.startswith("rect"):
                            coordinates = line.split()[1:]
                            x1, y1, x2, y2 = map(float, coordinates[:4])
                            print(coordinates)
                            color=coordinates[-2]
                            color=self.find_color(color)
                            corner_style=coordinates[-1]
                            if corner_style=="s":
                                rect_id=self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=self.stroke_width)
                                grp_arr.append(rect_id)
                                
                            elif corner_style=="r":
                                rect_id=draw_rounded_rectangle(self.canvas, x1, y1, x2, y2, radius=25, outline=color, width=self.stroke_width)
                                grp_arr.append(rect_id)
                        elif line.startswith("begin"):
                            group_stack.append("b")
                            grp_arr.append("b")
                            num_begin=num_begin+1
                        elif line.startswith("end"):
                            group_stack.pop()
                            grp_arr.append("e")

                    if len(grp_stack) > 0:
                        print("Grouping not closed properly")
                        return


                    b_index_stack=[]
                    e_index_stack=[]
                    for i in range(len(grp_arr)):
                        if grp_arr[i]=="b":
                            b_index_stack.append(i)
                    # iterate in opp direction
                    for i in range(len(grp_arr)):
                        if grp_arr[i]=="e":
                            e_index_stack.append(i)

                    while len(b_index_stack)>0:
                        b_index=b_index_stack.pop()
                        # e_index=e_index_stack.pop()
                        # find nearest e_index to b_index
                        e_index=0
                        for i in range(len(e_index_stack)):
                            if e_index_stack[i]>b_index:
                                e_index=e_index_stack[i]
                                # remove e_index from stack
                                e_index_stack.pop(i)
                                break

                        new_grp_arr=[]
                        for i in range(b_index+1,e_index):
                            if grp_arr[i]!="e" and grp_arr[i]!="b":
                                new_grp_arr.append(grp_arr[i])
                        self.grouped_dict[self.index]=new_grp_arr
                        self.index=self.index+1

    def handle_group(self, group_element, grp_arr):
        for child_element in group_element:
            if child_element.tag == 'line':
                begin = child_element.find('begin')
                end = child_element.find('end')
                color = child_element.find('color').text
                x1 = int(begin.find('x').text)
                y1 = int(begin.find('y').text)
                x2 = int(end.find('x').text)
                y2 = int(end.find('y').text)
                color=self.find_color(color)
                line_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.stroke_width)
                grp_arr.append(line_id)
            elif child_element.tag == 'rectangle':
                upper_left = child_element.find('upper-left')
                lower_right = child_element.find('lower-right')
                color = child_element.find('color').text
                corner = child_element.find('corner').text
                x1 = int(upper_left.find('x').text)
                y1 = int(upper_left.find('y').text)
                x2 = int(lower_right.find('x').text)
                y2 = int(lower_right.find('y').text)
                color=self.find_color(color)
                if corner=="rounded":
                    rect_id = draw_rounded_rectangle(self.canvas, x1, y1, x2, y2, radius=25, outline=color, width=self.stroke_width)
                elif corner=="square":
                    rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=self.stroke_width)
                grp_arr.append(rect_id)
            elif child_element.tag == 'group':
                grp_arr.append("b") 
                self.handle_group(child_element, grp_arr)
                grp_arr.append("e") 

    def open_with_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        grp_arr=[]
        print(root)
        for element in root:
            print(element.tag)
            if element.tag == 'line':
                begin = element.find('begin')
                end = element.find('end')
                color = element.find('color').text
                x1 = int(begin.find('x').text)
                y1 = int(begin.find('y').text)
                x2 = int(end.find('x').text)
                y2 = int(end.find('y').text)
                print("hello guys")
                print(x1, y1, x2, y2, color)
                line_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.stroke_width)
                grp_arr.append(line_id)

            elif element.tag == 'rectangle':
                upper_left = element.find('upper-left')
                lower_right = element.find('lower-right')
                color = element.find('color').text
                corner = element.find('corner').text
                x1 = int(upper_left.find('x').text)
                y1 = int(upper_left.find('y').text)
                x2 = int(lower_right.find('x').text)
                y2 = int(lower_right.find('y').text)
                if corner=="rounded":
                    rect_id = draw_rounded_rectangle(self.canvas, x1, y1, x2, y2, radius=25, outline=color, width=self.stroke_width)
                elif corner=="square":
                    rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=self.stroke_width)
                grp_arr.append(rect_id)

            elif element.tag == 'group':
                grp_arr.append("b")
                self.handle_group(element, grp_arr)
                grp_arr.append("e")

        # find numbr of "b" in grp_arr
        count_b=grp_arr.count("b")
        if count_b==0:
            print("Grouping not found")
            return
        
        b_index_stack=[]
        e_index_stack=[]
        for i in range(len(grp_arr)):
            if grp_arr[i]=="b":
                b_index_stack.append(i)
        # iterate in opp direction
        for i in range(len(grp_arr)):
            if grp_arr[i]=="e":
                e_index_stack.append(i)
        while len(b_index_stack)>0:
            b_index=b_index_stack.pop()
            # e_index=e_index_stack.pop()
            # find nearest e_index to b_index
            e_index=0
            for i in range(len(e_index_stack)):
                if e_index_stack[i]>b_index:
                    e_index=e_index_stack[i]
                    # remove e_index from stack
                    e_index_stack.pop(i)
                    break

            new_grp_arr=[]
            for i in range(b_index+1,e_index):
                if grp_arr[i]!="e" and grp_arr[i]!="b":
                    new_grp_arr.append(grp_arr[i])
            self.grouped_dict[self.index]=new_grp_arr
            self.index=self.index+1

    def open_file(self):
        # Assuming 'canvas' is your Canvas object
        self.canvas.delete("all")

        file_path = filedialog.askopenfilename(filetypes=[("TXT files", "*.txt"),("XML files", "*.xml")])
        if file_path:
            print("Opened file:", file_path)
            if file_path.endswith('.txt'):
                self.open_with_txt(file_path)
            elif file_path.endswith('.xml'):
                self.open_with_xml(file_path)
                
                
                
    def recursive_convert_to_xml(self, current_list):
        xml = ""
        print("hello")
        for item in self.reversed_items:
            f = 0
            for ii in self.deleted:
                if item == ii:
                    f = 1
                    break
            if f == 1:
                continue

            if len(current_list) != 0 and set(item).issubset(set(current_list)) == False:
                continue
            if len(item) == 1:
                if (self.canvas.type(item[0]) == "line"):

                    coords = self.canvas.coords(item[0])
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    color = self.canvas.itemcget(item[0], "fill")
                    xml += "<line>\n"

                    xml += "\t<begin>\n"
                    xml += "\t<x>"+str(int(x1))+"</x>\n"
                    xml += "\t<y>"+str(int(y1))+"</y>\n"
                    xml += "\t</begin>\n"

                    xml += "\t<end>\n"
                    xml += "\t<x>"+str(int(x2))+"</x>\n"
                    xml += "\t<y>"+str(int(y2))+"</y>\n"
                    xml += "\t</end>\n"

                    xml += "\t<color>"+color+"</color>\n"
                    xml += "</line>\n"
                    self.deleted.append(item)
                elif (self.canvas.type(item[0]) == "rectangle"):
                    coords = self.canvas.coords(item[0])
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    color = self.canvas.itemcget(item[0], "outline")
                    xml += "<rectangle>\n"

                    xml += "\t<upper-left>\n"
                    xml += "\t<x>"+str(int(x1))+"</x>\n"
                    xml += "\t<y>"+str(int(y1))+"</y>\n"
                    xml += "\t</upper-left>\n"

                    xml += "\t<lower-right>\n"
                    xml += "\t<x>"+str(int(x2))+"</x>\n"
                    xml += "\t<y>"+str(int(y2))+"</y>\n"
                    xml += "\t</lower-right>\n"

                    xml += "\t<color>"+color+"</color>\n"

                    xml += "\t<corner>square</corner>\n"
                    xml += "</rectangle>\n"
                    self.deleted.append(item)
                elif (self.canvas.type(item[0]) == "polygon"):
                    coords = self.canvas.coords(item[0])
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    color = self.canvas.itemcget(item[0], "outline")
                    xml += "<rectangle>\n"

                    xml += "\t<upper-left>\n"
                    xml += "\t<x>"+str(int(x1))+"</x>\n"
                    xml += "\t<y>"+str(int(y1))+"</y>\n"
                    xml += "\t</upper-left>\n"

                    xml += "\t<lower-right>\n"
                    xml += "\t<x>"+str(int(x2))+"</x>\n"
                    xml += "\t<y>"+str(int(y2))+"</y>\n"
                    xml += "\t</lower-right>\n"

                    xml += "\t<color>"+color+"</color>\n"

                    xml += "\t<corner>rounded</corner>\n"
                    xml += "</rectangle>\n"
                    self.deleted.append(item)

            else:
                xml += "<group>\n"
                self.deleted.append(item)
                xml += self.recursive_convert_to_xml(item)
                xml += "</group>\n"

        return xml

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xml", filetypes=[("Text files", "*.xml")])
        if file_path:
            with open(file_path, "w") as f:

                my_dict = {}
                i = 0
                for it in self.canvas.find_all():
                    my_dict[i] = it
                    i += 1
                for key, value in self.grouped_dict.items():
                    my_dict[i] = value
                    i += 1
                self.reversed_items = list(my_dict.items())[::-1]
                temp = []
                for item in self.reversed_items:
                    if type(item[1:][0]) == int:
                        ex = []
                        ex.append(item[1:][0])
                        temp.append(ex)
                    else:
                        temp.append(item[1:][0])

                self.reversed_items = temp
                print(self.reversed_items)
                data=""
                data+="<root>\n"
                data+= self.recursive_convert_to_xml([])
                data+="</root>\n"
                
                print(data)
                f.write(data)
                self.deleted = []

                f.close()

    def color_func(self, color):
        if color == "black":
            return "k"
        else:
            return color[0]


    def recursive_convert_to_ascii(self, current_list):
        xml = ""
        print("hello")
        for item in self.reversed_items:
            f = 0
            for ii in self.deleted:
                if item == ii:
                    f = 1
                    break
            if f == 1:
                continue

            if len(current_list) != 0 and set(item).issubset(set(current_list)) == False:
                continue
            if len(item) == 1:
                if (self.canvas.type(item[0]) == "line"):

                    coords = self.canvas.coords(item[0])
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    color = self.canvas.itemcget(item[0], "fill")
                    

                    xml += "line "+str(int(x1))+" "+str(int(y1)) + \
                        " "+str(int(x2))+" "+str(int(y2))+" "+self.color_func(color)+"\n"

                    self.deleted.append(item)

                elif (self.canvas.type(item[0]) == "rectangle"):
                    coords = self.canvas.coords(item[0])
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    color = self.canvas.itemcget(item[0], "outline")

                    xml += "rect "+str(int(x1))+" "+str(int(y1))+" " + \
                        str(int(x2))+" "+str(int(y2))+" "+self.color_func(color)+" s\n"

                    self.deleted.append(item)

                elif (self.canvas.type(item[0]) == "polygon"):
                    coords = self.canvas.coords(item[0])
                    x1=coords[-2]
                    y1=coords[1]
                    x2=coords[4]
                    y2=coords[11]
                    color = self.canvas.itemcget(item[0], "outline")

                    xml += "rect "+str(int(x1))+" "+str(int(y1))+" " + \
                        str(int(x2))+" "+str(int(y2))+" "+self.color_func(color)+" r\n"
                    self.deleted.append(item)

            else:
                xml += "begin\n"
                self.deleted.append(item)
                xml += self.recursive_convert_to_ascii(item)
                xml += "end\n"

        return xml

    def save_to_ASCII(self):

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:

                my_dict = {}
                i = 0
                for it in self.canvas.find_all():
                    my_dict[i] = it
                    i += 1
                for key, value in self.grouped_dict.items():
                    my_dict[i] = value
                    i += 1
                self.reversed_items = list(my_dict.items())[::-1]
                temp = []
                for item in self.reversed_items:
                    if type(item[1:][0]) == int:
                        ex = []
                        ex.append(item[1:][0])
                        temp.append(ex)
                    else:
                        temp.append(item[1:][0])

                self.reversed_items = temp
                print(self.reversed_items)
                data = self.recursive_convert_to_ascii([])
                print(data)
                self.deleted=[]
                f.write(data)
                f.close()
                


if __name__ == "__main__":
    
    app = PaintApp()
    app.mainloop()