# python process_results.py /media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/sample-output/Danvers-NN-VehSeg-Workzone/20230601_014414.mp4

import cv2
import os
import argparse
import numpy as np
import glob
import copy
import math
import datetime

height, width = 0, 0
frame_number = 0

dict_veh_FramesLoc = {} #key: trackID. Value: List of list [[(frameNo, [(x1, y1), (x2, y2), ...])], [], [], ..., catID]
dict_frame_LaneLoc = {} # storing only frames of interest. Key: frameNo. Value is polygon points of the highway.
dict_category = {0:"UNK", 1:"Small", 2:"Medium", 3:"Large", 4:"Person"}

def create_dict_veh_FramesLoc(veh_labels_dir, dict_veh_FramesLoc):
    #global dict_veh_FramesLoc
    #Note: In opencv frame no. starts from 0.
    for item in os.listdir(veh_labels_dir):
        item_path = os.path.join(veh_labels_dir, item)
        if os.path.isfile(item_path) and item.lower().endswith('.txt'):
            f_no = int(item_path.split('_')[-1][:-4])
            #print(f_no)
            with open(item_path, 'r') as file:
                for line in file:
                    # YOLO format: clsID x1 y1 x2 y2 x3 y3... trackID
                    num_list = line.split()
                    # If trackID not present in line, ignore.
                    if '.' in num_list[-1]: # last item is not an integer trackID
                        continue
                    
                    trackID = int(num_list[-1])
                    catID = int(num_list[0])
                    pts_lst = num_list[1:-1]
                    pts_lst_tpl = [(int(float(pts_lst[i]) * width), int(float(pts_lst[i + 1]) * height)) for i in range(0, len(pts_lst), 2)]
                    #print(pts_lst_tpl) #[(080.1562, 044.5312), (0.810938, 0.457031), (0.810938, 0.447266), (0.809375, 0.445312)]
                    #TO DO: Maybe check if polygon is single blob
                    if trackID in dict_veh_FramesLoc:
                        dict_veh_FramesLoc[trackID].append([f_no, pts_lst_tpl, catID]) 
                    else:
                        dict_veh_FramesLoc[trackID] = [[f_no, pts_lst_tpl, catID]]
    return dict_veh_FramesLoc #working
    
def is_point_on_right_of_line(test_point):
    point1 = (0., 512.)
    point2 = (500., 270.)
    vector_line = (point2[0] - point1[0], point2[1] - point1[1])
    vector_test = (test_point[0] - point1[0], test_point[1] - point1[1])

    cross_product = vector_line[0] * vector_test[1] - vector_line[1] * vector_test[0]

    return cross_product > 0

def check_dist_lane_draw(dict_veh_FramesLoc, laneLabelsFolder, vidPath):
    wait_frames = 30 #or use frame where the vehicle is nearest to a given point on the highway boundary.
    start_point_veh, end_point_lane = (0., 0.), (0., 0.)
    #For each trackID loop
    for trkID in dict_veh_FramesLoc:
        if len(dict_veh_FramesLoc[trkID]) <= wait_frames:
            continue
        #sorted_list = sorted(original_list, key=lambda x: x[0])
        dict_veh_FramesLoc[trkID] = sorted(dict_veh_FramesLoc[trkID], key=lambda x: x[0]) #sorted list based on frameNo
        f_no = dict_veh_FramesLoc[trkID][wait_frames][0]
        veh_poly = dict_veh_FramesLoc[trkID][wait_frames][1]
        cat_ID = dict_veh_FramesLoc[trkID][wait_frames][2]
        rightmost_veh_point = (0., 0.)#max(veh_poly, key=lambda veh_poly: veh_poly[0])
        for p in veh_poly:
            if p[0] > rightmost_veh_point[0]:
                rightmost_veh_point = p
        # Ignore vehicle tracks starting on upper half of frame
        if rightmost_veh_point[1] < 310:#270:
            continue
        #print("\n\n")
        #print(trkID)
        #print(f_no)
        #print(veh_poly)
        #print(rightmost_veh_point) #(0.367188, 0.769531)
        #Open correspondinig lane label file
        file_pattern = f"{laneLabelsFolder}/*_{f_no}.txt" #TO DO: if file doesn't exist, open the next one. Else part?
        matching_files = glob.glob(file_pattern)
        #Highway label is 3
        lane_poly = []
        if matching_files:
            file_labels = matching_files[0]
            with open(file_labels, 'r') as file:
                for line in file:
                    point_list = line.split()
                    if point_list[0] != '3':
                        continue
                    point_list_noCls = copy.deepcopy(point_list[1:])
                    lane_poly = [(int(float(point_list_noCls[i]) * width), int(float(point_list_noCls[i + 1]) * height)) for i in range(0, len(point_list_noCls), 2)]
                    
                    #print("point_list_noCls len:")
                    #print(len(point_list_noCls))
        # Find the shortest distance between rightmost_veh_point and a point on points to right (from lane poly)
        points_to_right = [point for point in lane_poly if point[0] > rightmost_veh_point[0] ]
        points_to_right = [point for point in lane_poly if is_point_on_right_of_line(point)]
        #print(points_to_right)
        closest_point = (0.,0.)
        if points_to_right:
            closest_point = min(points_to_right, key=lambda point: math.dist(rightmost_veh_point, point))
        
        #print(len(lane_poly))
        #print(matching_files)
        #rightmost_veh_point = (int(rightmost_veh_point[0]*width), rightmost_veh_point[1])
        #rightmost_veh_point = (rightmost_veh_point[0], int(rightmost_veh_point[1]*height))
        #closest_point = (int(closest_point[0]*width), closest_point[1])
        #closest_point = (closest_point[0], int(closest_point[1]*height))
        #print("\n")
        #print(rightmost_veh_point)
        #print(closest_point)

        #os.mkdir(vidPath.split('/')[-1])
        if math.dist(rightmost_veh_point, closest_point) < 45 and closest_point[0] - rightmost_veh_point[0] > 5:
            cat_name = dict_category[cat_ID]
            output_path = os.path.join("out", vidPath.split('/')[-1], f"output_frame-{trkID}-{f_no}-{cat_name}.png") #vidPath
            print(output_path)
            save_frame_with_horizontal_line(vidPath, f_no, output_path, rightmost_veh_point, closest_point)
            with open(os.path.join(os.path.dirname(output_path), "data.txt"), "a") as file:
                file.write(f"{f_no},{str(datetime.timedelta(seconds=float(f_no/29.0)))},{trkID},{cat_name}" + "\n")
    return 0#(start_point_veh, end_point_lane)

def drawPolygon(frame, polyPoints):
    polygon_points = np.array([
        (50, frame.shape[0] // 2),
        (100, frame.shape[0] // 3),
        (150, frame.shape[0] // 4),
        (200, frame.shape[0] // 4),
        (250, frame.shape[0] // 3),
        (300, frame.shape[0] // 2)
    ], np.int32)
    polygon_points = polygon_points.reshape((-1, 1, 2))
    frame = cv2.polylines(frame, [polygon_points], isClosed=True, color=(0, 255, 0), thickness=2)
    return frame
    
def drawLine(frame, start_point, end_point, line_color, line_thickness):
    #line_start = (20, frame.shape[0] // 2)
    #line_end = (100, frame.shape[0] // 2)
    cv2.line(frame, start_point, end_point, line_color, line_thickness)
    return frame

def save_frame_with_horizontal_line(video_path, frame_number, output_path, line_start, line_end):
    global height
    global width
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Check if the requested frame number is within valid range
    if frame_number < 0 or frame_number >= total_frames:
        print(f"Error: Invalid frame number. Must be between 0 and {total_frames - 1}")
        cap.release()
        return

    # Set the capture to the desired frame number
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frame
    ret, frame = cap.read()
    height = frame.shape[0]
    width = frame.shape[1]

    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read frame")
        cap.release()
        return
    #frame = drawPolygon(frame, [2,4])
    
    
    # Draw a horizontal line on the frame
    line_color = (75, 75, 205)  # color in BGR format
    line_thickness = 1
    frame = drawLine(frame, line_start, line_end, line_color, line_thickness)
    
    # Save the modified frame as a PNG image
    cv2.imwrite(output_path, frame)

    # Release the video capture object
    cap.release()

    print(f"Frame {frame_number} saved as {output_path}")


# Create an argument parser
parser = argparse.ArgumentParser(description="Save a specific frame from a video with a horizontal line.")
# Add arguments to the parser
parser.add_argument("veh_folder_path", help="Path to the input video file")

# Parse the command-line arguments
args = parser.parse_args()

# Input parameters
veh_folder_path = args.veh_folder_path

lane_folder_path = veh_folder_path.replace("Danvers-NN-VehSeg-Workzone", "Danvers-NN-LaneGore-Workzone")
video_name = veh_folder_path.split('/')[-1]
video_path = os.path.join(veh_folder_path, video_name)

output_folder = "out"
output_folder = os.path.join(output_folder, video_name)
# Check if the folder already exists
if not os.path.exists(output_folder):
    # Create the folder
    os.mkdir(output_folder)
    print(f"Folder '{output_folder}' created successfully.")
else:
    print(f"Folder '{output_folder}' already exists.")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video file")
else:
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

# Process vehicle labels folder 
veh_label_folder = os.path.join(veh_folder_path, "labels") #labelsV-few #44002 count
lane_label_folder = os.path.join(lane_folder_path, "labels") #labelsL-few #count

file_count = 0
# Iterate through all items in the veh folder
for item in os.listdir(veh_label_folder):
    item_path = os.path.join(veh_label_folder, item)
    if os.path.isfile(item_path):
        file_count += 1
print(f'Items in vehicle labels folder= {file_count}.')

file_count = 0
# Iterate through all items in the laneGore folder
for item in os.listdir(lane_label_folder):
    item_path = os.path.join(lane_label_folder, item)
    if os.path.isfile(item_path):
        file_count += 1
#print(f'Items in LaneGore labels folder= {file_count}.')

dict_veh_FramesLoc = create_dict_veh_FramesLoc(veh_label_folder, dict_veh_FramesLoc) #key: trackID. Value: List of list [[(frameNo, [(x1, y1), (x2, y2),...])], [],...]
#print(dict_veh_FramesLoc)

# Now check the 15th frame (half second elapse) of each track and how far it is from the right border of the highway
line_points = check_dist_lane_draw(dict_veh_FramesLoc, lane_label_folder, video_path)


exit(0)

#'/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/sample-output/veh-seg/20230601_014414.mp4/20230601_014414.mp4'
frame_number = 450# int(input("Enter the frame number: "))
output_folder = "out"
output_folder = os.path.join(output_folder, video_name)
# Check if the folder already exists
if not os.path.exists(output_folder):
    # Create the folder
    os.mkdir(output_folder)
    print(f"Folder '{output_folder}' created successfully.")
else:
    print(f"Folder '{output_folder}' already exists.")

output_path = os.path.join(output_folder, f"output_frame-{frame_number}.png")
line_start_veh = (80, 175)
line_end = (315, 175)

# Call the function to save the frame with the horizontal line
save_frame_with_horizontal_line(video_path, frame_number, output_path, line_start_veh, line_end)

