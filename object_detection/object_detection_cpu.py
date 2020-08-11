# Some basic setup:
import torch
import torch.nn as nn
import torch.nn.functional as F

# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import cv2

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

from skimage import transform
import torchvision
import sys

# Set the basic parameters
input_w = 640 # based on model input size
input_h = 480 # based on model input size

if __name__ == "__main__":
    # Load specific sample
    input_file = sys.argv[1]
    index = int(sys.argv[2])
    iou_thresh = float(sys.argv[3])
    data = np.load(input_file) # mid filtered has window size 256 --> each sample is 279x256
    sample = data[index,:,:]

    print("Loading pretrained model")
    # Load config from model zoo
    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cpu"
    # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0  # set threshold for this model, set to 0 because classification confidence is low
    # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
    predictor = DefaultPredictor(cfg)

    def object_detection(sample, input_w, input_h, iou_thresh):
        # device = torch.cuda.current_device()
        device = torch.device("cpu")
        input = transform.resize(sample, (input_w, input_h)) # upsample
        input_orig = torch.from_numpy(input).float().to(device)
        input = F.normalize(input_orig)
        input = torch.log(input)
        input = cv2.cvtColor(np.float32(input.cpu()),cv2.COLOR_GRAY2RGB) # convert grayscale input to 3 channel
        outputs = predictor(input)
        base_box = outputs['instances'].pred_boxes.tensor
        base_score = outputs['instances'].scores.cpu().numpy()
        nms_index = torchvision.ops.nms(base_box, outputs['instances'].scores, iou_thresh)
        box_nms = []
        scores_nms = []
        for i in nms_index:
            box_nms.append(base_box[i].cpu().numpy())
            scores_nms.append(base_score[i])
        output_instance = detectron2.structures.Instances((input_w, input_h))
        output_instance.set("pred_boxes", detectron2.structures.Boxes(box_nms))
        output_instance.set("scores", torch.tensor(scores_nms))
        return output_instance

    print("Running object detection algorithm on given sample")
    outputs = object_detection(sample, input_w, input_h, iou_thresh)

    out_name = "object_detection_" + input_file.split(".")[0]+".pickle"
    torch.save(outputs, out_name)

    print("Success!")