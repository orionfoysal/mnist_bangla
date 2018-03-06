import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from skimage import data
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb


image = imread('rifat_300.jpg', as_grey=True)
# fig, ax = plt.subplots(figsize=(10, 6))
# ax.imshow(image, cmap='gray')
# plt.show()

# apply threshold
thresh = threshold_otsu(image)
bw = closing(image > thresh, square(3))

# remove artifacts connected to image border
cleared = clear_border(bw)

# label image regions
label_image = label(cleared)
image_label_overlay = label2rgb(label_image, image=image)

fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(image, cmap='gray')

for region in regionprops(label_image):
    # take regions with large enough areas
    if region.area >= 50000:
        # print(region.area)
        # draw rectangle around segmented coins
        minr, minc, maxr, maxc = region.bbox
        print('Shape:%d X %d'%(maxr-minr,maxc-minc))
        # plt.figure()
        # plt.imshow(image[minr+20:maxr-20, minc+20:maxc-20],cmap='gray')

        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='red', linewidth=2)
        ax.add_patch(rect)

ax.set_axis_off()
plt.tight_layout()
plt.show()
