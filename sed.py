import os
import sys

def main():
    assert len(sys.argv) == 3
    src = sys.argv[1]
    dst = sys.argv[2]

    try: 
        os.mkdir(dst)
    except FileExistsError:
        print(dst + ' already exists')

    for filename in os.listdir(src):
        with open(os.path.join(src, filename), 'r') as file:
                lines = file.read()
                lines = lines.replace('\\\"', '')
                with open(os.path.join(dst, filename), 'w') as g:
                    g.write(lines)

if __name__ == "__main__":
    main()
