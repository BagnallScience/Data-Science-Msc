#####
# File Operations Functions V2
#####
import pandas as pd 

def load_marks():
    
    dfStudentMarks=pd.read_csv("marks.txt")
    #print("student Marks\n",dfstudentMarks)
    return dfStudentMarks

    
def save_marks(dfStudentMarks):
    print("saving students' marks to the file")
    dfStudentMarks.to_csv("marks.txt",index=False)

if __name__=="__main__":
    # testing load function 
    dfmarks=load_marks()
    print(dfmarks)
    # testing save function
    save_marks(dfmarks)
    