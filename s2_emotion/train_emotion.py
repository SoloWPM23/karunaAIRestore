import sys
sys.modules['tensorflow'] = None # type: ignore

import torch
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer, EarlyStoppingCallback # type: ignore
from torch import nn
from datasets import Dataset # type: ignore
import pandas as pd
from sklearn.metrics import f1_score, classification_report
import numpy as np
import os

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device} — {torch.cuda.get_device_name(0) if device=='cuda' else 'CPU'}")

EMOTION_TO_IDX = {
    "senang": 0,
    "sedih":  1,
    "marah":  2,
    "takut":  3,
    "kaget":  4,
    "jijik":  5,
    "netral": 6,
}
IDX_TO_EMOTION = {v: k for k, v in EMOTION_TO_IDX.items()}

TOPIC_TO_IDX = {
    "pekerjaan":    0,
    "relationship": 1,
    "keluarga":     2,
    "kesehatan":    3,
    "finansial":    4,
    "self":         5,
    "other":        6,
}
IDX_TO_TOPIC = {v: k for k, v in TOPIC_TO_IDX.items()}

def load_data(csv_path: str):

    df = pd.read_csv(csv_path)

    assert "text"    in df.columns, "Kolom 'text' tidak ditemukan"
    assert "emotion" in df.columns, "Kolom 'emotion' tidak ditemukan"
    assert "topic"   in df.columns, "Kolom 'topic' tidak ditemukan"

    df = df.drop_duplicates(subset=["text"]).dropna(subset=["text", "emotion", "topic"])
    df["emotion_label"] = df["emotion"].map(EMOTION_TO_IDX)
    df["topic_label"]   = df["topic"].map(TOPIC_TO_IDX)

    unknown_emotions = df[df["emotion_label"].isna()]["emotion"].unique()
    unknown_topics   = df[df["topic_label"].isna()]["topic"].unique()
    if len(unknown_emotions) > 0:
        print(f"Emosi tidak dikenali: {unknown_emotions}")
    if len(unknown_topics) > 0:
        print(f"Topik tidak dikenali: {unknown_topics}")

    df = df.dropna(subset=["emotion_label", "topic_label"])
    df["emotion_label"] = df["emotion_label"].astype(int)
    df["topic_label"]   = df["topic_label"].astype(int)

    print(f"Dataset loaded: {len(df)} baris")
    print(f"Distribusi emosi:\n{df['emotion'].value_counts().to_string()}")
    print(f"Distribusi topik:\n{df['topic'].value_counts().to_string()}")

    return df

def split_data(df, val_ratio=0.15, random_state=42):
    from sklearn.model_selection import train_test_split
    train_df, val_df = train_test_split(
        df,
        test_size=val_ratio,
        stratify=df["emotion_label"],
        random_state=random_state
    )
    print(f"\nSplit: {len(train_df)} train, {len(val_df)} val")
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True)

class EmotionModel(nn.Module):
    def __init__(self, n_emotions=7, n_topics=7, emotion_weights=None):
        super().__init__()
        self.encoder = AutoModel.from_pretrained("indolem/indobert-base-uncased")
        self.dropout  = nn.Dropout(0.3)
        self.emotion_head = nn.Sequential(
            nn.Linear(768, 256), nn.ReLU(), nn.Dropout(0.2), nn.Linear(256, n_emotions)
        )

        self.topic_head = nn.Sequential(
            nn.Linear(768, 128), nn.ReLU(), nn.Dropout(0.2), nn.Linear(128, n_topics)
        )
        # Register as buffer so it moves to GPU with model.to(device)
        self.register_buffer("emotion_weights", emotion_weights)

    def forward(self, input_ids, attention_mask, labels=None):
        out     = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = self.dropout(out.last_hidden_state[:, 0, :])
        emotion_logits = self.emotion_head(cls_emb)
        topic_logits   = self.topic_head(cls_emb)
        loss = None
        if labels is not None:
            ce_emotion = nn.CrossEntropyLoss(weight=self.emotion_weights)
            ce_topic   = nn.CrossEntropyLoss()
            loss = ce_emotion(emotion_logits, labels["emotion"]) * 0.7 \
                 + ce_topic(topic_logits,     labels["topic"])   * 0.3
        return {"loss": loss, "emotion": emotion_logits, "topic": topic_logits}

tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")

def tokenize_batch(batch):
    enc = tokenizer(
        batch["text"],
        max_length=128,
        padding="max_length",
        truncation=True,
    )
    return {
        "input_ids":      enc["input_ids"],
        "attention_mask": enc["attention_mask"],
        "emotion_label":  batch["emotion_label"],
        "topic_label":    batch["topic_label"],
    }

class MultiHeadTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        emotion_labels = inputs.pop("emotion_label")
        topic_labels   = inputs.pop("topic_label")
        labels = {"emotion": emotion_labels, "topic": topic_labels}

        outputs = model(**inputs, labels=labels)
        loss = outputs["loss"]
        return (loss, outputs) if return_outputs else loss


    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        emotion_labels = inputs.pop("emotion_label", None)
        topic_labels = inputs.pop("topic_label", None)
        with torch.no_grad():
            outputs = model(**inputs)
            loss = None
            if emotion_labels is not None and topic_labels is not None:
                labels = {"emotion": emotion_labels, "topic": topic_labels}
                outputs_with_labels = model(**inputs, labels=labels)
                loss = outputs_with_labels["loss"]
        emotion_logits = outputs["emotion"]
        return (loss, emotion_logits, emotion_labels)
    
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    if isinstance(logits, tuple):
        emotion_logits = logits[0]
    else:
        emotion_logits = logits

    emotion_preds = np.argmax(emotion_logits, axis=-1)

    if isinstance(labels, tuple):
        emotion_labels = labels[0]
    else:
        emotion_labels = labels

    f1_macro = f1_score(emotion_labels, emotion_preds, average="macro", zero_division=0)
    f1_per_class = f1_score(emotion_labels, emotion_preds, average=None, zero_division=0)

    metrics = {"emotion_f1_macro": f1_macro}
    for i, f1 in enumerate(f1_per_class):
        metrics[f"f1_{IDX_TO_EMOTION[i]}"] = f1

    return metrics

class CurhatDataset(torch.utils.data.Dataset):
    def __init__(self, df):
        self.encodings = tokenizer(
            df["text"].tolist(),
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        self.emotion_labels = torch.tensor(df["emotion_label"].values, dtype=torch.long)
        self.topic_labels   = torch.tensor(df["topic_label"].values,   dtype=torch.long)

    def __len__(self):
        return len(self.emotion_labels)

    def __getitem__(self, idx):
        return {
            "input_ids":      self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "emotion_label":  self.emotion_labels[idx],
            "topic_label":    self.topic_labels[idx],
        }

training_args = TrainingArguments(
    output_dir="./models/emotion_engine",
    num_train_epochs=40,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=3e-5,
    weight_decay=0.05,
    warmup_ratio=0.1,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_emotion_f1_macro",
    greater_is_better=True,
    fp16=True,
    dataloader_num_workers=0,
    report_to="none",
    logging_steps=50,
    logging_dir="./logs",
    remove_unused_columns=False,
)

if __name__ == "__main__":

    CSV_PATH = "s2_emotion/data/datasetCurhat.csv"

    df = load_data(CSV_PATH)

    train_df, val_df = split_data(df)
    print("\nTokenizing dataset (mungkin 1-2 menit)...")

    train_dataset = CurhatDataset(train_df)
    val_dataset   = CurhatDataset(val_df)
    print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)}")

    print("\nLoading IndoBERT...")
    from sklearn.utils.class_weight import compute_class_weight
    raw_weights = compute_class_weight(
        "balanced",
        classes=np.arange(len(EMOTION_TO_IDX)),
        y=train_df["emotion_label"].values
    )
    emotion_weights = torch.tensor(raw_weights, dtype=torch.float).to(device)
    print(f"Class weights: { {IDX_TO_EMOTION[i]: f'{w:.2f}' for i, w in enumerate(raw_weights)} }")

    model = EmotionModel(n_emotions=7, n_topics=7, emotion_weights=emotion_weights)
    model.to(device)

    FREEZE_UP_TO_LAYER = 6
    for param in model.encoder.embeddings.parameters():
        param.requires_grad = False
    for i, layer in enumerate(model.encoder.encoder.layer):
        if i < FREEZE_UP_TO_LAYER:
            for param in layer.parameters():
                param.requires_grad = False
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total     = sum(p.numel() for p in model.parameters())
    print(f"Parameter trainable: {trainable:,} / {total:,} ({trainable/total*100:.1f}%)")
    print("Model ready")

    trainer = MultiHeadTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=8)],
    )

    print("\nMulai training...\n")
    trainer.train()

    os.makedirs("./models/emotion_engine/final", exist_ok=True)
    torch.save(model, "./models/emotion_engine/final/emotion_model.pt")
    tokenizer.save_pretrained("./models/emotion_engine/final")
    print("\nModel tersimpan di ./models/emotion_engine/final/")

    print("\nEvaluasi final pada validation set:")
    results = trainer.evaluate()
    print(f"F1 Macro : {results['eval_emotion_f1_macro']:.4f}")
    for emotion in EMOTION_TO_IDX:
        key = f"eval_f1_{emotion}"
        if key in results:
            print(f"F1 {emotion:7s}: {results[key]:.4f}")

    print("\nTarget MVP:")
    print("F1 Macro > 0.65 — PASS" if results['eval_emotion_f1_macro'] > 0.65 else "   F1 Macro < 0.65 — perlu tuning")