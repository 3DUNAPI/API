import tkinter
from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog
import requests
import shutil
import json

import os
import sys
import math
import time





def callback():
    headers = {
        'Content-Type': 'application/json',
        'appid':entry_A.get(),
    }

    data = '{"username":"' + entry_U.get() + '","password":"' + entry_P.get() + '"}'
 
    response = requests.get('https://api.3dusernet.com/3dusernetApi/api/sign_in.json', headers=headers, data=data)
    text_area.insert(END, response.text + '\n')
    x = json.loads(response.text)
    show_token.insert(END, x['token'])
    rb_poj.invoke()
    



def listproj(table):
    print("listproj")
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }

    response2 = requests.get('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers)
    x = json.loads(response2.text)
    try:
        y = x['projects']
        for i in table.get_children():
            table.delete(i)
        if type(y) is list:
            if y == []:
                table.insert('','end', values = ( "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    table.insert('','end', values = ( y[i]['id'], y[i]['name']))
                    i +=1
        else:
            print(type(y))
            table.insert('','end', values = ( y['id'], y['name']))

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def add_Project():

    def sendProj():
        
        # send data to add Project
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        print (type( ent_pname.get()))
        # the line below is for text widget
        # print (txt_pdesc.get("1.0",END))
        print (txt_pdesc.get())
               
        print (lb_group.get(lb_group.curselection()[0]))
        print (type(ent_lat.get()))
        print (type(ent_lon.get()))

        data = '{"name":"'+ ent_pname.get() +'","description": "'+ txt_pdesc.get() +'","group_id": ' + str(lb_group.get(lb_group.curselection()[0])) + ',"latitude": '+ str(ent_lat.get()) +',"longitude": '+ str(ent_lon.get()) +'}'
        # create \n instead of single line characters
        data2 = (json.loads(data, strict=False))
        data3 = str(data)
        print(data2)
        print(data3)
        response = requests.post('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
        print (response.text)
        t.destroy
    
    t = Toplevel()
    t.title("Add new Project")
    lbl_pname = Label(t,text="Project Name").pack()
    ent_pname = Entry(t, background="grey", width = 15)
    ent_pname.pack()
    lbl_pdesc = Label(t,text="Project Description").pack()
    txt_pdesc = Entry(t, background="grey", width = 45)
    #txt_pdesc = Text(t, background="grey", width = 45, height = 10) - can't get this to send correctly
    txt_pdesc.pack()
    lbl_group = Label(t,text="Select a Group").pack()
    lb_group = Listbox(t)
    lb_group.pack()
    lbl_lat = Label(t,text="Latitude(Decimal)").pack()
    ent_lat = Entry(t, background="grey", width = 10)
    ent_lat.pack()
    lbl_lon = Label(t,text="Longitute(Decimal)").pack()
    ent_lon = Entry(t, background="grey", width = 10)
    ent_lon.pack()
    bt_Create = Button(t,text = "Create Project", command=lambda: sendProj())
    bt_Create.pack()
    bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
    bt_Cancel.pack()
    
    # get group data and add to listbox
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }

    response = requests.get('https://api.3dusernet.com/3dusernetApi/api/groups.json', headers=headers)
    x = json.loads(response.text)
    try:
        y = json.loads(x)
        if type(y) is list:
            print(y[1])
            print(len(y))
            i=0
            while i < len(y) :        
                lb_group.insert(END, y[i]['id'])
                i +=1
        else:
            print(type(y))           
            lb_group.insert(END, y['id'])

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise




def listlib(table):
    print("listlib")
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }

    response = requests.get('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers)
    x = json.loads(response.text)
    try:
        y = x['libraries']
        for i in table.get_children():
            table.delete(i)
        if type(y) is list:
            if y == []:
                table.insert('','end', values = ( "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    table.insert('','end', values = ( y[i]['id'], y[i]['name']))
                    i +=1
        else:
            print(type(y))
            table.insert('','end', values = ( y['id'], y['name']))

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    
def listpc():
    print("listPC")
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = listbox.focus()
    print (listbox.item(uid)['values'][0])
    data = '{ "id": '+ str(listbox.item(uid)['values'][0]) + '}'
    print (v.get())
    if v.get() ==1 :
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
    else:
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)       
    x = json.loads(response.text)
    y = x['pointclouds']
    for i in lb_assets.get_children():
        lb_assets.delete(i)
    try:
                             
        if type(y) is list:
            if y == []:
                lb_assets.insert('','end', values = ( "---", "<no data>"))
            else:
                print((y[0]['file_name']))
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['id'], y[i]['file_name']))
                    i +=1
        else:
            print(type(y['file_name']))
            lb_assets.insert(END, y['file_name'])

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def listmod():
    print("listMD")

    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = listbox.focus()
    print (listbox.item(uid)['values'][0])
    data = '{ "id": '+ str(listbox.item(uid)['values'][0]) + '}'
    print (v.get())
    if v.get() ==1 :
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
    else:
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)       
    x = json.loads(response.text)
    y = x['models']

    for i in lb_assets.get_children():
        lb_assets.delete(i)
    
    if v.get() ==1 :                             
        if type(y) is list:
            if y == []:
                lb_assets.insert('','end', values = ( "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['models']['id'], y[i]['models']['file_name']))
                    i +=1
        else:
            
            lb_assets.insert('','end', values = ( y['models']['id'], y['models']['file_name']))
    else:
        if type(y) is list:
            if y == []:
                lb_assets.insert('','end', values = ( "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['id'], y[i]['file_name']))
                    i +=1
        else:
            lb_assets.insert('','end', values = ( y['id'], y['file_name']))


def listsnaps():
    print("listSnaps")
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = listbox.focus()
    print (listbox.item(uid)['values'][0])
    data = '{ "id": '+ str(listbox.item(uid)['values'][0]) + '}'
    print (v.get())
    if v.get() ==1 :
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
    else:
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)       
    x = json.loads(response.text)
    y = x['snapshots']
    
    for i in lb_assets.get_children():
        lb_assets.delete(i)
    try:
                             
        if type(y) is list:
            if y == []:
                lb_assets.insert('','end', values = ( "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['id'], y[i]['name']))
                    i +=1
        else:
            print(type(y['name']))
            lb_assets.insert('','end', values = ( y['id'], y['name']))

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def updt_gr(event):
    print("update_group")
    print (v2.get())
    if v2.get() == 0:
        rb_pc.invoke()
    elif v2.get() ==1:
        listpc()
    elif v2.get() ==2:
        listmod()
    elif v2.get() ==3:
        listsnaps()       
        


def updt_as(event):
    print("update_asset")
    # update information on right side, required before download is available.
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = lb_assets.focus()
    print (lb_assets.item(uid)['values'][0])
    data = '{ "id": '+ str(lb_assets.item(uid)['values'][0]) + '}'
    print (v2.get())
    if str(lb_assets.item(uid)['values'][0]) =="---" :
        print("no data")
    else:
        if v2.get() == 1 :
            print ("pc")
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['point_cloud']

        elif v2.get()==2 :
            print("mod")
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['models']
            
 
        elif v2.get()==3 :
            print("snap")
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/snapshots.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['snapshots']
 
 
        else:
            print("no selection")
            
        uida.set ( y['id'])
        if v2.get() == 3 :
            name.set ( y['name']+ '.jpg')
            downl.set ( y['image'])
        else:
            name.set (y['file_name'])
            downl.set ( y['s3_file_download'])
        if v2.get() == 3 :
            size.set ( 'not availabe')
        else:           
            size.set ( y['file_size'])
        cr8td.set ( y['created'])
                            
         # to be completed once api command is sent                          
        mod.set ( "not available")
        


def download():
    def directoryBox():
        try:
            options = {}
            options['title'] = "select folder"
            options['mustexist'] = False
            fileName = filedialog.askdirectory(**options)
            if fileName == "":
                return None
            else:
                return fileName             
        except:
            textbox.insert(END, "There was an error opening ")
            textbox.insert(END, fileopen)
            textbox.insert(END, "\n") 
    print("download")
    if lb_assets.focus() == "" :
        print('no selection')
    else:
        folder = directoryBox()
        print(folder)
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        uid = lb_assets.focus()

        print (lb_assets.item(uid)['values'][0])
        data = '{ "id": '+ str(lb_assets.item(uid)['values'][0]) + '}'
        print (v2.get())
        if str(lb_assets.item(uid)['values'][0]) =="---" :
            print("no data")
        else:
            downl.get
            r = requests.get(downl.get(),stream=True)
            with open(folder + '/' + name.get(), 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            return folder
            if v2.get() == 1 :
                print ("pc")
                response = requests.get('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', headers=headers, data=data)
                x = json.loads(response.text)
                y = json.loads(x)
                r = requests.get(y["s3_file_download"],stream=True)
                with open(folder + '/' + y["file_name"], 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return folder
            elif v2.get()==2 :
                print("mod")
                response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models.json', headers=headers, data=data)
                x = json.loads(response.text)
                y = json.loads(x)
                r = requests.get(y["s3_file_download"],stream=True)
                with open(folder + '/' + y["file_name"], 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return folder
            else:
                print("snap - not operational yet")

def upload_pc():
    def sendpc():
        uid = listbox2.focus()
        print (listbox2.item(uid)['values'][0])
        HOST = '34.242.73.114'
        PORT = 8080
        api_url = 'http://{}:{}'.format(HOST, PORT)


        file_size = os.path.getsize(filename)
        max_byte_length = 1024 * 1024 * 5 # 5M
        headers = {'Filename': os.path.basename(filename).encode('utf-8')}        
        headers['Token'] = show_token.get("1.0",'end-1c')
        headers['Filesize'] = str(file_size)
        headers['Projectid'] = str(listbox2.item(uid)['values'][0])
        headers['Arguments'] = ent_pcattrib.get()
        headers['filesize'] = str(file_size)
        with open(filename, 'rb') as file:
            chunk_count = math.ceil(float(file_size) / max_byte_length)
            print("Total chunk count:", chunk_count)

            retry_timeout = 1
            sent_chunk_count = 0
            while True:
                headers['Range'] = "bytes={}/{}-{}".format(sent_chunk_count, int(chunk_count), file_size)

                data = file.read(max_byte_length)
                upload_endpoint = os.path.join(api_url, 'content', 'upload')
                print (headers)
                print(upload_endpoint)

                try:
                    response = requests.post(upload_endpoint, headers=headers, data=data)
                    if response.ok:
                        print('{}. chunk sent to server'.format(sent_chunk_count + 1))
                        sent_chunk_count += 1
                except requests.exceptions.RequestException as e:
                    print('Error while sending chunk to server. Retrying in {} seconds'.format(retry_timeout))
                    print (e)
                    time.sleep(retry_timeout)

                    # Sleep for max 10 seconds
                    if retry_timeout < 10:
                        retry_timeout += 1
                    continue

                if sent_chunk_count >= chunk_count:
                    t.destroy
                    return True

            return False


        
    print("upload pointcloud")
    
    filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("las files","*.las"),("laz files","*.laz"),("e57 files","*.e57"),("xyz files","*.xyz"),("ply files","*.ply")))
    print (filename)
    fn = filename.split("/")[len(filename.split("/"))-1]
    t = Toplevel()
    t.title("Upload Pointcloud")
    lbl_pname = Label(t,text="Project Name").pack()
    v3 = IntVar()
    rb_poj2 = Radiobutton(t, text="Projects", command=lambda: listproj(listbox2), variable=v3, value=1).pack()
    rb_lib2 = Radiobutton(t, text="Libraries", command=lambda: listlib(listbox2), variable=v3, value=2).pack()
    lb_header2 = ['id', 'name']
    listbox2 = ttk.Treeview(t, columns=lb_header, show="headings")
    listbox2.heading('id', text="id")
    listbox2.column('id',minwidth=0,width=40, stretch=NO)
    listbox2.heading('name', text="Name")
    listbox2.column('name',minwidth=0,width=150, stretch=NO)
    listbox2.pack()
    lbl_pcattrib = Label(t,text="Attributes").pack()
    ent_pcattrib = Entry(t)
    ent_pcattrib.pack()
    ent_pcattrib.insert(0, "-f xyzirgb -a RGB -intensity-range 0 65535 -color-range 0 255")
    btn_sendfile = Button(t,text ="Send File", command=lambda: sendpc()).pack()
    
    
def upload_md():
    print("upload model")
            
def mv_md():
    print ("move model")

def cp_md():
    print("copy model")
    
root = Tk()
root.title('Model Definition')
root.geometry('{}x{}'.format(650, 500))


# create all of the main containers
top_frame = Frame(root, bg='purple', width=450, height=50, pady=3)
center = Frame(root, bg='purple', width=50, height=40, padx=3, pady=3)
btm_frame = Frame(root, bg='white', height=90, pady=3)


# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=3, sticky="ew")

# create the widgets for the top frame
model_label = Label(top_frame, text='3DUserNet API Test',font=("Arial", 16), bg="purple", fg="white")
user_label = Label(top_frame, text='UserName:', bg="purple",fg="white")
pass_label = Label(top_frame, text='Password:', bg="purple",fg="white")
app_label = Label(top_frame, text='AppID:', bg="purple",fg="white")
entry_U = Entry(top_frame, background="white", width = 15)
entry_P = Entry(top_frame, show="*", background="white", width = 15)
entry_A = Entry(top_frame, background="white", width = 15)
get_token = Button(top_frame, bg="purple", highlightbackground="purple", text="OK", command=callback)
token_label = Label(top_frame, text='Token:', bg="purple",fg="white")
show_token = Text(top_frame, height = 1,background="grey", width =30)

# layout the widgets in the top frame
model_label.grid(row=0, columnspan=6)
user_label.grid(row=1, column=0)
pass_label.grid(row=1, column=2)
app_label.grid(row=1, column=4)
entry_U.grid(row=1, column=1)
entry_P.grid(row=1, column=3)
entry_A.grid(row=1, column=5)
get_token.grid(row=2,column=0)
token_label.grid(row=2,column=1)
show_token.grid(row=2,column=2,columnspan=3)

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

ctr_left = Frame(center, bg='grey', width=100, height=190,padx=3, pady=3)
ctr_mid = Frame(center, bg='grey', width=100, height=190, padx=3, pady=3)
ctr_right = Frame(center, bg='grey', width=250, height=190, padx=3, pady=3)

ctr_left.grid(row=0, column=0, sticky="ns")
ctr_mid.grid(row=0, column=1, sticky = "nsew")
ctr_right.grid(row=0, column=2, sticky="ns")

# create the widgets for the centre_left frame
ctr_left.grid_rowconfigure(1, weight=1)
ctr_left.grid_columnconfigure(1, weight=1)

v = IntVar()

rb_poj = Radiobutton(ctr_left, text="Projects", command=lambda: listproj(listbox), variable=v, value=1, bg = "grey")
rb_lib = Radiobutton(ctr_left, text="Libraries", command=lambda: listlib(listbox), variable=v, value=2, bg = "grey")
lb_header = ['id', 'name']
listbox = ttk.Treeview(ctr_left, columns=lb_header, show="headings")
listbox.heading('id', text="id")
listbox.column('id',minwidth=0,width=40, stretch=NO)
listbox.heading('name', text="Name")
listbox.column('name',minwidth=0,width=150, stretch=NO)
listbox.bind("<ButtonRelease-1>", updt_gr)

#replaced with ttk tree   - listbox = Listbox(ctr_left)
bt_addpr = Button(ctr_left,text="New Project", highlightbackground="grey", command=lambda: add_Project())

# layout the widgets in the centre_left frame

rb_poj.grid(row=0)
rb_lib.grid(row=1)
listbox.grid(row=2)
bt_addpr.grid(row=3)

# create the widgets for the centre_mid frame
ctr_mid.grid_rowconfigure(1, weight=1)
ctr_mid.grid_columnconfigure(1, weight=1)

v2 = IntVar()
rb_pc = Radiobutton(ctr_mid, text="Pointclouds", command=lambda: listpc(), variable=v2, value=1, bg = "grey")
rb_md = Radiobutton(ctr_mid, text="Models", command=lambda: listmod(), variable=v2, value=2, bg = "grey")
rb_ss = Radiobutton(ctr_mid, text="Snapshots", command=lambda: listsnaps(), variable=v2, value=3, bg = "grey")
lb_assets = ttk.Treeview(ctr_mid, columns=lb_header, show="headings")

#replaced with ttk tree  - lb_assets = Listbox(ctr_mid)
lb_assets.heading('id', text="id")
lb_assets.column('id',minwidth=0,width=40, stretch=NO)
lb_assets.heading('name', text="Name")
lb_assets.column('name',minwidth=0,width=150, stretch=NO)
lb_assets.bind("<ButtonRelease-1>", updt_as)

bt_downl = Button(ctr_mid,text="Download", command=lambda: download(), highlightbackground="grey")



# layout the widgets in the centre_left frame
rb_pc.grid(row=0)
rb_md.grid(row=1)
rb_ss.grid(row=2)
lb_assets.grid(row=3)
bt_downl.grid(row=4)


# create the widgets for the centre_left frame
uida = StringVar()
lbl_id = Label(ctr_right,width =30, textvariable = uida, font=("Arial", 12), anchor='w', bg="grey", fg="black")
uida.set("id")

name = StringVar()
lbl_name = Label(ctr_right,width =30, textvariable = name, anchor='w',font=("Arial", 12), bg="grey", fg="black")
name.set('name')

downl = StringVar()
lbl_downl = Label(ctr_right,width =30, textvariable = downl, anchor='w', font=("Arial", 12), bg="grey", fg="black")
downl.set("download link")

size = StringVar()
lbl_size = Label(ctr_right,width =30, textvariable = size,  anchor='w', font=("Arial", 12), bg="grey", fg="black")
size.set("size")

cr8td = StringVar()
lbl_cr8td = Label(ctr_right,width =30, textvariable = cr8td, anchor='w', font=("Arial", 12), bg="grey", fg="black")
cr8td.set("created")

mod = StringVar()
lbl_mod =Label(ctr_right,width =30, textvariable = mod, anchor='w', font=("Arial", 12), bg="grey", fg="black")
mod.set("model transformation")

bt_uplpc = Button(ctr_right,text = "Upload Pointcloud", command=lambda: upload_pc(), anchor='s', highlightbackground="grey")
bt_uplmd = Button(ctr_right,text = "Upload Model", command=lambda: upload_md(), anchor='s', highlightbackground="grey")
bt_mvmd = Button(ctr_right,text = "Move Model", command=lambda: mv_md(), anchor='s', highlightbackground="grey")
bt_cpmd = Button(ctr_right,text = "copy Model", command=lambda: cp_md(), anchor='s', highlightbackground="grey")

# layout the widgets in the centre_left frame
lbl_id.grid(row=0)
lbl_name.grid(row=1)
lbl_downl.grid(row=2)
lbl_size.grid(row=3)
lbl_cr8td.grid(row=4)
lbl_mod.grid(row=5)
bt_uplpc.grid(row=6)
bt_uplmd.grid(row=7)
bt_mvmd.grid(row=8)
bt_cpmd.grid(row=9)

# create the widgets for the bottom frame
btm_frame.grid_rowconfigure(0, weight=1)
btm_frame.grid_columnconfigure(0, weight=1)

text_area= Text(btm_frame, height = 5,background="cyan")

# layout the widgets in the bottom frame
text_area.grid(row=0,column=0,sticky=W+E)

root.mainloop()
