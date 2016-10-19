def fill_template(file, values):
    template_file= file+".templ"
    outfile = open(file,"w")
    infile = open(template_file,"r")
    for line in infile:
        outline = ""
        line = line.rstrip()
        if line.find("{{*") > -1:
          while line.find("{{*") > -1:
            starti = line.find("{{*")
            outline+= line[:starti]
            endi = line.find("*}}")
            parname = line[starti+3:endi]
            if parname in values:
                outline += values[parname]
                line = line[endi+3:]
            else:
                print("Error:",parname,"in template:",template_file," not given")
                return
        #else:
        outline += line
        outfile.write(outline+"\n")
        
    outfile.close()
    infile.close()
