import csv

# Read the file, and delete the lines between START/END
outfile = open('strings.po', 'r+')
content = outfile.readlines()
start_index = content.index('#START Alienware skin\n') + 1
end_index = content.index('#END Alienware skin\n')
del content[start_index:end_index]

#Now read the CSV, and put those strings in the outfile
with open('japanese.csv') as csvfile:
     reader = csv.reader(csvfile)
     reader.next() # first line is garbage
     for row in reader:
         try:
             alphauiid,xbmcid,english,japanese,junk=row
         except ValueError:
             continue
         if xbmcid:
             content.insert(start_index, 'msgctxt "#%s"\n' % xbmcid.strip('\"'))
             content.insert(start_index+1,'msgid "%s"\n' % english)
             content.insert(start_index+2,'msgstr "%s"\n\n' % japanese)
             start_index=start_index+3

# Write the file
outfile.seek(0)
outfile.write(''.join(content))
outfile.close()
