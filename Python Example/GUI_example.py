import tkinter
from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from PIL import Image, ImageTk
import shutil
import json
import os
import sys
import math
import time
import ast
import urllib.request
import io


def encoder(string, key):
    #create an encrypted version so password isn't stored in its raw form
    #WARNING this is not a proper encrytion solution, just a precautionary measure for storing single passwords
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(string[i] + key_c % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return (encoded_string)


def decoder(string, key) :
    #decoder for the above encoder using character shift technique
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) - ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return (encoded_string)
    

def callback():
    #sign in to API using defined credentials, return will be active token
    headers = {
        'Content-Type': 'application/json',
        'appid':entry_A.get(),
    }

    data = '{"username":"' + entry_U.get() + '","password":"' + entry_P.get() + '"}'
    response = requests.get('https://api.3dusernet.com/3dusernetApi/api/sign_in.json', headers=headers, data=data)

    # notify user and add tocken
    text_area.delete('1.0', 'end')
    text_area.insert(END, response.text + '\n')
    x = json.loads(response.text)
    show_token.insert(END, x['token'])

    # if 'save detials' is active, create a config file with the user details contained. Note file is saved to the default folder.
    if sve.get() == 1:
        f= open("config.txt","w+")
        f.write (entry_U.get() + "\n")
        enc = encoder((str(entry_P.get())).encode(),(str(entry_U.get())).encode())
        # binary encode password before saving
        f.write(str(enc.encode('utf-8')) + "\n")
        f.write(entry_A.get())
        f.close() 
        
    rb_poj.invoke()
    


def listproj(table):
    # request all projects for the signed in user
    print("listproj")
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }

    response = requests.get('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers)
    x = json.loads(response.text)

    # add project list to the table, note the difference for multiple and single returns.
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

def new_Container():
    # create new project or library
    if v.get() == 1:
        add_Project()
    else:
        add_Library()
        


def upd_Container():
    # update a project or library
    if v.get() == 1:
        upd_Project()
    else:
        upd_Library()


def add_Project():

    def sendProj():
        
        #Send data to API to add Project
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        
        # test to see is there is focus in the group table
        try:
            print (listbox4.item(listbox4.focus())['values'][0])
        except IndexError:
            print("Error - need to select Group")
            text_area.insert(END,"Error - need to select Group")
            return
        
        # sending data to API
        data = '{"name":"'+ ent_pname.get() +'","description": "'+ txt_pdesc.get() +'","group_id": ' + str(listbox4.item(listbox4.focus())['values'][0]) + ',"latitude": '+ str(ent_lat.get()) +',"longitude": '+ str(ent_lon.get()) +'}'
        response = requests.post('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        if v.get() ==1:
            listproj(listbox)
        t.destroy()

    #Build the interface for the pop-up UI
    text_area.delete('1.0', 'end')
    text_area.insert(END, 'Opening add project menu' + '\n')   
    t = Toplevel()
    t.title("Add new Project")
    lbl_pname = Label(t,text="Project Name").pack()
    ent_pname = Entry(t, background="grey", width = 15)
    ent_pname.pack()
    lbl_pdesc = Label(t,text="Project Description").pack()
    txt_pdesc = Entry(t, background="grey", width = 45)
    txt_pdesc.pack()
    lbl_group = Label(t,text="Select a Group").pack()
    lb_header4 = ['id', 'name']
    listbox4 = ttk.Treeview(t, columns=lb_header, show="headings")
    listbox4.heading('id', text="id")
    listbox4.column('id',minwidth=0,width=40, stretch=NO)
    listbox4.heading('name', text="Name")
    listbox4.column('name',minwidth=0,width=150, stretch=NO)
    listbox4.pack()
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
        y = x['groups']
        if type(y) is list:
            i=0
            while i < len(y) :
                listbox4.insert('','end', values= (y[i]['id'], y[i]['name']))
                i +=1
        else:
            print(type(y))           
            
    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def upd_Project():
    
    def updProj():
        
        #Update the Project
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        
        # test to see is there is focus in the group table
        try:
            print (listbox5.item(listbox5.focus())['values'][0])
        except IndexError:
            print("need to select a Group")
            text_area.insert(END, "Error - need to select a group"+ '\n')
            return

        # send data to API
        data = '{"name":"'+ ent_pname.get() +'","description": "'+ txt_pdesc.get() +'","group_id": ' + str(listbox5.item(listbox5.focus())['values'][0]) + ',"latitude": '+ str(ent_lat.get()) +',"longitude": '+ str(ent_lon.get()) +',"id":'+ str(ProjID) + '}'
        response = requests.put('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
        print (response.text)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        if v.get() ==1:
            listproj(listbox)
        t.destroy()
    
    #Get ID of selected Project
    if v.get()==1:
        try:
            ProjID = listbox.item(listbox.focus())['values'][0]
        except IndexError:
            print("need to select a project")
            text_area.insert(END, "Error - need to select a project"+ '\n')
            return
        print(ProjID)

        #Get Project Details
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }

        data = '{"id":'+ str(ProjID) +'}'
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
        x = json.loads(response.text)
        text_area.delete('1.0', 'end')
        text_area.insert(END, "Opening project update menu" + '\n')
        currGroup = 'Current Group is: ' + str(x['projects']['group_id'])

        #Enter New Details (Prepopulate with Existing Details)
        #Build the interface for the pop-up UI
        t = Toplevel()
        t.title("Update Project")
        lbl_pname = Label(t,text="Project Name").pack()
        ent_pname = Entry(t, background="grey", width = 15)
        ent_pname.insert(END, str(x['projects']['name']))
        ent_pname.pack()
        lbl_pdesc = Label(t,text="Project Description").pack()
        txt_pdesc = Entry(t, background="grey", width = 45)
        txt_pdesc.insert(END, str(x['projects']['description']))
        txt_pdesc.pack()
        lbl_group = Label(t,text="Select a Group").pack()
        lbl_group2 = Label(t,text=currGroup).pack()     
        lb_header5 = ['id', 'name']
        listbox5 = ttk.Treeview(t, columns=lb_header, show="headings")
        listbox5.heading('id', text="id")
        listbox5.column('id',minwidth=0,width=40, stretch=NO)
        listbox5.heading('name', text="Name")
        listbox5.column('name',minwidth=0,width=150, stretch=NO)
        listbox5.pack()
        lbl_lat = Label(t,text="Latitude(Decimal)").pack()
        ent_lat = Entry(t, background="grey", width = 10)
        ent_lat.insert(END, str(x['projects']['latitude']))
        ent_lat.pack()
        lbl_lon = Label(t,text="Longitute(Decimal)").pack()
        ent_lon = Entry(t, background="grey", width = 10)
        ent_lon.insert(END, str(x['projects']['longitude']))
        ent_lon.pack()
        bt_Create = Button(t,text = "Update Project", command=lambda: updProj())
        bt_Create.pack()
        bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
        bt_Cancel.pack()

        # get group data and add to listbox
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/groups.json', headers=headers)
        x2 = json.loads(response.text)
        try:
            y = x2['groups']
            if type(y) is list:
                print(y[1])
                print(len(y))
                i=0
                while i < len(y) :
                    listbox5.insert('','end', values= (y[i]['id'], y[i]['name']))
                    i +=1
            else:
                print(type(y))
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")  
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    else:
        print('Please select a Project')
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'Please select a Project')


def add_Library():

    def sendLib():
        
        #Send data to add Library
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        data = '{"name":"'+ ent_lname.get() +'","description": "'+ txt_ldesc.get() +'"}'
        response = requests.post('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        if v.get() ==2:
            listlib(listbox)
        t.destroy()
        
    #Build the interface for the pop-up UI

    text_area.delete('1.0', 'end')
    text_area.insert(END, 'Opening add library menu' + '\n')
    t = Toplevel()
    t.title("Add new Library")
    lbl_lname = Label(t,text="Library Name").pack()
    ent_lname = Entry(t, background="grey", width = 15)
    ent_lname.pack()
    lbl_ldesc = Label(t,text="Library Description").pack()
    txt_ldesc = Entry(t, background="grey", width = 45)
    txt_ldesc.pack()  
    bt_Create = Button(t,text = "Create Library", command=lambda: sendLib())
    bt_Create.pack()
    bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
    bt_Cancel.pack()



def upd_Library():

    def updLib():
        
        #Send Data to update the Library
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        data = '{"name":"'+ ent_lname.get() +'","description": "'+ txt_ldesc.get() +'", "id":'+str(LibID)+'}'
        response = requests.put('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        if v.get() ==2:
            listlib(listbox)
        t.destroy()
        print('Updated Library')

    #Check Library List is selected
    if v.get()==2:
        #Get ID of selected Library
        try:
             LibID = listbox.item(listbox.focus())['values'][0]
        except IndexError:
            print("need to select a library")
            text_area.insert(END, "Error - need to select a library"+ '\n')
            return 

        #Get Library Details
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        data = '{"id":'+ str(LibID) +'}'
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)
        x = json.loads(response.text)
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'Opening library update menu' + '\n')
        

        #Build the interface for the pop-up UI
        t = Toplevel()
        t.title("Update Library")
        lbl_lname = Label(t,text="Library Name").pack()
        ent_lname = Entry(t, background="grey", width = 15)
        ent_lname.insert(END,str(x['libraries']['name']))
        ent_lname.pack()
        lbl_ldesc = Label(t,text="Library Description").pack()
        txt_ldesc = Entry(t, background="grey", width = 45)
        txt_ldesc.insert(END,str(x['libraries']['description']))
        txt_ldesc.pack()  
        bt_update = Button(t,text = "Update Library", command=lambda: updLib())
        bt_update.pack()
        bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
        bt_Cancel.pack()

    else: 
        print('Please select a Library')
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'Please select a Library')
        
    print('Update Library')




def listlib(table):
    
    # Call for a list of user libraries and add to table
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

    # Call for a list of user pointclouds and add to asset table - works for both projects and librby containers
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = listbox.focus()
    try:
        print (listbox.item(uid)['values'][0])
    except IndexError:
        print ("Error - need to select a project/library")
        text_area.insert(END, "Error - need to select a project/library"+ '\n')
        return
    data = '{ "id": '+ str(listbox.item(uid)['values'][0]) + '}'


    # detemine what type of container has been selected
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
                lb_assets.insert('','end', values = ( "---", "---", "<no data>"))
            else:
                print((y[0]['file_name']))
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['id'], "---", y[i]['file_name']))
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

    # Call for a list of user models and adds to asset table - works for both projects and librby containers
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = listbox.focus()
    try:
        print (listbox.item(uid)['values'][0])
    except IndexError:
        print ("Error - need to select a project/library")
        text_area.insert(END, "Error - need to select a project/library"+ '\n')
        return

    data = '{ "id": '+ str(listbox.item(uid)['values'][0]) + '}'
    
    # detemine what type of container has been selected
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
                lb_assets.insert('','end', values = ( "---", "---", "<no data>"))
            else:
                i=0
                while i < len(y) :
                    
                    lb_assets.insert('','end', values = ( y[i]['models']['id'], y[i]['model_project_location']['id'], y[i]['models']['file_name']))
                    i +=1
        else:
            
            lb_assets.insert('','end', values = ( y['models']['id'],y['model_project_location']['id'], y['models']['file_name']))
    else:
        if type(y) is list:
            if y == []:
                lb_assets.insert('','end', values = ( "---", "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['id'], "---",  y[i]['file_name']))
                    i +=1
        else:
            lb_assets.insert('','end', values = ( y['id'], "---", y['file_name']))


def listsnaps():

    # Call for a list of user snapshots and adds to asset table - works for both projects and librby containers
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = listbox.focus()
    try:
        print (listbox.item(uid)['values'][0])
    except IndexError:
        print ("Error - need to select a project/library")
        text_area.insert(END, "Error - need to select a project/library"+ '\n')
        return
    data = '{ "id": '+ str(listbox.item(uid)['values'][0]) + '}'
    
    # detemine what type of container has been selected
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
                lb_assets.insert('','end', values = ( "---", "---", "<no data>"))
            else:
                i=0
                while i < len(y) :        
                    lb_assets.insert('','end', values = ( y[i]['id'], "---", y[i]['name']))
                    i +=1
        else:
            print(type(y['name']))
            lb_assets.insert('','end', values = ( y['id'],"---",  y['name']))

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def updt_gr(event):
    
     # sets up the asset table based on radio button selection. Note the program will defualt to Pointcloud on first load.
    if v2.get() == 0:
        rb_pc.invoke()
    elif v2.get() ==1:
        listpc()
    elif v2.get() ==2:
        listmod()
    elif v2.get() ==3:
        listsnaps()       
        


def updt_as(event):

    # update information on right side, required before download is available.
    headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c'),
    }
    uid = lb_assets.focus()


    data = '{ "id": '+ str(lb_assets.item(uid)['values'][0]) + '}'
    if str(lb_assets.item(uid)['values'][0]) =="---" :
        print("no data")
    else:
        if v2.get() == 1 :
            # pointcloud
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['point_cloud']
        elif v2.get()==2 :
           # model
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['models']
        elif v2.get()==3 :
           # snapshot
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/snapshots.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['snapshots']
        else:
            print("no selection")

        # Fill in detail on centre right
        uida.set ( y['id'])
        if v2.get() == 3 :
            name.set ( y['name']+ '.jpg')
            downl.set ( y['image'])
            size.set ( 'not availabe')
        else:
            name.set (y['file_name'])
            downl.set ( y['s3_file_download'])
            size.set ( y['file_size'])

        cr8td.set ( y['created'])
                            
        # Include model transformation Data for models inserted in projects only.

        if v.get() ==1 and v2.get() == 2:
            data = '{"id":' + str(listbox.item(listbox.focus())['values'][0]) + ',"model_id":' + str(lb_assets.item(lb_assets.focus())['values'][0]) + '}'
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models_orientation.json', headers=headers, data=data)
            x = json.loads(response.text)
            try:
                response = x['single response']
                mtrans = response['position']
                mrot = response['rotation']
                mscale = response['scale']
                mFT = 'T: ' + mtrans + '\nR: ' + mrot + '\nS: ' + mscale
                mod.set (mFT)
            except:
                print("multiple models")
                
            try:                
                response = x['multiple response']

                #cycle through responses and find matching orintation_ids
                for i in response:
                    
                    if str(lb_assets.item(lb_assets.focus())['values'][1]) == str(i['id']):
                        mtrans = i['position']
                        mrot = i['rotation']
                        mscale = i['scale']
                        mFT = 'T: ' + mtrans + '\nR: ' + mrot + '\nS: ' + mscale
                        mod.set (mFT)
            except:
                print("single model")                            
        else:
            mod.set ('Not Available')


def download():
    
    #Download an asset
    def directoryBox():
        
        #Open a folder select dialogue window
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
            
    #Test to make sure an assets is selected
    if lb_assets.focus() == "" :
        print('no selection')
    else:
        folder = directoryBox()

        
        headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c'),
        }
        uid = lb_assets.focus()

        data = '{ "id": '+ str(lb_assets.item(uid)['values'][0]) + '}'

        if str(lb_assets.item(uid)['values'][0]) =="---" :
            print("no data")
        else:
            downl.get
            r = requests.get(downl.get(),stream=True)
            with open(folder + '/' + str(name.get()), 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            return folder
            if v2.get() == 1 :
                # pointcloud
                response = requests.get('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', headers=headers, data=data)
                x = json.loads(response.text)
                y = json.loads(x)
                r = requests.get(y["s3_file_download"],stream=True)
                with open(folder + '/' + str(y["file_name"]), 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return folder
            elif v2.get()==2 :
                # Model
                response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models.json', headers=headers, data=data)
                x = json.loads(response.text)
                y = json.loads(x)
                r = requests.get(y["s3_file_download"],stream=True)
                with open(folder + '/' + str(y["file_name"]), 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return folder
            else:
                # Snapshots
                print("snapshots - not operational yet")

def upload_pc():

    #Upload pointcloud to project or library
    def sendpc():
        uid = listbox2.focus()
        # test listbox for focus
        try:
            print (listbox2.item(uid)['values'][0])
        except IndexError:
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Error - Please select Library or Project' + '\n')
            return

        MAX_UPLOAD_BYTE_LENGHT = 1024 * 1024 * 5 # 5M

        HOST = 'upload.3dusernet.com'
        #PORT = 8080
        API_URL = 'https://{}'.format(HOST)

        
        class Client:
            def __init__(self, api_url, max_byte_length):
                self.api_url = api_url
                self.max_byte_length = max_byte_length

            def upload_file(self, file_path, file_type, file_arg):
                file_size = os.path.getsize(file_path)
                headers = {'Filename': os.path.basename(file_path)}        
                headers['Token'] = show_token.get("1.0",'end-1c')
                headers['Filesize'] = str(file_size)
                #Check if Project or Library Selected
                if v3.get() == 1:
                    headers['Projectid'] = str(listbox2.item(uid)['values'][0])
                elif v3.get() == 2:
                    headers['Libraryid'] = str(listbox2.item(uid)['values'][0])
                
                headers['filesize'] = str(file_size)
                headers['Arguments'] = ent_pcattrib.get()
                headers['Filetype'] = str(file_type)
                headers['Description'] = ent_pcDesc.get()
                print (str(file_arg))
                print (str(file_type))
                text_area.delete('1.0', 'end')
                with open(file_path, 'rb') as file:
                    chunk_count = math.ceil(float(file_size) / self.max_byte_length)
                    print("Total chunk count:", chunk_count)
                    text_area.insert(END, "Total chunk count:" + str(chunk_count) + '\n')

                    retry_timeout = 1
                    sent_chunk_count = 0
                    while True:
                        headers['Range'] = "bytes={}/{}-{}".format(sent_chunk_count, int(chunk_count), file_size)

                        data = file.read(self.max_byte_length)
                        upload_endpoint = os.path.join(self.api_url, 'content', 'upload')
                        #print (headers)
                        #print (upload_endpoint)

                        try:
                            response = requests.post(upload_endpoint, headers=headers, data=data)
                            json_data = json.loads(response.text)
                            if json_data["result"]=="success":
                                print('{}. chunk sent to server'.format(sent_chunk_count + 1))
                                text_area.insert(END, '{}. chunk sent to server'.format(sent_chunk_count + 1) + '\n')
                                sent_chunk_count += 1
                            else:
                                print('Error Message:',json_data["message"])
                                return False
                        except requests.exceptions.RequestException as e:
                            print('Error while sending chunk to server. Retrying in {} seconds'.format(retry_timeout))
                            print (e)
                            time.sleep(retry_timeout)

                            # Sleep for max 10 seconds
                            if retry_timeout < 10:
                                retry_timeout += 1
                            continue

                        if sent_chunk_count >= chunk_count:
                            return True

                    return False

        if __name__ == '__main__':
            client = Client(API_URL, 

                MAX_UPLOAD_BYTE_LENGHT)
        try:
            file_path = filename
            file_type = "PC"
            file_arg = ent_pcattrib.get()
            print('Uploading file:', file_path)
            client.upload_file(file_path, file_type, file_arg)
        except IndexError:
            print("No file path provided")
            print("Usage: python chunk_uploader.py [file_path]")
            
        print("////// Pointcloud Uploaded")
        text_area.insert(END, "Success - Pointcloud Uploaded"+ '\n')
        t.destroy()
        if v2.get() ==1:
            listpc()
        elif v2.get()==2:
            listmod()
        else:
            listsnaps()

    
    filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("las files","*.las"),("laz files","*.laz"),("e57 files","*.e57"),("xyz files","*.xyz"),("ply files","*.ply")))
    fn = filename.split("/")[len(filename.split("/"))-1]

    #Build the interface for the pop-up UI
    t = Toplevel()
    t.title("Upload Pointcloud")
    lbl_pname = Label(t,text="Choose Upload Location").pack()
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
    lbl_pcDesc = Label(t,text="Enter Description").pack()
    ent_pcDesc = Entry(t)
    ent_pcDesc.pack()
    lbl_pcattrib = Label(t,text="Attributes").pack()
    ent_pcattrib = Entry(t)
    ent_pcattrib.pack()
    ent_pcattrib.insert(0, "-f xyzirgb -a RGB INTESNITY --intensity-range 0 65535 --color-range 0 255")
    btn_sendfile = Button(t,text ="Send File", command=lambda: sendpc()).pack()
    bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
    bt_Cancel.pack()
    
    
def upload_md():
    def sendmod():
        uid = listbox2.focus()
        try:
            print (listbox2.item(uid)['values'][0])
        except IndexError:
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Error - Please select Library or Project' + '\n')
            return

        MAX_UPLOAD_BYTE_LENGHT = 1024 * 1024 * 5 # 5M

        HOST = 'upload.3dusernet.com'
        #PORT = 8080
        API_URL = 'https://{}'.format(HOST)

        
        class Client:
            def __init__(self, api_url, max_byte_length):
                self.api_url = api_url
                self.max_byte_length = max_byte_length

            def upload_file(self, file_path, file_type, file_arg):
                file_size = os.path.getsize(file_path)
                print(file_size)
                headers = {'Filename': os.path.basename(file_path)}        
                headers['Token'] = show_token.get("1.0",'end-1c')
                headers['Filesize'] = str(file_size)
                #Check if Project or Library Selected
                if v3.get() == 1:
                    headers['Projectid'] = str(listbox2.item(uid)['values'][0])
                elif v3.get() == 2:
                    headers['Libraryid'] = str(listbox2.item(uid)['values'][0])

                headers['filesize'] = str(file_size)
                headers['Arguments'] = ent_modattrib.get()
                headers['Description'] = ent_modDesc.get()
                headers['Filetype'] = str(file_type)
                headers['location'] = ent_modPos.get()
                headers['rotation'] = ent_modRot.get()
                headers['scale'] = ent_modScl.get()
                print (str(file_arg))
                print (str(file_type))
                text_area.delete('1.0', 'end')

                with open(file_path, 'rb') as file:
                    chunk_count = math.ceil(float(file_size) / self.max_byte_length)
                    print("Total chunk count:", chunk_count)
                    text_area.insert(END, "Total chunk count:" + str(chunk_count) + '\n')

                    retry_timeout = 1
                    sent_chunk_count = 0
                    while True:
                        headers['Range'] = "bytes={}/{}-{}".format(sent_chunk_count, int(chunk_count), file_size)

                        data = file.read(self.max_byte_length)
                        upload_endpoint = os.path.join(self.api_url, 'content', 'upload')

                        try:
                            response = requests.post(upload_endpoint, headers=headers, data=data)
                            json_data = json.loads(response.text)
                            if json_data["result"]=="success":
                                print('{}. chunk sent to server'.format(sent_chunk_count + 1))
                                text_area.insert(END, '{}. chunk sent to server'.format(sent_chunk_count + 1) + '\n')
                                sent_chunk_count += 1
                            else:
                                print('Error Message:',json_data["message"])
                                return False
                        except requests.exceptions.RequestException as e:
                            print('Error while sending chunk to server. Retrying in {} seconds'.format(retry_timeout))
                            print (e)
                            time.sleep(retry_timeout)

                            # Sleep for max 10 seconds
                            if retry_timeout < 10:
                                retry_timeout += 1
                            continue

                        if sent_chunk_count >= chunk_count:
                            return True

                    return False
 
        if __name__ == '__main__':
            client = Client(API_URL, 

                MAX_UPLOAD_BYTE_LENGHT)
        try:
            file_path = filename
            file_type = "Model"
            file_arg = ent_modattrib.get()
            print('Uploading file:', file_path)
            client.upload_file(file_path, file_type, file_arg)
        except IndexError:
            print("No file path provided")
            print("Usage: python chunk_uploader.py [file_path]")
            
        print("////// Model Uploaded")
        text_area.insert(END, "Success - Model Uploaded"+ '\n')
        t.destroy()
        if v2.get() ==1:
            listpc()
        elif v2.get()==2:
            listmod()
        else:
            listsnaps()

    #Build the interface for the pop-up UI
    filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("stl files","*.stl"),("fbx files","*.fbx"),("ifc files","*.ifc"),("obj files","*.obj"),("ply files","*.ply"), ("zip files","*.zip")))
    print (filename)
    fn = filename.split("/")[len(filename.split("/"))-1]

    #Build the interface for the pop-up UI
    t = Toplevel()
    t.title("Upload Model")
    lbl_pname = Label(t,text="Choose Upload Location").pack()
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
    lbl_modDesc = Label(t,text="Enter Description").pack()
    ent_modDesc = Entry(t)
    ent_modDesc.pack()
    lbl_modattrib = Label(t,text="Attributes").pack()
    ent_modattrib = Entry(t)
    ent_modattrib.pack()
    ent_modattrib.insert(0, "-a None -s smooth -d normal")
    lbl_modPosattrib = Label(t,text="Position").pack()
    ent_modPos = Entry(t)
    ent_modPos.pack()
    ent_modPos.insert(0, "0, 0, 0")
    lbl_modRotattrib = Label(t,text="Rotation (Radians)").pack()
    ent_modRot = Entry(t)
    ent_modRot.pack()
    ent_modRot.insert(0, "0, 0, 0")
    lbl_modSclattrib = Label(t,text="Scale").pack()
    ent_modScl = Entry(t)
    ent_modScl.pack()
    ent_modScl.insert(0, "1, 1, 1")
 
    btn_sendfile = Button(t,text ="Send File", command=lambda: sendmod()).pack()
    bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
    bt_Cancel.pack()
    print("upload model")

    
            
def mv_md():

    # Move model to new location
    ProjID = ""
    ModelID = ""
    
    def movMod():
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }

        data = '{"id":' + str(modprojlocID) + ',"scale":"' + str(ent_modScl.get()) + '","location":"' + str(ent_modPos.get()) + '","rotation":"' + str(ent_modRot.get()) + '","copy":"false"}'

        #Important to ensure the request is PUT
        response = requests.put('https://api.3dusernet.com/3dusernetApi/api/models_orientation.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        modMovresp = json.loads(response.text)
        
        print('Model Position / Rotation / Scale Updated')

    
    #Get the IDs of the selected project and model from the main UI lists
    if v.get() == 1 and v2.get() == 2:
        #Get values for the selected Project and Model
        ProjID = listbox.item(listbox.focus())['values'][0]
        ModelID = lb_assets.item(lb_assets.focus())['values'][0]
        print (ProjID)
        print (ModelID)

        #Get the ModelProjectLocation id for the selected Project and Model
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }

        data = '{"id":' + str(ProjID) + ',"model_id":' + str(ModelID) + '}'
        
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models_orientation.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        modprojloc = json.loads(response.text)

        modprojlocID = modprojloc['single response']['id']
        
        print('ModelProjectLocation = ', modprojlocID)

        #Build the interface for the pop-up UI
        t = Toplevel()
        t.title("Move Model")
        lbl_pname = Label(t,text="Change the Parameters").pack()
 
        lbl_pcattrib = Label(t,text="Position").pack()
        ent_modPos = Entry(t)
        ent_modPos.pack()
        ent_modPos.insert(0, str(modprojloc['single response']['position']))
        lbl_pcattrib = Label(t,text="Rotation (Radians)").pack()
        ent_modRot = Entry(t)
        ent_modRot.pack()
        ent_modRot.insert(0, str(modprojloc['single response']['rotation']))
        lbl_pcattrib = Label(t,text="Scale").pack()
        ent_modScl = Entry(t)
        ent_modScl.pack()
        ent_modScl.insert(0, str(modprojloc['single response']['scale']))

        btn_sendfile = Button(t,text ="Move Model", command=lambda: movMod()).pack()
        bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
        bt_Cancel.pack()
        
    else:
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'No valid IDs - Please select a Project and Model')
        print('No valid IDs - Please select a Project and Model')
 

def cp_md():

    # Copy model to new location
    ProjID = ""
    ModelID = ""
    
    def copyMod():
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }

        #Note the copy attribute:
        data = '{"id":' + str(modprojlocID) + ',"scale":"' + str(ent_modScl.get()) + '","location":"' + str(ent_modPos.get()) + '","rotation":"' + str(ent_modRot.get()) + '","copy":"true"}'
        print(data)
        #Important to ensure the request is PUT
        response = requests.put('https://api.3dusernet.com/3dusernetApi/api/models_orientation.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        modCopresp = json.loads(response.text)
        
        print('Model copied to new Position / Rotation / Scale')

    
    #Get the IDs of the selected project and model from the main UI lists
    if v.get() == 1 and v2.get() == 2:
        #Get values for the selected Project and Model
        ProjID = listbox.item(listbox.focus())['values'][0]
        ModelID = lb_assets.item(lb_assets.focus())['values'][0]
        print (ProjID)
        print (ModelID)

        #Get the ModelProjectLocation id for the selected Project and Model
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }
        data = '{"id":' + str(ProjID) + ',"model_id":' + str(ModelID) + '}'
        response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models_orientation.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        modprojloc = json.loads(response.text)
        modprojlocID = modprojloc['single response']['id']
        

        #Build the interface for the pop-up UI
        t = Toplevel()
        t.title("Copy Model")
        lbl_pname = Label(t,text="Enter the Parameters").pack()
        lbl_pcattrib = Label(t,text="Position").pack()
        ent_modPos = Entry(t)
        ent_modPos.pack()
        ent_modPos.insert(0, str(modprojloc['single response']['position']))
        lbl_pcattrib = Label(t,text="Rotation (Radians)").pack()
        ent_modRot = Entry(t)
        ent_modRot.pack()
        ent_modRot.insert(0, str(modprojloc['single response']['rotation']))
        lbl_pcattrib = Label(t,text="Scale").pack()
        ent_modScl = Entry(t)
        ent_modScl.pack()
        ent_modScl.insert(0, str(modprojloc['single response']['scale']))
        btn_sendfile = Button(t,text ="Copy Model", command=lambda: copyMod()).pack()
        bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
        bt_Cancel.pack()
        
    else:
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'No valid IDs - Please select a Project and Model')
        print('No valid IDs - Please select a Project and Model')
 

def delProj():
        
    #Case 1 - Project Selected
    if v.get() == 1:
        #Find the selected project ID
        try:
            ProjID = listbox.item(listbox.focus())['values'][0]
        except IndexError:
            print("need to select a project")
            text_area.insert(END, "Error - need to select a project"+ '\n')
            return
        
        #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this project?")
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return
            
        #Send the API command with the relevant ID to delete the Project
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }
        data = '{"id":' + str(ProjID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/project.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Project has been deleted')

    #Case 2 - Library Selected
    elif v.get() == 2:
        #Find the selected library ID
        try:
            LibID = listbox.item(listbox.focus())['values'][0]
        except IndexError:
            print("need to select a library")
            text_area.insert(END, "Error - need to select a library"+ '\n')
            return
        
        #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this Library?")
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return
        
        #Send the API command with the relevant ID to delete the Project
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }
        data = '{"id":' + str(LibID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/library.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Library has been deleted')

    if v.get() ==1:
        listproj(listbox)
    else:
        listlib(listbox)

def delItem():
      
    #Case 1 - Project Items Selected
    #Pointclouds
    if v.get() == 1 and v2.get() ==1:

        #Get values for the selected Project and Pointcloud
        #Check something is selected
        try:
            index = str(listbox.selection()[0])
            ProjID = listbox.item(listbox.focus())['values'][0]

            try:
                index2 = str(lb_assets.selection()[0])
                pcID = lb_assets.item(lb_assets.focus())['values'][0]
            
            except:
                print ('Need to select a valid Pointcloud')
                text_area.delete('1.0', 'end')
                text_area.insert(END, 'Error - Need to select a valid Pointcloud' + '\n')
            
        except IndexError:
            print ('Need to select a Project')
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Need to select a Project' + '\n')

       #check with User to verify delete
        response = messagebox.askokcancel("Warning","Are you sure you wish to delete this Library?")
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return

       
        #Perform Deletion of Selected Object
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }
        data = '{"point_cloud_id":' + str(pcID) + ',"project_id":' + str(ProjID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/delete_project_point_cloud.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Pointcloud has been deleted')

    #Models
    elif v.get() == 1 and v2.get() == 2:
        
        #Get values for the selected Project and Model
        #Check something is selected
        try:
            index = str(listbox.selection()[0])
            ProjID = listbox.item(listbox.focus())['values'][0]
            try:
                index2 = str(lb_assets.selection()[0])
                modID = lb_assets.item(lb_assets.focus())['values'][0]
                instID = lb_assets.item(lb_assets.focus())['values'][1]
            except:
                print ('Need to select a Model')
                text_area.delete('1.0', 'end')
                text_area.insert(END, 'Need to select a Model' + '\n')         
        except IndexError:
            print ('Need to select a Project')
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Need to select a Project' + '\n')
            
        #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this Library?")
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return

        #Perform Deletion of Selected Object
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }
        data = '{"model_id":' + str(modID) + ',"project_id":' + str(ProjID) + ',"model_project_location_id":' + str(instID) +'}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/delete_project_model.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Model has been deleted')

        
    #Snapshots
    elif v.get() == 1 and v2.get() ==3:

        #Get values for the selected Project and Snapshot
        #Check something is selected
        try:
            index = str(listbox.selection()[0])
            ProjID = listbox.item(listbox.focus())['values'][0]

            try:
                index2 = str(lb_assets.selection()[0])
                snapID = lb_assets.item(lb_assets.focus())['values'][0]
            
            except:
                print ('Need to select a Snapshot')
                text_area.delete('1.0', 'end')
                text_area.insert(END, 'Need to select a Snapshot' + '\n')
            
        except IndexError:
            print ('Need to select a Project')
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Need to select a Project' + '\n')

        #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this Library?")
        print (response)
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return

       #Perform Deletion of Snapshot
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }
        data = '{"snapshot_id":' + str(snapID) + ',"project_id":' + str(ProjID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/delete_project_snapshot.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Snapshot has been deleted')

        
    
    #Case 2 - Library Items Selected
    #Pointclouds
    if v.get() == 2 and v2.get() ==1:

        #Get values for the selected Library and Pointcloud
        #Check something is selected
        try:
            index = str(listbox.selection()[0])
            LibID = listbox.item(listbox.focus())['values'][0]

            try:
                index2 = str(lb_assets.selection()[0])
                pcID = lb_assets.item(lb_assets.focus())['values'][0]

            except:
                print ('Need to select a Pointcloud')
                text_area.delete('1.0', 'end')
                text_area.insert(END, 'Need to select a Pointcloud' + '\n')
            
        except IndexError:
            print ('Need to select a Library')
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Need to select a Library' + '\n')

       #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this Library?")
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return

        #Perform Deletion of Selected Object
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }

        data = '{"point_clouds_ids":[' + str(pcID) + '],"library":' + str(LibID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/delete_library_point_cloud.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Pointcloud has been deleted')  
          
    #Models
    elif v.get() == 2 and v2.get() == 2:

        #Get values for the selected Library and Pointcloud
        #Check something is selected
        try:
            index = str(listbox.selection()[0])
            LibID = listbox.item(listbox.focus())['values'][0]

            try:
                index2 = str(lb_assets.selection()[0])
                modID = lb_assets.item(lb_assets.focus())['values'][0]
            
            except:
                print ('Need to select a Model')
                text_area.delete('1.0', 'end')
                text_area.insert(END, 'Need to select a Model' + '\n')
            
        except IndexError:
            print ('Need to select a Library')
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Need to select a Library' + '\n')

        #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this Library?")
        print (response)
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return
        
        #Perform Deletion of Selected Object
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }

        data = '{"models_ids":[' + str(modID) + '],"library":' + str(LibID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/delete_library_model.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Model has been deleted')
        
        
    #Snapshots
    elif v.get() == 2 and v2.get() ==3:
        
        #Get values for the selected Library and Snapshot
        #Check something is selected
        try:
            index = str(listbox.selection()[0])
            LibID = listbox.item(listbox.focus())['values'][0]

            try:
                index2 = str(lb_assets.selection()[0])
                snapID = lb_assets.item(lb_assets.focus())['values'][0]
            
            except:
                print ('Need to select a Snapshot')
                text_area.delete('1.0', 'end')
                text_area.insert(END, 'Need to select a Snapshot' + '\n')
            
        except IndexError:
            print ('Need to select a Library')
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Need to select a Library' + '\n')

        #check with User to verify delete
        response = messagebox.askokcancel("Python","Are you sure you wish to delete this Library?")
        print (response)
        if response == False:
            print("Operation cancelled")
            text_area.insert(END, "Operation cancelled"+ '\n')
            return

        
       #Perform Deletion of Selected Object
        headers = {
        'Content-Type': 'application/json',
        'token': show_token.get("1.0",'end-1c')
        }

        data = '{"snapshots_ids":[' + str(snapID) + '],"library":' + str(LibID) + '}'
        response = requests.delete('https://api.3dusernet.com/3dusernetApi/api/delete_library_snapshot.json', headers=headers, data=data)
        text_area.delete('1.0', 'end')
        text_area.insert(END, response.text + '\n')
        print ('Snapshot has been deleted')

    if v2.get() ==1:
        listpc()
    elif v2.get()==2:
        listmod()
    else:
        listsnaps()
        
def upd_asset():
    if v2.get() == 1:
        upd_Pointcloud()
    else:
        upd_Model()

def upd_Pointcloud():

    #Updates pointcloud informaation including a thumbnail loader
    def chooseTN():
        basewidth = 300
        print ("choosing thumbnail")
        fileLoc =  filedialog.askopenfilename(initialdir = "/",title = "Select Thumbnail",filetypes = (("jpg files","*.jpg"),("png files","*.png"),("bmp files","*.bmp")))
        fln = fileLoc.split("/")[len(fileLoc.split("/"))-1]

        # require global variable otherwise img and gif1 is sent to garbage at the end of the function
        global img
        global gif1

        
        #Load Image, resize and send to canvas
        img = Image.open(str(fileLoc))
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), resample=Image.BILINEAR)
        
        gif1 = ImageTk.PhotoImage(img)    
        ent_canvas.delete("all")
        ent_canvas.create_image(0,0,image=gif1, anchor=NW)
        t.lift()

    def clearTN():
        
        #This clears the thumbnail from the viewer, however at this point in time there is no way of clearing a thumbnail from the API
        global img
        img = ""
        ent_canvas.delete("all")

    def sendpc():
        
        #Two different requests depening on whether a thumbnail is to uploaded or not
        if type(img) == str:
            print ("no image")


            headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c')
            }
            data = '{"id":' + str(x['point_cloud']['id']) + ', "description":"' + str(ent_pcDesc.get()) + '", "file_name":"' + str(ent_pcName.get()) + '"}'
            response = requests.put('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', headers=headers, data=data)

            #send notification to user
            text_area.delete('1.0', 'end')
            text_area.insert(END, response.text + '\n')
            print ('Pointcloud has been Updated')


        else:
            
            output = io.BytesIO()
            img.save(output, format='PNG')

            #Send Data for Pointcloud Update - note that image is sent as hexidecimal binary
            
            multipart_data = MultipartEncoder(
                fields={
                        # a file upload field
                        'files':('thumb', output.getvalue(), 'image/png'),
                        # plain text fields
                        'id':str(x['point_cloud']['id']), 
                        'description':str(ent_pcDesc.get()),
                        'file_name':str(ent_pcName.get()),
                       }
                )
            response = requests.put('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', data=multipart_data, headers={
                #Important to note different type of content in the header here
                'Content-Type': multipart_data.content_type,
                'token': show_token.get("1.0",'end-1c'),
            })
            text_area.delete('1.0', 'end')
            text_area.insert(END, response.text + '\n')
            print ('Pointcloud has been Updated')
        t.destroy()

    #Check if a Pointcloud is selected and get ID
    if v2.get()==1:
        if lb_assets.focus() == "" :
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Please select a Pointcloud')
            print('Please select a Pointcloud')

        else:
            #Get Name & Description of Pointcloud
            headers = {
                'Content-Type': 'application/json',
                'token': show_token.get("1.0",'end-1c'),
            }
            uid = lb_assets.focus()
            print (lb_assets.item(uid)['values'][0])
            data = '{ "id": '+ str(lb_assets.item(uid)['values'][0]) + '}'

            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/point_cloud.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['point_cloud']

            

            #Build the interface for the pop-up UI
            t = Toplevel()
            t.title("Update Pointcloud")
            lbl_pcName = Label(t,text="Name").pack()
            ent_pcName = Entry(t)
            ent_pcName.insert(END,str(x['point_cloud']['file_name']))
            ent_pcName.pack()
            lbl_pcDesc = Label(t,text="Description").pack()
            ent_pcDesc = Entry(t)
            ent_pcDesc.insert(END,str(x['point_cloud']['description']))
            ent_pcDesc.pack()
            ent_canvas = Canvas(t,width=300, height=200, bg='black')
            ent_canvas.pack()

            # Using PIL to load image and resize to 275 width, keeping image proportionally correct
            basewidth = 275
            global img
            global gif1
            try:
                fd =  urllib.request.urlopen(y['thumbnail'])
                image_file = io.BytesIO(fd.read())
                img = Image.open(image_file)
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), resample=Image.BILINEAR)
                gif1 = ImageTk.PhotoImage(img) 
                ent_canvas.create_image(0,0,image=gif1, anchor=NW)
 
            except:
                text_area.insert(END, 'current Thumbnail empty or not stored as url' + '\n')
                img = ""                          
            btn_clearThumb = Button(t,text ="Clear Thumbnail", command=lambda: clearTN()).pack()
            bt_chooseTH = Button(t,text ="Choose Thumbnail", command=lambda: chooseTN()).pack()
            bt_sendfile = Button(t,text ="Update", command=lambda: sendpc()).pack()
            bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
            bt_Cancel.pack()

    else:
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'Please select a Pointcloud')
        print('Please select a Pointcloud')


def upd_Model():

    #Updates model informaation including a thumbnail loader
    def chooseTN():
        basewidth = 300
        print ("choosing thumbnail")
        fileLoc =  filedialog.askopenfilename(initialdir = "/",title = "Select Thumbnail",filetypes = (("jpg files","*.jpg"),("png files","*.png"),("bmp files","*.bmp")))
        fln = fileLoc.split("/")[len(fileLoc.split("/"))-1]
        global img
        global gif1
        #Load Image, resize and send to canvas
        img = Image.open(str(fileLoc))
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), resample=Image.BILINEAR)    
        gif1 = ImageTk.PhotoImage(img)    
        ent_canvas.delete("all")
        ent_canvas.create_image(0,0,image=gif1, anchor=NW)
        t.lift()

    def clearTN():
        global img
        img = ""
        ent_canvas.delete("all")

    def sendmod():
        if type(img) == str:
            print ("no image")
            headers = {
            'Content-Type': 'application/json',
            'token': show_token.get("1.0",'end-1c')
            }
            data = '{"id":' + str(x['models']['id']) + ', "description":"' + str(ent_modDesc.get()) + '", "file_name":"' + str(ent_modName.get()) + '"}'
            response = requests.put('https://api.3dusernet.com/3dusernetApi/api/models.json', headers=headers, data=data)

            #send notification to user
            text_area.delete('1.0', 'end')
            text_area.insert(END, response.text + '\n')
            print ('Model has been Updated')

        else:
            
            output = io.BytesIO()
            img.save(output, format='PNG')

            #Send Data for Pointcloud Update
            multipart_data = MultipartEncoder(
                fields={
                        # a file upload field
                        'files':('thumb', output.getvalue(), 'image/png'),
                        # plain text fields
                        'id':str(x['models']['id']), 
                        'description':str(ent_modDesc.get()),
                        'file_name':str(ent_modName.get()),
                       }
                )
            response = requests.put('https://api.3dusernet.com/3dusernetApi/api/models.json', data=multipart_data, headers={
                #Important to note different type of content in the header here
                'Content-Type': multipart_data.content_type,
                'token': show_token.get("1.0",'end-1c'),
            })
            text_area.delete('1.0', 'end')
            text_area.insert(END, response.text + '\n')
            print ('Model has been Updated')
            t.destroy()

    #Check if a Model is selected and get ID
    if v2.get()==2:
        if lb_assets.focus() == "" :
            text_area.delete('1.0', 'end')
            text_area.insert(END, 'Please select a Model')
            print('Please select a Model')

        else:
            #Get Name & Description of Pointcloud
            headers = {
                'Content-Type': 'application/json',
                'token': show_token.get("1.0",'end-1c'),
            }
            uid = lb_assets.focus()
            print (lb_assets.item(uid)['values'][0])
            data = '{ "id": '+ str(lb_assets.item(uid)['values'][0]) + '}'
            response = requests.get('https://api.3dusernet.com/3dusernetApi/api/models.json', headers=headers, data=data)
            x = json.loads(response.text)
            y = x['models']

            #Build the interface for the pop-up UI

            t = Toplevel()
            t.title("Update Pointcloud")           
            lbl_modName = Label(t,text="Name").pack()
            ent_modName = Entry(t)
            ent_modName.insert(END,str(x['models']['file_name']))
            ent_modName.pack()
            lbl_modDesc = Label(t,text="Description").pack()
            ent_modDesc = Entry(t)
            ent_modDesc.insert(END,str(x['models']['description']))
            ent_modDesc.pack()
            ent_canvas = Canvas(t,width=300, height=200, bg='black')
            ent_canvas.pack()

            # Using PIL to load image and resize to 275 width, keeping image proportionally correct

            basewidth = 275
            global img
            global gif1

            try:
                fd =  urllib.request.urlopen(y['thumbnail'])
                image_file = io.BytesIO(fd.read())
                img = Image.open(image_file)
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), resample=Image.BILINEAR)
                gif1 = ImageTk.PhotoImage(img) 
                ent_canvas.create_image(0,0,image=gif1, anchor=NW)
 
            except:
                text_area.insert(END, 'current Thumbnail empty or not stored as url' + '\n')
                img = ""

                                           
            
            btn_clearThumb = Button(t,text ="Clear Thumbnail", command=lambda: clearTN()).pack()
            bt_chooseTH = Button(t,text ="Choose Thumbnail", command=lambda: chooseTN()).pack()
            bt_sendfile = Button(t,text ="Update", command=lambda: sendmod()).pack()
            bt_Cancel = Button(t, text = "Cancel",command= t.destroy)
            bt_Cancel.pack()

    else:
        text_area.delete('1.0', 'end')
        text_area.insert(END, 'Please select a Model')
        print('Please select a Model')
    
    print('Updating Model')          


##############   TKINTER ROOT MENU  ################# 
    
root = Tk()
root.title('API Example interface V1.0')
root.geometry('{}x{}'.format(650, 600))


# create all of the main containers
top_frame = Frame(root, bg='#660066', width=450, pady=3)
center = Frame(root, bg='#660066', width=50, padx=3, pady=3)
btm_frame = Frame(root, bg='white', pady=3)


# layout all of the main containers
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=3, sticky="ew")

# create the widgets for the top frame
model_label = Label(top_frame, text='3DUserNet API Example',font=("Arial", 16), bg="#660066", fg="white")
user_label = Label(top_frame, text='UserName:', bg="#660066",fg="white")
pass_label = Label(top_frame, text='Password:', bg="#660066",fg="white")
app_label = Label(top_frame, text='AppID:', bg="#660066",fg="white")

user = StringVar()
pword = StringVar()
api = StringVar()

entry_U = Entry(top_frame, background="white", width = 15, textvariable=user)
entry_P = Entry(top_frame, show="*", background="white", width = 15, textvariable=pword)
entry_A = Entry(top_frame, background="white", width = 15, textvariable=api)
get_token = Button(top_frame, bg="light grey", highlightbackground="#660066", text="OK", command=callback)
token_label = Label(top_frame, text='= Token', bg="#660066",fg="white")
show_token = Text(top_frame, height = 1,background="light grey", width = 70)

sve = IntVar()

cb_saveUser = Checkbutton(top_frame, bg="#660066", foreground="light grey", text="", variable=sve)
sv_label = Label(top_frame, text='Save details:', bg="#660066",fg="white",font=("Arial", 10))

# layout the widgets in the top frame
model_label.grid(row=0, columnspan=8)
user_label.grid(row=1, column=0)
pass_label.grid(row=1, column=2)
app_label.grid(row=1, column=4)
entry_U.grid(row=1, column=1)
entry_P.grid(row=1, column=3)
entry_A.grid(row=1, column=5)
get_token.grid(row=2,column=0, sticky=W)
token_label.grid(row=2,column=5, sticky=E)
show_token.grid(row=2,column=1, columnspan=5, sticky=W)
cb_saveUser.grid(row=0,column=5, sticky=E)
sv_label.grid(row=0,column=5)

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

ctr_left = Frame(center, bg='#c6bfd2', width=100, padx=3, pady=3)
ctr_mid = Frame(center, bg='#c6bfd2', width=100, padx=3, pady=3)
ctr_right = Frame(center, bg='#c6bfd2', width=250, padx=3, pady=3)

ctr_left.grid(row=0, column=0, sticky="ns")
ctr_mid.grid(row=0, column=1, sticky = "nsew")
ctr_right.grid(row=0, column=2, sticky="ns")

# create the widgets for the centre_left frame
ctr_left.grid_rowconfigure(1, weight=0)
ctr_left.grid_columnconfigure(1, weight=1)

v = IntVar()

rb_poj = Radiobutton(ctr_left, text="Projects", command=lambda: listproj(listbox), variable=v, value=1, bg = "#c6bfd2")
rb_lbl = Label(ctr_left, text='- - - - - - - - - - - - - - - ',font=("Arial", 12), bg="#c6bfd2", fg="white")
rb_lib = Radiobutton(ctr_left, text="Libraries", command=lambda: listlib(listbox), variable=v, value=2, bg = "#c6bfd2")
lb_header = ['id', 'name']
listbox = ttk.Treeview(ctr_left, columns=lb_header, show="headings")
listbox.heading('id', text="id")
listbox.column('id',minwidth=0,width=40, stretch=NO)
listbox.heading('name', text="Name")
listbox.column('name',minwidth=0,width=150, stretch=NO)
listbox.bind("<ButtonRelease-1>", updt_gr)


#replaced with ttk tree   - listbox = Listbox(ctr_left)
bt_addpr = Button(ctr_left,text="New", highlightbackground="#c6bfd2", command=lambda: new_Container())
bt_updpr = Button(ctr_left,text="Update", highlightbackground="#c6bfd2", command=lambda: upd_Container())
bt_delpr = Button(ctr_left,text="Delete", highlightbackground="#c6bfd2", command=lambda: delProj())

# layout the widgets in the centre_left frame

rb_poj.grid(row=0)
rb_lbl.grid(row=1)
rb_lib.grid(row=2)
listbox.grid(row=3)
bt_addpr.grid(row=4)
bt_updpr.grid(row=5)
bt_delpr.grid(row=8)

# create the widgets for the centre_mid frame
ctr_mid.grid_rowconfigure(1, weight=0)
ctr_mid.grid_columnconfigure(1, weight=1)

v2 = IntVar()
rb_pc = Radiobutton(ctr_mid, text="Pointclouds", command=lambda: listpc(), variable=v2, value=1, bg = "#c6bfd2")
rb_md = Radiobutton(ctr_mid, text="Models", command=lambda: listmod(), variable=v2, value=2, bg = "#c6bfd2")
rb_ss = Radiobutton(ctr_mid, text="Snapshots", command=lambda: listsnaps(), variable=v2, value=3, bg = "#c6bfd2")
lb_header2 = ['id', 'instid', 'name']
lb_assets = ttk.Treeview(ctr_mid, columns=lb_header2, show="headings")

#replaced with ttk tree  - lb_assets = Listbox(ctr_mid)
lb_assets.heading('id', text="id")
lb_assets.column('id',minwidth=0,width=40, stretch=NO)
lb_assets.heading('instid', text="inst_id")
lb_assets.column('instid',minwidth=0,width=40, stretch=NO)
lb_assets.heading('name', text="Name")
lb_assets.column('name',minwidth=0,width=150, stretch=NO)
lb_assets.bind("<ButtonRelease-1>", updt_as)

bt_downl = Button(ctr_mid,text="Download Object", command=lambda: download(), highlightbackground="#c6bfd2")
bt_updAss = Button(ctr_mid,text="Update Object", command=lambda: upd_asset(), highlightbackground="#c6bfd2")
bt_delIt = Button(ctr_mid,text="Delete Object", command=lambda: delItem(), highlightbackground="#c6bfd2")



# layout the widgets in the centre_mid frame
rb_pc.grid(row=0)
rb_md.grid(row=1)
rb_ss.grid(row=2)
lb_assets.grid(row=3)
bt_downl.grid(row=4)
bt_updAss.grid(row=5)
bt_delIt.grid(row=6)



# create the widgets for the centre_right frame
details_label = Label(ctr_right, text='Selected File Details:',font=("Arial", 14), bg="#c6bfd2", fg="white")
uida = StringVar()
lbl_id = Label(ctr_right,width =30, textvariable = uida, font=("Arial", 10), anchor='e', bg="#c6bfd2", fg="black")
uida.set("id")

name = StringVar()
lbl_name = Label(ctr_right,width =30, textvariable = name, anchor='e',font=("Arial", 10), bg="#c6bfd2", fg="black")
name.set('Name')

downl = StringVar()
lbl_downl = Label(ctr_right, justify=RIGHT, textvariable = downl, anchor='e', wraplength= 180, font=("Arial", 10), bg="#c6bfd2", fg="#063c53")
downl.set("Download Link")

size = StringVar()
lbl_size = Label(ctr_right,width =30, textvariable = size,  anchor='e', font=("Arial", 10), bg="#c6bfd2", fg="black")
size.set("File Size")

cr8td = StringVar()
lbl_cr8td = Label(ctr_right,width =30, textvariable = cr8td, anchor='e', font=("Arial", 10), bg="#c6bfd2", fg="black")
cr8td.set("Created")

mod = StringVar()
lbl_mod =Label(ctr_right, justify=RIGHT, textvariable = mod, wraplength= 180, anchor='e', font=("Arial", 10), bg="#c6bfd2", fg="#45025b")
mod.set("Model Transformation")

bt_uplpc = Button(ctr_right,text = "Upload Pointcloud", command=lambda: upload_pc(), anchor='s', highlightbackground="#c6bfd2")
bt_uplmd = Button(ctr_right,text = "Upload Model", command=lambda: upload_md(), anchor='s', highlightbackground="#c6bfd2")
bt_mvmd = Button(ctr_right,text = "Move Model", command=lambda: mv_md(), anchor='s', highlightbackground="#c6bfd2")
bt_cpmd = Button(ctr_right,text = "Copy Model", command=lambda: cp_md(), anchor='s', highlightbackground="#c6bfd2")

# layout the widgets in the centre_right frame
details_label.grid(row=0, sticky=E)
lbl_id.grid(row=1, sticky=W)
lbl_name.grid(row=2, sticky=W)
lbl_downl.grid(row=3, sticky=E)
lbl_size.grid(row=4, sticky=W)
lbl_cr8td.grid(row=5, sticky=W)
lbl_mod.grid(row=6, sticky=E)
bt_uplpc.grid(row=7)
bt_uplmd.grid(row=8)
bt_mvmd.grid(row=9)
bt_cpmd.grid(row=10)

# create the widgets for the bottom frame
btm_frame.grid_rowconfigure(0, weight=1)
btm_frame.grid_columnconfigure(0, weight=1)

text_area= Text(btm_frame, background="#c1c5d6"
                )

# layout the widgets in the bottom frame
text_area.grid(row=0,column=0,sticky=W+E)


# load config info into fields if they exist
try:
    f=open("config.txt", "r")
    if f.mode == 'r':
        contents =f.read()
        user.set(contents.splitlines()[0])
        api.set(contents.splitlines()[2])
        enc = ast.literal_eval(contents.splitlines()[1])
        senc = enc.decode('utf-8')
        dec = decoder(senc,str(contents.splitlines()[0]))
        pword.set(dec)
except:
    print("Error - Unable to load previous details")
    text_area.delete('1.0', 'end')
    text_area.insert(END, 'Error - Unable to load previous details' + '\n')
    
root.lift()
root.mainloop()
