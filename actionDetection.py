from mmaction.apis import inference_recognizer, init_recognizer
import mmengine
from mmengine import Config
from mmengine.runner import set_random_seed, Runner
from mmaction.evaluation import ConfusionMatrix
import os.path as osp
import os
import torch
from operator import itemgetter

class ActionDetector():
    def __init__(self):

        config_path = 'Configs/timesformer_divST_8xb8-8x32x1-15e_DoctorVCoachAug.py'
        self.config = Config.fromfile(config_path)
        self.checkpoint = 'Checkpoints/epoch_15.pth'

        self.resultsDir = './myResults'
        if not os.path.exists(self.resultsDir):
                os.makedirs(self.resultsDir)

        self.config.load_from = self.checkpoint
        self.config.test_evaluator = dict(type='AccMetric')
        self.config.work_dir = self.resultsDir

        # assign the desired device.
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print('Using device:', device)

        # build the model from a config file and a checkpoint file
        self.model = init_recognizer(self.config, self.checkpoint, device=device)

    def testVideo(self, videoPath):
        # test a single video and show the result:
        video = videoPath
        # labels = 'Configs/label_map.txt'
        results = inference_recognizer(self.model, video)

        pred_scores = results.pred_score.tolist()[:11]
        score_tuples = tuple(zip(range(len(pred_scores)), pred_scores))
        score_sorted = sorted(score_tuples, key=itemgetter(1), reverse=True)

        return score_sorted