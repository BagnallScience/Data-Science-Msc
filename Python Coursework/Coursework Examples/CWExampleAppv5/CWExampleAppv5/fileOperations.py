#####
# File Operations Functions V3
#####
import pandas as pd 
import sqlite3

def save_to_db(dfStudentMarks):
    #print("i am here to save")
    conn = sqlite3.connect('marksDB.db')

    dfStudentMarks.to_sql("marks",conn,if_exists='replace',index=False)
    """
    'append': Adds the data from the DataFrame to the existing table, if it exists. 
                If the table does not exist, it will be created.
    'replace': Drops the existing table and replaces it with new data from the DataFrame.
    """
    conn.close()

def load_from_db():
    #print("i am here to load ")
    conn = sqlite3.connect('marksDB.db')

    dfStudentMarks=pd.read_sql('select * from marks',conn)

    conn.close()
    
    return dfStudentMarks

def load_marks():
    
    dfStudentMarks=pd.read_csv("marks.txt")
    #print("student Marks\n",dfstudentMarks)
    return dfStudentMarks

    
def save_marks(dfStudentMarks):
    print("saving students' marks to the file")
    dfStudentMarks.to_csv("marks.txt",index=False)

if __name__=="__main__":
#     # testing load function 
#     dfmarks=load_marks()
#     print(dfmarks)
#     # testing save function
#     save_marks(dfmarks)
    
    dfmarks=load_marks()
    save_to_db(dfmarks)
    dfMarksDB=load_from_db()
    print(dfMarksDB)
    
    
    