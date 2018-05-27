import  re, subprocess, sys

if len(sys.argv) != 2:
    exit()

in_file = sys.argv[1]

with open(in_file, 'r') as f:
    reader = f.read()

networks = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}\/\d{2}', reader)

for net in networks:
    p = subprocess.Popen(["ufw", "deny", "from", net], stdout=subprocess.PIPE)
    output, err = p.communicate()
    print  (output)
