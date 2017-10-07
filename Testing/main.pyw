from PIL import Image


def write_image(start_image, red, green, blue):
    image = Image.open(start_image)
    width, height = image.size
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), (red[y][x], green[y][x], blue[y][x]))

    new_image_name = "steg" + start_image
    image.save(new_image_name)
    print("Image Saved!!!")


def lsb_list(channel):
    bit_list = []
    zero_num = 0
    temp_num = 0
    for row in channel:
        for value in row:

            if value % 2 == 0:
                zero_num += 0
                temp_num = value / 2
            else:
                zero_num += 1
                temp_num = (value - 1) / 2
            if temp_num % 2 == 0:
                zero_num += 0
            else:
                zero_num += 2
            bit_list.append(zero_num)
            temp_num = 0
            zero_num = 0
    return bit_list


def return_two_lsbs_zeroed(non_zero_list, width, height):
    zero_list = []
    temp_num = 0
    zero_num = 0
    for li in non_zero_list:
        for number in li:
            if number % 2 == 0:
                zero_num += 0
                temp_num = number / 2
            else:
                zero_num += 1
                temp_num = (number - 1)/2
            if temp_num % 2 == 0:
                zero_num += 0
            else:
                zero_num += 2
            zero_list.append(number - zero_num)
            temp_num = 0
            zero_num = 0
    zero_list_nested = []
    zero_row = []
    counter = 0
    for heightCount in range(height):
        for widthCount in range(width):
            if widthCount == 0:
                zero_row = []
            zero_row.append(zero_list[counter])
            counter += 1
        zero_list_nested.append(zero_row)
    return zero_list_nested


def byte_to_quad_bit_pair(byte):
    quad_bit = []
    current = 0
    if byte >= 128:
        current += 2
        byte -= 128
    if byte >= 64:
        current += 1
        byte -= 64
    quad_bit.append(current)
    current = 0
    if byte >= 32:
        current += 2
        byte -= 32
    if byte >= 16:
        current += 1
        byte -= 16
    quad_bit.append(current)
    current = 0
    if byte >= 8:
        current += 2
        byte -= 8
    if byte >= 4:
        current += 1
        byte -= 4
    quad_bit.append(current)
    current = 0
    if byte >= 2:
        current += 2
        byte -= 2
    if byte >= 1:
        current += 1
        byte -= 1
    quad_bit.append(current)

    return quad_bit


def txt_to_steg_code(plaintext):
    plaintext = plaintext + "EOFEOFEOFEOFEOF"
    plain_list = []
    pairs_list_dec = []
    steg_list = []
    for char in plaintext:
        plain_list.append((ord(char)))
    for item in plain_list:
        pairs_list_dec.append(byte_to_quad_bit_pair(item))
    for item in pairs_list_dec:
        for subItem in item:
            steg_list.append(subItem)
    return steg_list


def image_reading(filename):
    file_extension = filename[-3:]
    image = Image.open(filename)
    width, height = image.size
    print("width: " + (str(width)))
    print("height: " + (str(height)))
    redarray = []
    greenarray = []
    bluearray = []
    if file_extension == "png":  # will work for png with alpha channel
        image.putalpha(0)  # adds alpha channel in case it is png without alpha channel, should replace existing
    for heightCount in range(height):
        for widthCount in range(width):
            if widthCount == 0:
                red_row = []
                green_row = []
                blue_row = []
            if file_extension == "png":  # will work for png with alpha channel
                red, green, blue, alpha = image.getpixel((widthCount, heightCount))
                red_row.append(red)
                green_row.append(green)
                blue_row.append(blue)
            else:
                red, green, blue = image.getpixel((widthCount, heightCount))
                red_row.append(red)
                green_row.append(green)
                blue_row.append(blue)

        redarray.append(red_row)
        greenarray.append(green_row)
        bluearray.append(blue_row)

    print("Arrays Generated")
    return redarray, greenarray, bluearray, width, height


def steg_channel(zero_channel, steg_list, down_counter, width, height, counter):
    steganography_coded_channel = []
    steg_row = []
    for heightCount in range(height):

        for widthCount in range(width):

            if widthCount == 0:
                steg_row = []
            if down_counter > 0:
                steg_row.append((zero_channel[heightCount][widthCount] + steg_list[counter]))
            else:
                steg_row.append((zero_channel[heightCount][widthCount]))
            down_counter -= 1
            counter += 1
        steganography_coded_channel.append(steg_row)
    return steganography_coded_channel, down_counter, counter


def encode():
    start_image = str(input("enter a .bmp or .png file to encode.\n"))
    redchan, greenchan, bluechan, width, height = image_reading(start_image)
    steg_list = txt_to_steg_code(str(input("enter the message to encode into the image\nDO NOT use the enter key or "
                                           "paste anything with line breaks or new lines,\nonly the first paragraph "
                                           "will be encoded.\n")))

    zero_red = return_two_lsbs_zeroed(redchan, width, height)
    zero_blue = return_two_lsbs_zeroed(bluechan, width, height)
    zero_green = return_two_lsbs_zeroed(greenchan, width, height)

    steg_red, downcounter, counter = steg_channel(zero_red, steg_list, (len(steg_list)), width, height, 0)
    steg_green, downcounter, counter = steg_channel(zero_green, steg_list, downcounter, width, height, counter)
    steg_blue, downcounter, counter = steg_channel(zero_blue, steg_list, downcounter, width, height, counter)

    write_image(start_image, steg_red, steg_green, steg_blue)

    print("Done!!\n\n\n")


def steg_decode(long_steg_list):
    length = len(long_steg_list)
    decoded_text = ""
    for index in range(0, (length - 3), 4):
        ord_num = 0
        ord_num += (long_steg_list[index]) * 64
        ord_num += (long_steg_list[(index + 1)]) * 16
        ord_num += (long_steg_list[(index + 2)]) * 4
        ord_num += (long_steg_list[(index + 3)])
        decoded_text = decoded_text + chr(ord_num)
    return decoded_text


def decode():
    start_image = str(input("enter a .bmp or .png file to decode.\n"))
    redchan, greenchan, bluechan, width, height = image_reading(start_image)
    encoded_message = lsb_list(redchan) + lsb_list(greenchan) + lsb_list(bluechan)
    separator = "EOFEOFEOFEOFEOF"

    decoded_message = str(steg_decode(encoded_message))

    decoded_message = decoded_message.split(separator, 1)[0]
    print("the encoded message was:\t" + decoded_message)


option = ""
while option != "quit":
    option = str(input('Type "encode" to encode a message into an image and "decode" to read a message from an image, '
                       'when finished type "quit" to end the program\n').lower())
    if option == "encode":
        encode()
    elif option == "decode":
        decode()
    elif option != "quit":
        print("I don't understand that, please retry below.")

print("Program quitting")
print("Goodbye!")

