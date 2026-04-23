import torch
from torch import nn
from transformers import AutoTokenizer, AutoModel
from transformers.models.bert import modeling_bert
from dataclasses import dataclass

# ── Compatibility patch for missing BertSdpaSelfAttention ──────────────────────
# Model was trained with transformers ~4.35-4.44 which had BertSdpaSelfAttention.
# Newer versions removed/renamed this class. We alias it to BertSelfAttention.
if not hasattr(modeling_bert, 'BertSdpaSelfAttention'):
    modeling_bert.BertSdpaSelfAttention = modeling_bert.BertSelfAttention
if not hasattr(modeling_bert, 'BertSdpaAttention'):
    modeling_bert.BertSdpaAttention = modeling_bert.BertAttention

class EmotionModel(nn.Module):
    """Mirror of the training class — required for torch.load unpickling."""
    def __init__(self, n_emotions=7, n_topics=7, emotion_weights=None):
        super().__init__()
        self.encoder = AutoModel.from_pretrained("indolem/indobert-base-uncased")
        self.dropout = nn.Dropout(0.3)
        self.emotion_head = nn.Sequential(
            nn.Linear(768, 256), nn.ReLU(), nn.Dropout(0.2), nn.Linear(256, n_emotions)
        )
        self.topic_head = nn.Sequential(
            nn.Linear(768, 128), nn.ReLU(), nn.Linear(128, n_topics)
        )
        # Register as buffer so it moves to GPU with model.to(device)
        if emotion_weights is not None:
            self.register_buffer("emotion_weights", emotion_weights)

    def forward(self, input_ids, attention_mask, labels=None):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = self.dropout(out.last_hidden_state[:, 0, :])
        emotion_logits = self.emotion_head(cls_emb)
        topic_logits = self.topic_head(cls_emb)
        loss = None
        if labels is not None:
            ce_emotion = nn.CrossEntropyLoss(weight=self.emotion_weights if hasattr(self, 'emotion_weights') else None)
            ce_topic   = nn.CrossEntropyLoss()
            loss = ce_emotion(emotion_logits, labels["emotion"]) * 0.7 \
                 + ce_topic(topic_logits, labels["topic"]) * 0.3
        return {"loss": loss, "emotion": emotion_logits, "topic": topic_logits}

EMOTION_LABELS = {0:"senang", 1:"sedih", 2:"marah", 3:"takut", 4:"kaget", 5:"jijik", 6:"netral"}
TOPIC_LABELS   = {0:"pekerjaan", 1:"relationship", 2:"keluarga", 3:"kesehatan", 4:"finansial", 5:"self", 6:"other"}

@dataclass
class EmotionResult:
    """Result from emotion analysis — used by orchestrator."""
    dominant     : str
    score        : float
    distribution : dict
    topics       : list
    distress_score: float 

def _patch_bert_config(model):
    """Fix missing config attributes for newer transformers versions."""
    if hasattr(model, 'encoder') and hasattr(model.encoder, 'config'):
        cfg = model.encoder.config
        defaults = {
            'output_attentions': False,
            'output_hidden_states': False,
            'use_cache': True,
            'chunk_size_feed_forward': 0,
            'is_decoder': False,
            'add_cross_attention': False,
        }
        for attr, val in defaults.items():
            if not hasattr(cfg, attr):
                setattr(cfg, attr, val)

class EmotionEngine:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        import types, pickle
        # Register EmotionModel under __main__ so torch.load can unpickle it
        import __main__
        __main__.EmotionModel = EmotionModel
        self.model = torch.load(f"{model_path}/emotion_model.pt", map_location=self.device, weights_only=False)
        _patch_bert_config(self.model)
        self.model.eval()
        self.model.to(self.device)

    def analyze(self, text: str) -> EmotionResult:
        """
        Analyze emotion from text.

        Returns:
            EmotionResult with dominant emotion, distribution, topics, and distress score.
        """
        inputs = self.tokenizer(text, max_length=128, padding="max_length",
                                truncation=True, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items() if k in ("input_ids", "attention_mask")}
        with torch.no_grad():
            outputs = self.model(**inputs)
        emotion_probs = torch.softmax(outputs["emotion"], dim=-1)[0]
        topic_probs   = torch.softmax(outputs["topic"],   dim=-1)[0]
        dominant_idx  = emotion_probs.argmax().item()

        # Distress = sedih(1) + marah(2) + takut(3) + jijik(5)
        distress = (emotion_probs[1] + emotion_probs[2] + emotion_probs[3] + emotion_probs[5]).item()

        topics   = [TOPIC_LABELS[i] for i, prob in enumerate(topic_probs) if prob > 0.3]
        return EmotionResult(
            dominant=EMOTION_LABELS[dominant_idx],
            score=emotion_probs[dominant_idx].item(),
            distribution={EMOTION_LABELS[i]: p.item() for i, p in enumerate(emotion_probs)},
            topics=topics if topics else ["other"],
            distress_score=distress
        )