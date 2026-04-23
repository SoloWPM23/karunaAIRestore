# s3_crisis/cds_layer2.py
# Inference Layer 2 — IndoBERT crisis detector
# Load model hasil training dan prediksi level krisis dari teks

import torch
from transformers import AutoTokenizer
from dataclasses import dataclass

# ── Konstanta ─────────────────────────────────────────────────────────────
MODEL_DIR   = "./models/crisis_detector/final"
MAX_LENGTH  = 128
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

IDX_TO_LABEL = {0: "safe", 1: "at_risk", 2: "crisis"}

# Map output Layer 2 → level CDS yang sama dengan Layer 1
# safe     → NORMAL
# at_risk  → L2  (distress tinggi, perlu perhatian)
# crisis   → L3  (bahaya, perlu intervensi)
LABEL_TO_LEVEL = {
    "safe":    "NORMAL",
    "at_risk": "L2",
    "crisis":  "L3",
}

# ── Output dataclass ───────────────────────────────────────────────────────
@dataclass
class Layer2Result:
    label     : str    # "safe" / "at_risk" / "crisis"
    level     : str    # "NORMAL" / "L2" / "L3"
    confidence: float  # probabilitas kelas yang diprediksi (0.0 – 1.0)
    probs     : dict   # probabilitas semua kelas

# ── Model loader (singleton — load sekali, pakai berkali-kali) ────────────
_model     = None
_tokenizer = None

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

def _load_model():
    """
    Load model dan tokenizer dari disk.
    Dipanggil sekali saat pertama kali layer2_detect dijalankan.
    """
    global _model, _tokenizer

    if _model is not None:
        return  # Sudah di-load sebelumnya

    import os
    if not os.path.exists(MODEL_DIR):
        raise FileNotFoundError(
            f"Model tidak ditemukan di '{MODEL_DIR}'.\n"
            f"Jalankan training dulu: python s3_crisis/train_crisis.py"
        )

    print(f"[CDS-L2] Loading model dari {MODEL_DIR} ({DEVICE})...")
    # CrisisModel was pickled from __main__ in train_crisis.py;
    # patch __main__ so torch.load can resolve the class.
    import __main__
    from s3_crisis.train_crisis import CrisisModel
    __main__.CrisisModel = CrisisModel

    _model     = torch.load(f"{MODEL_DIR}/crisis_model.pt", map_location=DEVICE, weights_only=False)
    _patch_bert_config(_model)
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    _model.eval()
    print(f"[CDS-L2] Model ready")

# ── Fungsi utama ───────────────────────────────────────────────────────────
def layer2_detect(text: str) -> Layer2Result:
    """
    Prediksi level krisis dari teks menggunakan IndoBERT.

    Args:
        text: Teks input dari user (satu pesan / utterance)

    Returns:
        Layer2Result dengan label, level CDS, confidence, dan semua probabilitas
    """
    _load_model()

    # Tokenisasi
    inputs = _tokenizer(text, max_length=MAX_LENGTH, padding="max_length", truncation=True, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items() if k in ("input_ids", "attention_mask")}

    # Inferensi
    with torch.no_grad():
        outputs = _model(**inputs)
        logits  = outputs["logits"]                          # shape: (1, 3)
        probs   = torch.softmax(logits, dim=-1)[0]           # shape: (3,)

    # Ambil prediksi
    pred_idx    = int(torch.argmax(probs).item())
    pred_label  = IDX_TO_LABEL[pred_idx]
    pred_level  = LABEL_TO_LEVEL[pred_label]
    confidence  = float(probs[pred_idx].item())

    prob_dict = {
        IDX_TO_LABEL[i]: round(float(probs[i].item()), 4)
        for i in range(3)
    }

    return Layer2Result(
        label=pred_label,
        level=pred_level,
        confidence=confidence,
        probs=prob_dict,
    )


# ── Quick test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        ("gue capek kerjaan numpuk tapi masih oke kok",          "safe"),
        ("udah lama gue ngerasa gak ada gunanya buat terus coba", "at_risk"),
        ("gue mau mengakhiri semuanya, udah gak kuat",            "crisis"),
        ("hari ini seru banget, abis jalan sama temen-temen",     "safe"),
        ("rasanya semua orang bakal lebih baik tanpa gue ada",    "crisis"),
    ]

    print("=" * 60)
    print("CDS Layer 2 — Quick Test")
    print("=" * 60)
    for text, expected in test_cases:
        result = layer2_detect(text)
        status = "PASS" if result.label == expected else "FAIL"
        print(f"\n{status} Input   : {text[:55]}")
        print(f"   Prediksi : {result.label:8s} (expected: {expected})")
        print(f"   Level    : {result.level}")
        print(f"   Conf     : {result.confidence:.3f}")
        print(f"   Probs    : safe={result.probs['safe']:.3f} "
              f"at_risk={result.probs['at_risk']:.3f} "
              f"crisis={result.probs['crisis']:.3f}")