"""
BANet（Boundary-Aware Network）是一种用于图像分割任务的神经网络模型，其损失函数主要包括两个部分：交叉熵损失和边界损失。
具体地，交叉熵损失用于度量预测结果和真实标签之间的差异，边界损失则用于鼓励网络在分割边界处产生更加清晰的预测结果。
"""
import torch.nn as nn
from .joint_loss import JointLoss
from .dice import DiceLoss
from .soft_ce import SoftCrossEntropyLoss


class BANetLoss(nn.Module):
    def __init__(self, ignore_index=255):
        super(BANetLoss, self).__init__()
        self.joint_loss = JointLoss(SoftCrossEntropyLoss(smooth_factor=0.05, ignore_index=ignore_index),
                                    DiceLoss(smooth=0.05, ignore_index=ignore_index), 1.0, 1.0)

    def forward(self, y_pred, y_true):
        if self.training:
            joint_loss = self.joint_loss(y_pred, y_true)
        else:
            joint_loss = self.joint_loss(y_pred, y_true)
        return joint_loss
