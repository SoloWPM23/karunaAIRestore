import sys
sys.modules['tensorflow'] = None

import torch
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
from torch import nn
import pandas as pd
from sklearn.metrics import f1_score, recall_score, precision_score, classification_report
from sklearn.model_selection import train_test_split
import numpy as np
import os

# ── Cek GPU ───────────────────────────────────────────────────────────────
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device} — {torch.cuda.get_device_name(0) if device=='cuda' else 'CPU'}")

# ── Label Mapping ─────────────────────────────────────────────────────────
CRISIS_TO_IDX = {
    "safe":     0,
    "at_risk":  1,
    "crisis":   2,
}
IDX_TO_CRISIS = {v: k for k, v in CRISIS_TO_IDX.items()}

# ── Class Weights (kompensasi imbalanced dataset) ─────────────────────────
# Gunakan bobot yang moderat: cukup nudge model, bukan mendominasi loss.
# Rumus aman: inverse frequency yang dinormalisasi
# safe≈42% → 1.0, at_risk≈35% → 1.2, crisis≈23% → 1.8
CLASS_WEIGHTS = torch.tensor([1.0, 1.2, 1.8], dtype=torch.float)

# ── Load & Prepare Dataset ────────────────────────────────────────────────
def load_data(csv_path: str):
    """
    Load CSV dengan kolom: text, label (0/1/2), label_name (safe/at_risk/crisis)
    """
    df = pd.read_csv(csv_path)

    # Validasi kolom
    assert "text"       in df.columns, "Kolom 'text' tidak ditemukan"
    assert "label"      in df.columns, "Kolom 'label' tidak ditemukan"
    assert "label_name" in df.columns, "Kolom 'label_name' tidak ditemukan"

    # Bersihkan
    df = df.drop_duplicates(subset=["text"]).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)

    # Validasi nilai label
    valid_labels = {0, 1, 2}
    invalid = set(df["label"].unique()) - valid_labels
    if invalid:
        print(f"Label tidak dikenali: {invalid} — baris tersebut akan dihapus")
        df = df[df["label"].isin(valid_labels)]

    print(f"Dataset loaded: {len(df)} baris")
    print(f"Distribusi kelas:")
    for name, count in df["label_name"].value_counts().items():
        pct = count / len(df) * 100
        print(f"   {name:10s}: {count:4d} ({pct:.1f}%)")

    return df.reset_index(drop=True)

# ── Train/Val Split ───────────────────────────────────────────────────────
def split_data(df, val_ratio=0.15, random_state=42):
    """
    Stratified split — pastikan proporsi tiap kelas sama di train dan val.
    Penting untuk kelas crisis yang jumlahnya sedikit.
    """
    train_df, val_df = train_test_split(
        df,
        test_size=val_ratio,
        stratify=df["label"],  # Stratified by crisis level
        random_state=random_state
    )
    print(f"\nSplit: {len(train_df)} train | {len(val_df)} val")
    print(f"Val crisis  : {(val_df['label']==2).sum()} sampel")
    print(f"Val at_risk : {(val_df['label']==1).sum()} sampel")
    print(f"Val safe    : {(val_df['label']==0).sum()} sampel")
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True)

# ── Model ─────────────────────────────────────────────────────────────────
class CrisisModel(nn.Module):
    """
    Single-head crisis detector berbasis IndoBERT.
    Berbeda dengan EmotionModel (multi-head), CrisisModel hanya butuh
    satu output: level krisis (safe / at_risk / crisis).
    """
    def __init__(self, n_classes=3):
        super().__init__()
        self.encoder = AutoModel.from_pretrained("indolem/indobert-base-uncased")
        self.dropout = nn.Dropout(0.3)
        # Classifier head: 768 → 256 → 3
        self.classifier = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, n_classes)
        )

    def forward(self, input_ids, attention_mask, labels=None):
        out     = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_emb = self.dropout(out.last_hidden_state[:, 0, :])  # [CLS] token
        logits  = self.classifier(cls_emb)

        loss = None
        if labels is not None:
            # Weighted CrossEntropy — berikan penalti lebih besar jika
            # model melewatkan kasus crisis
            weights = CLASS_WEIGHTS.to(logits.device)
            ce   = nn.CrossEntropyLoss(weight=weights)
            loss = ce(logits, labels)

        return {"loss": loss, "logits": logits}

# ── Tokenizer ─────────────────────────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")

# ── Dataset Class ─────────────────────────────────────────────────────────
class CrisisDataset(torch.utils.data.Dataset):
    def __init__(self, df):
        self.encodings = tokenizer(
            df["text"].tolist(),
            max_length=128,         # Teks crisis biasanya pendek, 128 cukup
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        self.labels = torch.tensor(df["label"].values, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids":      self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels":         self.labels[idx],
        }

# ── Custom Trainer ────────────────────────────────────────────────────────
class CrisisTrainer(Trainer):
    """
    Override prediction_step agar kompatibel dengan output dict model kita.
    HuggingFace Trainer default mengharapkan output berupa tensor, bukan dict.
    """
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels  = inputs.pop("labels")
        outputs = model(**inputs, labels=labels)
        loss    = outputs["loss"]
        return (loss, outputs) if return_outputs else loss

    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        labels = inputs.pop("labels", None)
        with torch.no_grad():
            outputs = model(**inputs)
            loss = None
            if labels is not None:
                outputs_with_loss = model(**inputs, labels=labels)
                loss = outputs_with_loss["loss"]
        logits = outputs["logits"]
        return (loss, logits, labels)

# ── Compute Metrics ───────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    """
    Metrik utama untuk CDS Layer 2:
    - RECALL crisis  → prioritas tertinggi (jangan sampai miss kasus bahaya)
    - F1 macro       → keseimbangan antar kelas
    - Precision crisis → hindari false alarm berlebihan
    """
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    # F1 per kelas dan macro
    f1_macro = f1_score(labels, preds, average="macro", zero_division=0)
    f1_per   = f1_score(labels, preds, average=None,    zero_division=0, labels=[0,1,2])

    # Recall & Precision khusus crisis (label=2) — METRIK PALING PENTING
    recall_crisis    = recall_score(labels, preds, labels=[2], average="micro", zero_division=0)
    precision_crisis = precision_score(labels, preds, labels=[2], average="micro", zero_division=0)

    # Recall at_risk (label=1)
    recall_atrisk = recall_score(labels, preds, labels=[1], average="micro", zero_division=0)

    return {
        # ── Metrik utama ──
        "crisis_recall":    recall_crisis,      # Target > 0.85
        "crisis_precision": precision_crisis,
        "f1_macro":         f1_macro,
        # ── Per kelas ──
        "f1_safe":          f1_per[0],
        "f1_at_risk":       f1_per[1],
        "f1_crisis":        f1_per[2],
        "recall_at_risk":   recall_atrisk,
    }

# ── Training Config ───────────────────────────────────────────────────────
training_args = TrainingArguments(
    output_dir="./models/crisis_detector",
    num_train_epochs=10,            # Lebih banyak epoch karena dataset lebih kecil
    per_device_train_batch_size=16, # Turunkan ke 8 jika VRAM penuh
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.15,              # Warmup lebih panjang — stabilkan awal training
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",   # F1 macro dulu agar model belajar semua kelas
    greater_is_better=True,             # Setelah stabil, bisa ganti ke crisis_recall
    fp16=True,                      # Mixed precision — RTX 4050 support ini
    dataloader_num_workers=0,       # Windows: WAJIB 0
    report_to="none",               # Matikan wandb/tensorboard
    logging_steps=20,
    logging_dir="./logs",
    remove_unused_columns=False,
)

# ── Main ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # 1. Load dataset
    CSV_PATH = "s3_crisis/data/datasetCrisis.csv"
    df = load_data(CSV_PATH)

    # 2. Split train/val
    train_df, val_df = split_data(df)

    # 3. Buat PyTorch Dataset
    print("\nTokenizing dataset...")
    train_dataset = CrisisDataset(train_df)
    val_dataset   = CrisisDataset(val_df)
    print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)}")

    # 4. Inisialisasi model
    print("\nLoading IndoBERT...")
    model = CrisisModel(n_classes=3)
    model.to(device)
    print("Model ready")

    # 5. Trainer
    trainer = CrisisTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    # 6. Train!
    print("\nMulai training CDS Layer 2...\n")
    trainer.train()

    # 7. Simpan model final
    save_dir = "./models/crisis_detector/final"
    os.makedirs(save_dir, exist_ok=True)
    torch.save(model, f"{save_dir}/crisis_model.pt")
    tokenizer.save_pretrained(save_dir)
    print(f"\nModel tersimpan di {save_dir}/")

    # 8. Evaluasi final + laporan lengkap
    print("\nEvaluasi final pada validation set:")
    results = trainer.evaluate()

    print(f"\n   {'─'*35}")
    print(f"   Crisis Recall    : {results['eval_crisis_recall']:.4f}   ← TARGET > 0.85")
    print(f"   Crisis Precision : {results['eval_crisis_precision']:.4f}")
    print(f"   Crisis F1        : {results['eval_f1_crisis']:.4f}")
    print(f"   {'─'*35}")
    print(f"   At-Risk Recall   : {results['eval_recall_at_risk']:.4f}")
    print(f"   At-Risk F1       : {results['eval_f1_at_risk']:.4f}")
    print(f"   Safe F1          : {results['eval_f1_safe']:.4f}")
    print(f"   F1 Macro         : {results['eval_f1_macro']:.4f}")
    print(f"   {'─'*35}")

    # Classification report lengkap
    print("\nClassification Report:")
    val_preds_out = trainer.predict(val_dataset)
    preds_final = np.argmax(val_preds_out.predictions, axis=-1)
    labels_final = val_preds_out.label_ids
    print(classification_report(
        labels_final, preds_final,
        target_names=["safe", "at_risk", "crisis"],
        digits=4
    ))

    # 9. Verdict
    print("Verdict:")
    recall  = results['eval_crisis_recall']
    f1_mac  = results['eval_f1_macro']

    # Cek dulu apakah model collapse (prediksi semua sebagai satu kelas)
    unique_preds = len(set(preds_final.tolist()))
    if unique_preds == 1:
        pred_class = IDX_TO_CRISIS[int(preds_final[0])]
        print(f"Model collapse — prediksi semua sebagai '{pred_class}'")
        print(f"Fix: turunkan CLASS_WEIGHTS crisis, misal [1.0, 1.2, 1.5]")
    elif f1_mac < 0.40:
        print(f"F1 Macro {f1_mac:.2f} terlalu rendah — model belum belajar dengan baik")
        print(f"Coba:")
        print(f"1. Pastikan CLASS_WEIGHTS tidak terlalu ekstrem (max 2.0 untuk crisis)")
        print(f"2. Tambah data di kelas yang F1-nya 0")
        print(f"3. Cek apakah dataset ter-load dengan benar")
    elif recall >= 0.85 and f1_mac >= 0.60:
        print(f"Crisis Recall {recall:.2f} & F1 Macro {f1_mac:.2f} — LULUS target MVP")
    elif recall >= 0.85:
        print(f"Crisis Recall bagus ({recall:.2f}) tapi F1 Macro rendah ({f1_mac:.2f})")
        print(f"Turunkan sedikit CLASS_WEIGHTS crisis: [1.0, 1.2, 1.5]")
    elif f1_mac >= 0.60:
        print(f"F1 Macro bagus ({f1_mac:.2f}) tapi Crisis Recall kurang ({recall:.2f})")
        print(f"Naikkan sedikit CLASS_WEIGHTS crisis: [1.0, 1.3, 2.2]")
    else:
        print(f"Crisis Recall {recall:.2f} | F1 Macro {f1_mac:.2f} — perlu tuning lanjut")
        print(f"Coba training lebih lama atau sesuaikan learning_rate ke 3e-5")