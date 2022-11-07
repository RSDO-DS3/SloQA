# Tools for evaluating the datasets

Follow these lines to create an environment for dataset evaluation.

1. Create a virtual environment

    ```python -m venv ./venv```

2. Activate the virtual environment

    ```./venv/bin/activate```

3. Upgrade pip

    ```python -m pip install --upgrade pip```

4. Install the wheel package

    ```pip install wheel```

5. Install CUDA compiled PyTorch

    ```pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117```

6. Install the transformers package with SuperGLUE support (https://github.com/W4ngatang/transformers/tree/superglue)

    ```pip install git+https://github.com/W4ngatang/transformers/@superglue```

7. Install the rest of the requirements

    ```pip install -r ./requirements.txt```

8. Place the datasets in `data/[task]` folders; `[task]` can be `boolq`, `multirc` or `record`; datasets must be in JSONL format and named `train`, `val`, `test` and `dev`

9. Run the `run_superglue.py` script (example for `boolq`):

    ```
    python run_superglue.py \
        --data_dir "data/" \
        --task_name "boolq" \
        --output_dir "results/" \
        --overwrite_output_dir \
        --model_type "bert" \
        --model_name_or_path "bert-base-uncased" \
        --do_train \
        --num_train_epochs 3 \
        --do_eval \
        --eval_and_save_steps 1500 \
        --save_only_best \
        --learning_rate 0.00001 \
        --warmup_ratio 0.06 \
        --weight_decay 0.01 \
        --use_gpuid 0 \
        --per_gpu_train_batch_size 16 \
        --per_gpu_eval_batch_size 16 \
        --gradient_accumulation_steps 8 \
        --logging_steps 100
    ```