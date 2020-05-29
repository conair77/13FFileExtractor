def txt_to_xml(fName):
    # Open file and readlines
    file = open(fName, 'r')
    lines = file.readlines()
    file.close()

    count = 0
    for line in lines:
        count += 1
        if line.startswith("<informationTable xsi"): break

    del lines[0:count]  # add index of lines to remove
    del lines[-4:]

    new_file = open(fName[:-4] + ".xml", "w+")
    new_file.write("<informationTable >\n")
    for line in lines:
        new_file.write(line)
    pass