from PIL import Image
import sys, os

output_folder = 'output/'

# Get a list of non-zero value pixels.
def get_grid(img):
    width, height = img.size
    ret = []
    max_v = 0
    for x in range(width):
        for y in range(height):
            p = img.getpixel((x, y))
            max_v = max(max_v, p)
            if p > 0:
                ele = [y, x, p]
                ret.append(' '.join(map(str, ele)))
    print('Grid2Image: image has ', len(ret), ' non-zero entries.')
    return '\n'.join(ret)


if __name__ == '__main__':

    input_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_folder = sys.argv[2]

    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    Image.MAX_IMAGE_PIXELS = None

    if os.path.isfile(input_path):
        filename = os.path.basename(input_path)
        prefix, extension = os.path.splitext(filename)
        # filename, file_extension = os.path.splitext(file)
        output_path = os.path.join(output_folder, 'grid.txt')  # ''output/' + '.txt'
        img = Image.open(input_path)
        mat = get_grid(img)  # mat now is just a string
        with open(output_path, 'w') as output_file:
            output_file.write(mat)

    elif os.path.isdir(input_path):
        files = [os.path.join(input_path, x) for x in os.listdir(input_path)]
        for file in files:

            filename = os.path.basename(file)
            prefix, extension = os.path.splitext(filename)
            # filename, file_extension = os.path.splitext(file)
            output_path = os.path.join(output_folder, prefix + '.txt') #''output/' + '.txt'
            img = Image.open(file)
            mat = get_grid(img) # mat now is just a string

            with open(output_path, 'w') as output_file:
                output_file.write(mat)
