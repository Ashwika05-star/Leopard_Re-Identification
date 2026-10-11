"""
The four AI models. Every method takes a BGR image CROP (the leopard region), exactly like training.
  validate  : is it a leopard?            (ResNet features -> your saved sklearn classifier + threshold)
  category  : Normal/Dark/Red/...          (ResNet18, 92.8%)
  viewpoint : front/left/right/back/down   (ResNet18, 81.8%)
  identity  : which individual (109 ids)   (ResNet18 + dropout head, 81.9%)
"""
import os
import cv2
import numpy as np
import joblib
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T

CATEGORIES = ["dark", "grayscale", "normal", "obscured", "red"]        # sorted, as in training
VIEWPOINTS = ["back", "down", "front", "left", "right"]                # sorted, as in training


class AIModels:
    def __init__(self, models_dir, identity_ids, validator_fail_open=False):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models_dir = models_dir
        self.fail_open = validator_fail_open
        self.tf = T.Compose([T.ToPILImage(), T.Resize((224, 224)), T.ToTensor(),
                             T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        self.category_model = self._plain("category_classifier_BEST.pth", len(CATEGORIES))
        self.viewpoint_model = self._plain("viewpoint_classifier_BEST.pth", len(VIEWPOINTS))
        self.identity_ids = list(identity_ids)
        self.identity_model = self._identity()
        self._validator()

    # ---------- loading ----------
    def _state(self, name):
        return torch.load(os.path.join(self.models_dir, name), map_location=self.device)

    def _plain(self, name, n):
        m = models.resnet18(weights=None)
        m.fc = nn.Linear(m.fc.in_features, n)
        m.load_state_dict(self._state(name))
        return m.to(self.device).eval()

    def _identity(self):
        sd = self._state("identity_classifier_v2_BEST.pth")
        n_model = sd["fc.1.weight"].shape[0]
        if n_model != len(self.identity_ids):
            raise RuntimeError(
                f"Identity classifier was trained on {n_model} leopards but the gallery CSV gives "
                f"{len(self.identity_ids)} leopards with 10+ photos. Put the exact training list "
                f"(one individual_id per line, in sorted order) in gallery_data/identity_classes.txt.")
        m = models.resnet18(weights=None)
        m.fc = nn.Sequential(nn.Dropout(0.4), nn.Linear(m.fc.in_features, n_model))
        m.load_state_dict(sd)
        return m.to(self.device).eval()

    def _validator(self):
        self.validator = joblib.load(os.path.join(self.models_dir, "resnet_leopard_classifier.pkl"))
        self.threshold = float(np.load(os.path.join(self.models_dir, "resnet_classifier_threshold.npy")))
        n_in = getattr(self.validator, "n_features_in_", None)
        self.backbone = None
        try:
            if n_in == 512:
                self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            elif n_in == 2048:
                self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            else:
                raise RuntimeError(f"validator expects {n_in} features; expected 512 (ResNet18) or 2048 (ResNet50)")
            self.backbone.fc = nn.Identity()
            self.backbone = self.backbone.to(self.device).eval()
        except Exception as e:
            if not self.fail_open:
                raise
            print(f"WARNING: validator disabled ({e})")
        self.pos_col = 1
        classes = list(getattr(self.validator, "classes_", [0, 1]))
        if 1 in classes:
            self.pos_col = classes.index(1)

    # ---------- inference ----------
    def _tensor(self, crop_bgr):
        return self.tf(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)).unsqueeze(0).to(self.device)

    @torch.no_grad()
    def _top1(self, model, crop_bgr):
        probs = torch.softmax(model(self._tensor(crop_bgr)), dim=1)
        conf, idx = probs.max(1)
        return int(idx.item()), float(conf.item())

    def category(self, crop):
        i, c = self._top1(self.category_model, crop)
        return CATEGORIES[i], c

    def viewpoint(self, crop):
        i, c = self._top1(self.viewpoint_model, crop)
        return VIEWPOINTS[i], c

    def identity(self, crop):
        i, c = self._top1(self.identity_model, crop)
        return self.identity_ids[i], c

    @torch.no_grad()
    def validate(self, crop):
        if self.backbone is None:
            return True, 1.0
        try:
            feat = self.backbone(self._tensor(crop)).cpu().numpy().reshape(1, -1)
            p = float(self.validator.predict_proba(feat)[0][self.pos_col])
            return p >= self.threshold, p
        except Exception:
            if self.fail_open:
                return True, 1.0
            raise
