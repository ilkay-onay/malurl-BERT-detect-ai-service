# src/metrics.py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import (
    f1_score, precision_score, recall_score, accuracy_score, 
    confusion_matrix, classification_report, roc_curve, auc, 
    precision_recall_curve
)
from .config import Config

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    # Probabilities for ROC/PR curves
    # We apply softmax to logits to get actual probabilities
    probs = np.exp(logits) / np.sum(np.exp(logits), axis=-1, keepdims=True)
    phish_probs = probs[:, 1]
    
    f1 = f1_score(labels, predictions)
    precision = precision_score(labels, predictions)
    recall = recall_score(labels, predictions)
    acc = accuracy_score(labels, predictions)
    
    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

def generate_report_visuals(y_true, y_pred, y_probs, suffix="FINAL"):
    """Generates all graphs needed for a professional technical report."""
    if not os.path.exists(Config.PLOT_DIR): os.makedirs(Config.PLOT_DIR)
    
    # 1. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Safe', 'Phish'], yticklabels=['Safe', 'Phish'])
    plt.title(f'Confusion Matrix - {suffix}')
    plt.savefig(f"{Config.PLOT_DIR}/confusion_matrix_{suffix}.png")
    plt.close()

    # 2. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {suffix}')
    plt.legend(loc="lower right")
    plt.savefig(f"{Config.PLOT_DIR}/roc_curve_{suffix}.png")
    plt.close()

    # 3. Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    plt.figure()
    plt.plot(recall, precision, color='blue', lw=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Precision-Recall Curve - {suffix}')
    plt.savefig(f"{Config.PLOT_DIR}/pr_curve_{suffix}.png")
    plt.close()

    # 4. Textual Classification Report
    report = classification_report(y_true, y_pred, target_names=['Safe', 'Phish'])
    with open(f"{Config.PLOT_DIR}/classification_report_{suffix}.txt", "w") as f:
        f.write(report)
    print(f"\n\U0001f4c4 Technical report and graphs saved to {Config.PLOT_DIR}")