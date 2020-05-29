def txt_to_xml(filename):
        # Open file and read the lines of the file and then close the file
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()

        # Create count variable to index where the xml of the data table info begins
        count = 0
        for line in lines:
                count += 1
                if line.startswith("<informationTable xsi"): break

        # Remove all lines up to the first line of the data table xml info
        del lines[0:count]

        # Remove last 4 lines of excess data
        del lines[-4:]

        # Write new info to new file which doesnt contain deleated files
        new_file = open(filename[:-4] + ".xml", "w+")
        new_file.write("<informationTable >\n")
        for line in lines:
                new_file.write(line)