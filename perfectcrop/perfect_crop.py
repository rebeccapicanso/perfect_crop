from moviepy.editor import VideoFileClip
from PIL import Image
from transformers import pipeline
import cv2
import os

# please make sure you're using a term recognized by the model
print("Perfect crop currently runs on HuggingFace's models with YOLO annotation, support other annotations are to be completed later.\n")

print("please make sure you're using a term recognized by the model")
print("https://cocodataset.org/#explore")

LABEL = input("Please enter the label you are looking for.\n"
             + "Labels must be searchable at https://cocodataset.org/#explore:" )

# run the code only ever X frames (5 by default)
SKIP = 5

# build out pipeline
pipe = pipeline("object-detection", model="hustvl/yolos-tiny")

average_center = []

def save_images(input, output, search=LABEL):

    # set input as videofile
    videofile = input
    clip = VideoFileClip(videofile)
    
    # initializing..
    index = 0
    frame_no = 0

    # make output directory
    if not os.path.exists("output"):
        os.makedirs("output")

    
    for frame in clip.iter_frames():
        frame_no += 1
        if frame_no % SKIP != 0:
            continue

        # print("Detecting objects in frame", frame_no)
        
        # calling Pillow's Image function
        image = Image.fromarray(frame)

        # then tossing that image into the pipeline
        # i.e. is it there or not?
        results = pipe(image)

        for r in results:
            # print(r)
            
            # if the labeled object is in frame, yay
            # YOLO annotative obj. detect algos draw the bounding box (the square it throws around something)
            # based on max & min values. here, i'm just looking at the cross points.
            # a bounding box is an ephemeral thing. it's not recorded, its an internal throw away process.
            
            if r["label"] == search:
                box = r["box"]

                xmin = box["xmin"]
                ymin = box["ymin"]
                xmax = box["xmax"]
                ymax = box["ymax"]

                # print(xmin,ymin,xmax,ymax)

                # must make sure that the box is not out of bounds
                if xmin > 0 and xmax > 0 and ymin > 0 and ymax > 0:
                    # this is giving a harmless global error... not sure why
                    img_read= cv2.imread(r'image.png')
                    # hide the global load save error
                    # ^^ didn't get to this, check back for v2
                    
                    # As the box isn't real, I'm using cv2's rectangle function
                    # this is mostly used to determine pixel color
                    cv2.rectangle(img_read,(xmin,ymin),(xmax,ymax),(0,0,255),3)
                    
                    # calculating cross points
                    center_x = int((xmin+xmax)//2)
                    center_y = int((ymin+ymax)//2)
                    
                    # center pixel to an array
                    center = [center_x,center_y]
                    average_center.append(center)
                    # print(center)

                    index += 1
                else:
                    print("out of bounds")
                    continue
    
    # it's a little inelegant but it works without sacrificing quality

    def average_crop():
        print(average_center)

        true_center= [sum(x)/len(x) for x in zip(*average_center)]

        # now we have the coordinates of the box, we can crop the video
        clip = VideoFileClip(videofile)

        midpoint_x = true_center[0]
        midpoint_y = true_center[1]

        width = 300
        height = 300

        # jam in whatever coordinates you want, size in pixels
        video = clip.crop(x_center=midpoint_x, y_center=midpoint_y, width=width, height=height)

        # write it as the same name as the video file + _cropped
        video.write_videofile(f'{input}_label.mp4')
    
    # call average crop
    average_crop()
    
    # move clip from average crop into output directory
    # create output directory if it doesn't already exist
    if not os.path.exists(f'{output}'):
        os.makedirs(f'{output}')
    
    os.system(f'mv *.mp4 {output}')
    os.system(f'mv {output}/{input} .')

    # notify file location
    print("Files are in " + output)

if __name__ == "__main__":
    save_images(input, output)
