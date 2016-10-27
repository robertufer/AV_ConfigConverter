import re
import os


def main():
    fileinout()
    menu()
    searches()


def fileinout():
    global temp_file
    global inputfolderfiles
    global outputfolderfiles
    global baseconfig
    inputpathcheck = os.path.exists(r'.\Inputfiles') # check if folder exists
    outputpathcheck = os.path.exists(r'.\Outputfiles') # check if folder exists
    print(inputpathcheck)
    inputfolderfiles = os.listdir(r'.\Inputfiles')
    print(inputfolderfiles)
    print(type(inputfolderfiles))
    outputfolderfiles = os.listdir(r'.\Outputfiles')
    baseconfig = open('_base cisco l3 switch config.txt','r')

def menu():
    ans = True
    while ans:
        print("""
----------------------------------------------------------------------
|                 Switch config converter (mostly)                   |
----------------------------------------------------------------------

 Select option:
  1. List files in input directory
  2. List files in output directory
  3. list contents of config base file
  4. Kick off conversion process
  5. Exit



""")
        ans = input("Choose option : ")
        if ans == "1":
            print("""
----------------------------
| input directory contents |
----------------------------""")
            print(inputfolderfiles)
        elif ans == "2":
            print("""
-----------------------------
| output directory contents |
-----------------------------""")
            print(outputfolderfiles)
        elif ans == "3":
            print("base config contents")
            print(baseconfig.read())
        elif ans == "4":
            ans = False
        elif ans == "5":
            raise SystemExit
        else:
            print("no good")


def searches():
    # adding in function to pull from input folder and assign fine name to var
    print("Input files found : "+str(inputfolderfiles))
    for inputfilename in inputfolderfiles:
        with open(".\Inputfiles\\"+inputfilename) as input_file:

            # hostname to filename builder for output file
            result = re.search('(cli prompt ")(.+)' , input_file.read())
            result = result.group(2)
            result = result.replace('"', '')
            print(result)
            outputfilename = result
            outputfiledestination = open('.\Outputfiles\\'+result+'.txt', 'w+')
            print("file name set")

            # add in base config to file
            print(baseconfig.read(), file = outputfiledestination)
            print("base config output to "+outputfilename)

            # Hostname grabber
            input_file.seek(0)
            result = re.search('(cli prompt ")(.+)' , input_file.read())
            result = result.group(2)
            result = result.replace('" ', '')
            print("hostname "+result, file = outputfiledestination)
            print("hostname "+result+" converted")
        
            # SNMP server info grabber
            input_file.seek(0)
            result = re.search('(sys set location )(.+)' , input_file.read())
            result = result.group(2)
            result = result.replace('"', "")
            print("snmp-server location "+result, file = outputfiledestination)
            print("snmp server converted")
        
            # vlan database creation
            input_file.seek(0)
            result = re.finditer('(vlan \d{1,4}) create byport 1 name \"(.+)' , input_file.read())
            for item in result:
                print(item.group(1)+"\n "+"name "+item.group(2).strip('"'), file = outputfiledestination)

            # vlan interfaces
            input_file.seek(0)
            result = re.finditer('vlan (\d{1,4}) ip create (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_file.read())
            for i in result:
                vlannumber = i.group(1)
                vlanip = i.group(2)
                vlansnmask = i.group(3)
            print("interface vlan "+vlannumber+"\n ip address "+vlanip+" "+vlansnmask)
            print("vlan ints converted")

            # Loopback interface
            input_file.seek(0)
            result = re.search(r'ip circuitless-ip-int  1 create (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_file.read())
            result = result.group(1)
            print("interface loopback 0\n ip address "+result, file = outputfiledestination)
            print("loopback converted")

            # OSPF conversion
            input_file.seek(0)
            result = re.search(r'ip ospf router-id (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_file.read())
            input_file.seek(0)
            resultarea = re.search(r'ip ospf area \d{1,3}\.\d{1,3}\.(\d{1,3})\.\d{1,3} create', input_file.read())
            result = result.group(1)
            resultarea = resultarea.group(1)
            print("router ospf  "+resultarea+"\n router-id "+result+"\n passive-interface default", file = outputfiledestination)
            print("ospf info converted")

            # Switch Stack conversion - possible additional feature to convert a set of individual switches to a stack
            # switchnumber = input("what is the new switch number of __") (for stacking if we need to stack individuals)


            # vlan port info
            switchnumber = "1"
            input_file.seek(0)
            result = re.finditer('(vlan (\d{1,4}) ports add (.+)member portmember)' , input_file.read())
            for i in result: #going into each step in the iter
                vlannumber = i.group(2) # vlannumber is string var of vlan tag
                vlanports = i.group(3) # string of csv port listing
                singleportmatch = re.compile(r'(\d/\d{1,2})[.,^ - ]')
                portrangematch = re.compile(r'(\d/\d{1,2})-\d/(\d{1,2})')
                singlematches = re.findall(singleportmatch,vlanports)
                rangematches = re.findall(portrangematch,vlanports)
                singlematches = ["interface t" + var + " allowed vlan add " + vlannumber for var in singlematches]
                for i in singlematches:
                    print(i,file = outputfiledestination)
                for i in rangematches: # port range is a list of tuples, this pulls them into a list and prints
                    print("interface range "+i[0]+" - "+i[1]+" allowed vlan add "+vlannumber, file = outputfiledestination)
            print("vlan to port mapping converted")

    
            # OSPF networks (for reference, keep at end of config)
            input_file.seek(0)
            result = re.finditer(r'ip ospf interface (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) area (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_file.read())
            for i in result:   
                ospfnetwork = i.group(1)
                resultarea = i.group(2)
                print("! (ospf) network "+ospfnetwork+" x.x.x.x area "+resultarea, file = outputfiledestination)
            print("OSPF networks added as comments")
        print("device "+outputfilename+" converted and output to ./Outputfiles")

main() 