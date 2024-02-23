import cv2
import numpy as np
import math
  

def get_contours(img, img_contour, contour_type):
    if contour_type == "line":
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(len(contours))
    
    rectangle_contours = []
    line_contours = []
    
    for i in range(len(contours)):
        peri = cv2.arcLength(contours[i], True)
        approx = cv2.approxPolyDP(contours[i], 0.02 * peri, True)
        area = cv2.contourArea(contours[i])

        rect = cv2.minAreaRect(contours[i])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        center = rect[0]
        size = rect[1]
        angle = rect[2]

        if contour_type == "line":
            if area >= 5:
                if size[0] < 20 or size[1] < 20:
                    cv2.drawContours(img_contour, [box], 0, (0, 0, 255), 2)
                    print(f"Contour {i} may be line.")
                    line_dict = {'contour': i,
                                 'center': center,
                                 'size': size,
                                 'angle': angle,
                                 'area': area,
                                 'box': box}
                    line_contours.append(line_dict)
        else:
            x_start = box[3][0]
            y_start = box[3][1]
            a = box[0][0]
            b = box[0][1]
            c = box[2][0]
            d = box[2][1]
            d1 = math.sqrt((x_start - a) ** 2 + (y_start - b) ** 2)
            d2 = math.sqrt((x_start - c) ** 2 + (y_start - d) ** 2)
            if d1 >= d2:
                x_end = x_start - int(size[0])
                y_end = y_start - int(size[1])
            else:
                x_end = x_start + int(size[1])
                y_end = y_start - int(size[0])

            cv2.drawContours(img_contour, [box], 0, (0, 0, 255), 3)
            rect_dict = {'contour': i,
                         'center': center,
                         'size': size,
                         'angle': angle,
                         'area': area,
                         'box': box,
                         'BBpoints': [x_start, y_start, x_end, y_end]}
            rectangle_contours.append(rect_dict)

    if contour_type == "line":
        print(len(line_contours))
        similar_line_list = []
        while len(line_contours) != 0:
            similar_line = []
            line = line_contours[0]
            similar_line.append(line)
            for j in range(1, len(line_contours)):
                if j < len(line_contours):
                    if abs(line['center'][0] - line_contours[j]['center'][0] < 10 and line['center'][1] -
                           line_contours[j]['center'][1] < 10.0):
                        if abs(line['angle'] - line_contours[j]['angle']) < 1.0:
                            if abs(line['area'] - line_contours[j]['area']) < 175:
                                similar_line.append(line_contours[j])
                                print(f"Contours- {line['contour']} and {line_contours[j]['contour']} are same !!!")
                                del line_contours[j]
                                print(f"Length of line_contours : {len(line_contours)}")
            del line_contours[0]
            similar_line_list.extend([similar_line])

        for similar_lines in similar_line_list:
            if len(similar_lines) > 1:
                if similar_lines[0]['area'] < similar_lines[1]['area']:
                    line_contours.append(similar_lines[0])
                    print(f"Line {similar_lines[0]['contour']} is added to Line Contours")
                else:
                    line_contours.append(similar_lines[1])
                    print(f"Line {similar_lines[1]['contour']} is added to Line Contours")

            else:
                line_contours.append(similar_lines[0])
                print(f"Line {similar_lines[0]['contour']} is added to Line Contours")
        return line_contours

    else:
        return rectangle_contours
  
def stack_images(scale, img_array):
    rows = len(img_array)
    cols = len(img_array[0])
    rows_available = isinstance(img_array[0], list)
    width = img_array[0][0].shape[1]
    height = img_array[0][0].shape[0]
    
    if rows_available:
        for x in range(rows):
            for y in range(cols):
                if img_array[x][y].shape[:2] == img_array[0][0].shape[:2]:
                    img_array[x][y] = cv2.resize(img_array[x][y], (0, 0), None, scale, scale)
                else:
                    img_array[x][y] = cv2.resize(img_array[x][y], (img_array[0][0].shape[1], img_array[0][0].shape[0]), None, scale, scale)
                    
                if len(img_array[x][y].shape) == 2:
                    img_array[x][y] = cv2.cvtColor(img_array[x][y], cv2.COLOR_GRAY2BGR)
                    
        image_blank = np.zeros((height, width, 3), np.uint8)
        hor = [image_blank] * rows
        
        for x in range(rows):
            hor[x] = np.hstack(img_array[x])
            
        ver = np.vstack(hor)
        
    else:
        for x in range(rows):
            if img_array[x].shape[:2] == img_array[0].shape[:2]:
                img_array[x] = cv2.resize(img_array[x], (0, 0), None, scale, scale)
            else:
                img_array[x] = cv2.resize(img_array[x], (img_array[0].shape[1], img_array[0].shape[0]), None, scale, scale)
                
            if len(img_array[x].shape) == 2:
                img_array[x] = cv2.cvtColor(img_array[x], cv2.COLOR_GRAY2BGR)
                
        hor = np.hstack(img_array)
        ver = hor
        
    return ver

def main():
    image = cv2.imread('image.jpg')
    original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.putText(original_image, "Original RGB Image", (120, 28), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
    cv2.imshow("Original Image", original_image)
    
    blank_image = cv2.imread('blank.jpg')

    image_contour = image.copy()

    image_blur = cv2.GaussianBlur(image, (7, 7), 1)
    image_gray = cv2.cvtColor(image_blur, cv2.COLOR_BGR2GRAY)

    image_canny = cv2.Canny(image_gray, 20, 23)

    line_contours = get_contours(image_canny, image_contour, "line")
    rectangle_contours = get_contours(image_canny, image_contour, "rectangle")

    rotated_image_contour = image.copy()

    for rect_contour in rectangle_contours:
        cv2.rectangle(rotated_image_contour, (rect_contour['BBpoints'][0], rect_contour['BBpoints'][1]),
                      (rect_contour['BBpoints'][2], rect_contour['BBpoints'][3]), (0, 255, 0), 2)
        cv2.putText(rotated_image_contour, "Rectangle Aligned Image", (120, 28), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        cv2.rectangle(blank_image, (rect_contour['BBpoints'][0], rect_contour['BBpoints'][1]),
              (rect_contour['BBpoints'][2], rect_contour['BBpoints'][3]), (0, 0, 0), 2)
        cv2.putText(blank_image, "Rectangle Aligned Image", (120, 28), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        cv2.imshow("Rectangular Alignment Window", blank_image)

    cv2.putText(image, "BGR Image", (120, 28), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, ), 2)
    cv2.putText(image_blur, "Blur Image", (120, 28), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
    cv2.putText(image_gray, "Gray Image", (120, 28), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
    cv2.putText(image_canny, "Canny Image", (120, 28), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image_contour, "Minimum Area Bounded", (120, 28), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)

    img_stacked = stack_images(0.8, ([image, image_blur, image_gray],[image_canny, image_contour, rotated_image_contour]))

    cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
    cv2.imshow("Result", img_stacked)
    cv2.waitKey(0)

    print("Task Completed")


if __name__ == "__main__":
    main()
