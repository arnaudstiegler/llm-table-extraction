import json
from functools import partial

import bitsandbytes as bnb
import torch
from accelerate import Accelerator
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoProcessor,
    BitsAndBytesConfig,
    PaliGemmaForConditionalGeneration,
    Trainer,
    TrainingArguments,
)


# Have to declare before model initialization because of deepspeed
args = TrainingArguments(
    output_dir="/home/ubuntu/out/",
    num_train_epochs=2,
    remove_unused_columns=False,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=1,
    warmup_steps=2,
    learning_rate=1e-4,
    weight_decay=1e-6,
    adam_beta2=0.999,
    logging_steps=1,
    optim="adamw_bnb_8bit",
    save_strategy="steps",
    save_steps=1000,
    push_to_hub=False,
    save_total_limit=1,
    bf16=True,
    deepspeed = 'pali_gemma/deepspeed_config.json',
    # report_to=["tensorboard"],
    dataloader_pin_memory=False,
    # FSDP arguments
    # fsdp='full_shard',
    # Torch compile fails for now
    # torch_compile=True,
    # torch_compile_backend='inductor'
)

model_id = "google/paligemma-3b-pt-448"
processor = AutoProcessor.from_pretrained(model_id)


# TODO: should remove that
def collate_fn(processor: AutoProcessor, examples):
    texts = ["Process " for _ in examples]
    labels = [
        json.dumps({k: v for k, v in example.items() if k != "image"})
        for example in examples
    ]
    images = [example["image"].convert("RGB") for example in examples]
    tokens = processor(
        text=texts,
        images=images,
        suffix=labels,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128,
        tokenize_newline_separately=False,
    )
    return tokens


collate = partial(collate_fn, processor)

dataset = load_dataset("arnaudstiegler/synthetic_us_passports_easy")

processor.max_length = 128


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16
)

lora_config = LoraConfig(
    r=8,
    target_modules=[
        "q_proj",
        "o_proj",
        "k_proj",
        "v_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    task_type="CAUSAL_LM",
)
model = PaliGemmaForConditionalGeneration.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    # device_map={'':torch.cuda.current_device()}
    device_map={"": Accelerator().process_index},
)
model.gradient_checkpointing_enable()
model.enable_input_require_grads()
model = get_peft_model(model, lora_config)
prepare_model_for_kbit_training(model)
print(model.print_trainable_parameters())
optimizer = bnb.optim.Adam8bit(model.parameters(), lr=1e-4)

trainer = Trainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    data_collator=collate,
    args=args,
)
print(trainer.is_model_parallel)

with torch.autocast("cuda"):
    trainer.train()
