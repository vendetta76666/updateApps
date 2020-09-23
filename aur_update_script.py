import subprocess
import os
import re
import glob
import pickle
import sys

#directories / files for app
appDir=os.environ['HOME'] + '/AUR/update-apps/'  #where are your apps located
updateAppsNeeds = []
gitList = os.environ['HOME'] + "/AUR/gitUrls"
appUpdates = os.environ['HOME'] + "/AUR/appUpdates"

def enumerateAppDirs():
    filteredDirs = []
    unfilteredDirs = os.listdir(rf"{appDir}")
    # print(unfilteredDirs)
    for i in unfilteredDirs:
        # print(filteredDirs)
        if os.path.isdir(os.path.join(appDir,i)):
            filteredDirs.append(i)
    return filteredDirs

folders=enumerateAppDirs() #list of folders in app directory

def printTitle():
    title = "Welcome to Update Apps AUR Helper"
    print('-' * len(title),"\n",title,"\n",'-' * len(title))

def printMenu():
    menu = ["1. Update Git Origin", "2. Update Apps ", "3. View Report","4. Clean App Directories"] #"2. Get list of AUR git repository urls",  "3. Reset Git Head"
    for item in menu:
        print(item)

def loadApps():
    if os.path.exists(appDir + "updateAppNeeds.dat"):
        os.chdir(appDir)
        updateAppNeeds = pickle.load(open("updateAppNeeds.dat","rb"))
        return updateAppNeeds
    else:
            print("There are no apps in the saved array that need to be loaded.")       

def getUserChoice():

    while True:
        choice = sys.stdin.read(1) #input("What option would you like to pick?  ")
        match = re.search(r"[1-4]{1}",choice)
        if not match:
            print("Please enter valid option.")
            continue
        elif match:
            break
        else:
            print("Error no match found")
            main()

    return choice

def runOption(choice, updateAppNeeds):
    if choice == "1":
       return updateGitOrigin(updateAppNeeds)
    if choice == "2":
        updateApps(updateAppNeeds)
    if choice == "3":
        printReport(updateAppNeeds)
    elif choice == "4":
        cleanApps(updateAppNeeds)

def updateGitOrigin(report):

    #this function switches into each directory, cleans it, updates git from origin master, compiles source, then installs
    #this is the loop that loops into each directory it then runs processes in each app directory, git clean, git pull, and makepk
    if report:
        report = report
    else:
        report = []

    for folder in folders:

        #changes into app directory
        os.chdir(appDir + folder)
        print("Current Working Directory", os.getcwd())

        print("Running update routine for",folder)
        output = subprocess.run(['git','pull','origin','master'],capture_output=True)
        match = re.search('Already up to date.', str(output))

        if len(report) > 0:
            if not match and folder not in report:
                report.append(folder)
        elif not report:
            if not match:
                report.append(folder)

    os.chdir(appDir)
    pickle.dump(report,open("updateAppNeeds.dat", "wb"))
   

    return report

def printReport(report):
    print("You have the following apps that need to be updated:  ")
    print(report)

def cleanApps(updateAppNeeds):
    for app in updateAppNeeds:
        os.chdir(appDir + app)
        print("Running cleaing routines for",app)
        subprocess.run(['git','clean','-f'])


#TODO USE GLOB TO GET LATEST SRC AND INSTALL WITH OS.SYSTEM
#https://stackoverflow.com/questions/52693107/python-script-for-installing-aur-packages
#https://docs.python.org/3/library/subprocess.html#subprocess.run
#https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
def updateApps(updateAppNeeds):
    print("Runnings updateApps")
    print(updateAppNeeds)
    #clears directory
    for app in updateAppNeeds:
        os.chdir(appDir + app)
        #compiles source with makepkg
        print("Currentworking diretory: ", os.getcwd())
        print("Compiling source...")
        subprocess.run(['makepkg','-s'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        #find the latest tar.xz file
        listOfFiles = glob.glob(appDir + app + '/*.tar.*')
        print(listOfFiles)
        latestSource = max(listOfFiles, key=os.path.getctime)
        #install the compiled source
        os.system("sudo pacman -U " + latestSource)
        
        
            
def getGitUrls():

    #this functions compiles a list of aur apps in the update folders by getting the https* url from ./.git/config
    for folder in folders:
        #change into the directory and print name of directory
        os.chdir(appDir + folder)
        print("Current directory: ",appDir + folder)
    
        #if there is a ./.git then proceeed otherwise complain
        if(os.path.exists(appDir + folder + "/" +".git")):
            os.chdir(".git")
            f = open("config",'rt')
            match = re.search(r'http[\'"]?([^\'" >]+).git',f.read())
            if match:
                matchUrl = match.group(0)
                print("adding....",matchUrl)
                g = open(gitList,'w')
                g.write(matchUrl + '\n')
                g.close()
            f.close()
        else:
            print(".git directory does not exists and is probably not a git repository")
    return False

def resetHead():
    for folder in folders:
        os.chdir(appDir + folder)
        print(subprocess.run(["git","fetch","origin"],capture_output=True))
        print(subprocess.run(["git","reset","--hard","origin/master"],capture_output=True))
    return False


def main():
    printTitle()
    printMenu()
    updateAppNeeds = loadApps()
    # print(updateAppNeeds)
    # print(folders)
    choice = getUserChoice()
    if choice == "1":
        updateAppNeeds = runOption(choice, updateAppNeeds)
    else:
        runOption(choice, updateAppNeeds)

    restart = input("Would you like to do something else? (y or n) ")
    while True:
        if restart != 'y' and restart != 'n':
            print("Please enter valid input.")
            restart = input("Would you like to do something else? (y or n) ")
            continue
        elif restart == 'y':
            main()
            break
        elif restart == 'n':
            break

    # if updateAppNeeds:
    #     print("The follow apps needs to be updated: " + '\n', updateAppNeeds)
    #     while True:
    #         print("Please enter y for yes or n for no...")
    #         update = input("Would you like to update them now? y or n ")
    #         if update == "y":
    #             updateApps(updateAppNeeds)
    #             break
    #         elif update == "n": 
    #             print("Exiting...")
    #             break
    #         else:
    #             continue

def test():
    choice = input("type shit")
    print(choice.isdigit())
    while choice.isdigit():
        print("Please enter valid option.")
        printMenu()
        choice = input("What option would you like to pick?  ")
    
main()
# test()