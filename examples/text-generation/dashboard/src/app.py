import streamlit as st
import time
import json
import boto3
import os


def predict(text, min_length, max_length, temperature):
    data = {
        'text': text,
        'parameters': {
            'min_length': min_length,
            'max_length': max_length,
            'temperature': temperature
        }
    }
    sagemaker_client = boto3.client('sagemaker-runtime', region_name='us-west-2')
    try:
        response = sagemaker_client.invoke_endpoint(
            EndpointName=os.environ['DASHBOARD_SAGEMAKER_MODEL'], 
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps(data)
        )
    except sagemaker_client.exceptions.ClientError as e:
        if "ExpiredTokenException" in str(e):
            raise Exception("""
                ExpiredTokenException.
                You can refresh credentials by restarting the Docker container.
                Only occurs during development (due to passing of temporary credentials).
            """)
        else:
            raise e
    body_str = response['Body'].read().decode("utf-8")
    body = json.loads(body_str)
    return body['text']


def main():
    st.markdown("""
    # DistilGPT-2 Text Generation

    We use text generation as a simple example of interacting with
    a machine learning model from within a dashboard. Our 
    [DistilGPT-2](https://huggingface.co/distilgpt2) model has been deployed with Amazon SageMaker.

    #### Model Notes

    Our pre-trained [DistilGPT-2](https://huggingface.co/distilgpt2) model 
    is from [Hugging Face](https://huggingface.co/). It weighs 
    37% less, and is twice as fast as its OpenAI counterpart, while 
    keeping the same generative power. Originally introduced 
    in the [DistilBERT](https://arxiv.org/abs/1910.01108) paper, 
    the same method has been applied to the smallest version of GPT-2.

    #### Model Parameters

    Given a text prompt, the model will sample from likely next 
    words. You can control the *minimum length* and *maximum length* of 
    the generated text using the the sidebar controls. You can also 
    choose the sampling *temperature*: a higher temperature makes the 
    generated text more random.

    #### Model Outputs

    Choose a preset prompt below or write one from scratch...
    """)

    st.sidebar.markdown('Parameters')

    text_length = st.sidebar.slider(
        label="Select length of text:",
        min_value=20,
        max_value=200,
        value=(50, 150),
        step=1,
        format="%d words"
    )
    assert len(text_length) == 2
    assert isinstance(text_length[0], int)
    assert isinstance(text_length[1], int)

    temperature = st.sidebar.slider(
        label="Select temperature:",
        min_value=0.5,
        max_value=1.5,
        value=0.75,
        step=0.01
    )
    assert isinstance(temperature, float)

    prompt = st.selectbox(
        label='Select preset prompt:',
        options=[
            '',
            ('In a shocking finding, scientist discovered '
             'a herd of unicorns living in a remote, previously '
             'unexplored valley, in the Andes Mountains. Even more '
             'surprising to the researchers was the fact that the unicorns '
             'spoke perfect English.'),
            ('A train carriage containing controlled nuclear '
             'materials was stolen in Cincinnati today. Its whereabouts are unknown.'),
            ('Amazon SageMaker is a fully managed service that provides '
             'every developer and data scientist with the ability to '
             'build, train, and deploy machine learning (ML) models quickly.'),
        ]
    )
    assert isinstance(prompt, str)
    
    prompt = st.text_area(
        label='Write prompt:',
        value=prompt
    )
    assert isinstance(prompt, str)

    if prompt:
        with st.spinner('Generating text...'):
            text = predict(
                prompt,
                min_length=text_length[0],
                max_length=text_length[1],
                temperature=temperature
            )
        st.info(text)


if __name__ == "__main__":
    debug = os.getenv('DASHBOARD_DEBUG', 'false') == 'true'
    if debug:
        main()
    else:
        try:
            main()
        except Exception as e:
            st.error('Internal error occurred.')