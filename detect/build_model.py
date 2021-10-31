import itertools

import numpy as np
from datasets import ClassLabel, Dataset, DatasetDict, Features, Value
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          DataCollatorWithPadding, Trainer, TrainingArguments)
from utils.config import DATASET, DETECT_RESULT
from utils.data_reader import ManySStuBs4J


ignored_bug_types = [
    'CHANGE_MODIFIER',
    'ADD_THROWS_EXCEPTION',
    'DELETE_THROWS_EXCEPTION',
]

checkpoint = 'huggingface/CodeBERTa-small-v1'

sstubs = ManySStuBs4J(DATASET).bugs

all_data = [(bug.source_before_fix, bug.source_after_fix)
            for bug in sstubs if bug.bug_type not in ignored_bug_types]
all_labels = list(itertools.repeat((1, 0), len(all_data)))
bug_types = [bug.bug_type for bug in sstubs
             if bug.bug_type not in ignored_bug_types]

train_data, test_data, train_labels, test_labels = train_test_split(
    all_data, all_labels, test_size=0.2, random_state=42, stratify=bug_types)

train_data = itertools.chain.from_iterable(train_data)
train_labels = itertools.chain.from_iterable(train_labels)
test_data = itertools.chain.from_iterable(test_data)
test_labels = itertools.chain.from_iterable(test_labels)

class_names = ['not_buggy', 'buggy']
features = Features({'text': Value('string'),
                     'label': ClassLabel(names=class_names)})

raw_train_dataset = Dataset.from_dict(
    {'text': train_data,
     'label': train_labels},
    features=features,
)
raw_val_dataset = Dataset.from_dict(
    {'text': test_data,
     'label': test_labels},
    features=features,
)
raw_dataset = DatasetDict(train=raw_train_dataset, validation=raw_val_dataset)

tokenizer = AutoTokenizer.from_pretrained(checkpoint)


def model_init():
    return AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)


def compute_metrics(eval_preds):
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    metrics = {
        'accuracy': accuracy_score(labels, predictions),
        'precision': precision_score(labels, predictions),
        'recall': recall_score(labels, predictions),
        'f1-score': f1_score(labels, predictions),
    }
    return metrics


def tokenize_function(example):
    return tokenizer(example["text"], truncation=True)


tokenized_dataset = raw_dataset.map(tokenize_function, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)


training_args = TrainingArguments(
    output_dir=DETECT_RESULT,
    num_train_epochs=10,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    learning_rate=5e-5,
    weight_decay=0.01,
    evaluation_strategy='epoch',
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model='f1-score',
    report_to="none",
)

trainer = Trainer(
    model_init=model_init,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()

# Run evaluation and get best model's metrics
evaluation_metrics = trainer.evaluate()
print(evaluation_metrics)
