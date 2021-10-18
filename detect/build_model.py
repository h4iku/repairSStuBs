import json
import os
import random
from datasets.features.features import Features

import numpy as np
import pandas as pd
import torch
from datasets import Dataset, DatasetDict, Value, Features, ClassLabel
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import (AdamW, AutoModelForSequenceClassification,
                          AutoTokenizer, DataCollatorWithPadding, Trainer,
                          TrainingArguments)
# from simpletransformers.classification import ClassificationModel, ClassificationArgs
from utils.config import DATASET, EMBED_MODEL, PATCH_TOKENS, n_jobs
from utils.data_reader import ManySStuBs4J

os.environ["WANDB_DISABLED"] = "true"
os.environ['HF_DATASETS_OFFLINE'] = "1"
os.environ['TRANSFORMERS_OFFLINE'] = "1"

# TODO: Test without specifying a bug type and train on everything.
#       Using `stratify` will keep the bug types at balance.
bug_type = 'LESS_SPECIFIC_IF'

# checkpoint = 'distilbert-base-uncased'
checkpoint = 'huggingface/CodeBERTa-small-v1'

sstubs = ManySStuBs4J(DATASET).bugs
random.Random(3).shuffle(sstubs)

all_data = []
all_labels = []
for bug in sstubs:
    if bug.bug_type == bug_type:
        all_data.append(bug.source_before_fix)
        all_labels.append(1)
        all_data.append(bug.source_after_fix)
        all_labels.append(0)

nb_train = int(0.8 * len(all_data))
train_data = all_data[: nb_train]
train_labels = all_labels[:nb_train]
eval_data = all_data[nb_train:]
eval_labels = all_labels[nb_train:]

class_names = ['not buggy', 'buggy']
features = Features({'text': Value('string'),
                     'label': ClassLabel(names=class_names)})

raw_train_dataset = Dataset.from_dict(
    {'text': train_data,
     'label': train_labels},
    features=features
)
raw_val_dataset = Dataset.from_dict(
    {'text': eval_data,
     'label': eval_labels},
    features=features
)
raw_dataset = DatasetDict(train=raw_train_dataset, validation=raw_val_dataset)

print(raw_dataset['train'].features)
# import sys
# sys.exit(0)

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint,
                                                           num_labels=2)


def compute_metrics(eval_preds):
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    metrics = {
        'accuracy': accuracy_score(labels, predictions),
        'precision': precision_score(labels, predictions),
        'recall': recall_score(labels, predictions)
    }
    # print(metrics)
    return metrics


def tokenize_function(example):
    return tokenizer(example["text"], truncation=True)


tokenized_dataset = raw_dataset.map(tokenize_function, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)


training_args = TrainingArguments(
    output_dir="test-trainer",
    num_train_epochs=2,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    evaluation_strategy='epoch'  # should set evaluation_strategy to `epoch` or `steps`
    # logging_dir='./logs',
    # logging_steps=10,
)

trainer = Trainer(
    model,
    training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()

predictions = trainer.predict(tokenized_dataset["validation"])
print(predictions.predictions.shape, predictions.label_ids.shape)


preds = np.argmax(predictions.predictions, axis=-1)


acc = accuracy_score(predictions.label_ids, preds)
prec = precision_score(predictions.label_ids, preds)
rec = recall_score(predictions.label_ids, preds)
print(acc, prec, rec)
