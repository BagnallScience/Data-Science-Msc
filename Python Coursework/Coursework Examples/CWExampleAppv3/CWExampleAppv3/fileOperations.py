#####
# File Operations Functions 
#####

def remote_func():
    print("I am here")

def load_marks():
    StudentMarks=[]
    
    f=open("marks.txt","r")
    for mark in f:
        clean_mark=mark.strip()
        sName, sMark=clean_mark.split(",")# name
        StudentMarks.append([sName,int(sMark)])
    print("student Marks\n",StudentMarks)
    
    f.close()
    return StudentMarks

    
def save_marks(studentMarks):
    print("saving students' marks to the file")
    f=open("marks.txt","w")
    for mark in studentMarks:
        record=mark[0]+","+str(mark[1])+"\n"
        f.write(mark[0]+","+str(mark[1])+"\n")
    f.close()
