import os
import sys

def replace(root, old_string, new_string):
    if root[-1] == "/":
        root = root[0:-1]

    for x in os.listdir(root):
        path = root + "/" + x
    
        if os.path.isdir(path):
            replace(path, old_string, new_string)
      
        else:
            p, sep, ext = path.partition('.')
            if ext in ("py", "py.tmpl"):
                infile = open(path, "r+")
                text = infile.read()
                if text.find(old_string) != -1:
                    text = text.replace(old_string, new_string)
                    infile.seek(0)
                    infile.write(text)
                    print "Replaced in " + path
                infile.close()        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <new_version>" % sys.argv[0]
        sys.exit(1)
    
    ref_file = open("djangoerp/__init__.py")
    text = ref_file.read()
    ref_file.close()
    for line in text.split("\n"):
        if line.startswith("__version__"):
            replace("djangoerp", line, "__version__ = '%s'" % sys.argv[1])
            break
  
