from transformers import AutoTokenizer, AutoModelWithLMHead
import numpy as np
from pathlib import Path
import json
import joblib


def model_fn(model_dir):
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2", cache_dir=model_dir)
    model = AutoModelWithLMHead.from_pretrained("distilgpt2", cache_dir=model_dir)
    model_assets = {
        "tokenizer": tokenizer,
        "model": model
    }
    return model_assets


def input_fn(request_body_str, request_content_type):
    assert (
        request_content_type == "application/json"
    ), "content_type must be 'application/json'"
    request_body = json.loads(request_body_str)
    return request_body


def get_parameter(request_body, parameter_name, default):
    parameter = default
    if 'parameters' in request_body:
        if parameter_name in request_body['parameters']:
            parameter = request_body['parameters'][parameter_name]
    return parameter


def predict_fn(request_body, model_assets):
    input_text = request_body["text"]
    tokenizer = model_assets['tokenizer']
    model = model_assets['model']
    input_ids = tokenizer.encode(input_text, return_tensors='pt')
    sample_output = model.generate(
        input_ids,
        do_sample=True,
        min_length=get_parameter(request_body, 'min_length', 25),
        max_length=get_parameter(request_body, 'max_length', 100),
        top_k=0,
        temperature=get_parameter(request_body, 'temperature', 100)
    )
    output_text = tokenizer.decode(sample_output[0], skip_special_tokens=True)
    return {"text": output_text}


def output_fn(prediction, response_content_type):
    assert (
        response_content_type == "application/json"
    ), "accept must be 'application/json'"
    response_body_str = json.dumps(prediction)
    return response_body_str
