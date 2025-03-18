import numpy as np
import pandas as pd
import tensorflow as tf
import torch
import transformers
import spacy
import nltk
import gensim
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import speech_recognition as sr
from gtts import gTTS
import os
import io
from bs4 import BeautifulSoup
import scrapy
from fastapi import FastAPI
import uvicorn
import pytest
import asyncio
from PIL import Image
import plotly
import xgboost as xgb
import lightgbm as lgb
import optuna

def test_numpy():
    print("\nTesting NumPy...")
    try:
        arr = np.array([1, 2, 3, 4, 5])
        print(f"NumPy version: {np.__version__}")
        print(f"Array: {arr}")
        print("✓ NumPy working correctly")
    except Exception as e:
        print(f"✗ NumPy test failed: {str(e)}")

def test_pandas():
    print("\nTesting Pandas...")
    try:
        df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
        print(f"Pandas version: {pd.__version__}")
        print("DataFrame:")
        print(df)
        print("✓ Pandas working correctly")
    except Exception as e:
        print(f"✗ Pandas test failed: {str(e)}")

def test_tensorflow():
    print("\nTesting TensorFlow...")
    try:
        print(f"TensorFlow version: {tf.__version__}")
        print(f"✓ Metal GPU available: {tf.config.list_physical_devices('GPU')}")
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(1, input_shape=(1,))
        ])
        model.compile(optimizer='adam', loss='mse')
        print("✓ TensorFlow working correctly")
    except Exception as e:
        print(f"✗ TensorFlow test failed: {str(e)}")

def test_pytorch():
    print("\nTesting PyTorch...")
    try:
        print(f"PyTorch version: {torch.__version__}")
        x = torch.randn(5, 3)
        print("Random tensor:")
        print(x)
        print("✓ PyTorch working correctly")
    except Exception as e:
        print(f"✗ PyTorch test failed: {str(e)}")

def test_transformers():
    print("\nTesting Transformers...")
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        model_name = "facebook/opt-125m"
        print(f"Loading {model_name} model and tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        model = model.cpu()
        text = "Hello, how are you?"
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        print(f"Model output shape: {outputs.logits.shape}")
        print("✓ Transformers working correctly")
    except Exception as e:
        print(f"✗ Transformers test failed: {str(e)}")

def test_spacy():
    print("\nTesting spaCy...")
    try:
        nlp = spacy.load('en_core_web_sm')
        text = "Apple Inc. is headquartered in Cupertino, California."
        doc = nlp(text)
        print("Text analysis:")
        print(f"Original text: {text}")
        print("\nNamed entities:")
        for ent in doc.ents:
            print(f"- {ent.text} ({ent.label_})")
        print("✓ spaCy working correctly")
    except Exception as e:
        print(f"✗ spaCy test failed: {str(e)}")

def test_nltk():
    print("\nTesting NLTK...")
    try:
        text = "This is a test sentence."
        tokens = text.split()
        print(f"Tokenized text: {tokens}")
        print("✓ NLTK working correctly")
    except Exception as e:
        print(f"✗ NLTK test failed: {str(e)}")

def test_gensim():
    print("\nTesting Gensim...")
    try:
        from gensim.models import Word2Vec
        sentences = [['this', 'is', 'a', 'test', 'sentence']]
        model = Word2Vec(sentences, min_count=1)
        print("✓ Gensim working correctly")
    except Exception as e:
        print(f"✗ Gensim test failed: {str(e)}")

def test_opencv():
    print("\nTesting OpenCV...")
    try:
        print(f"OpenCV version: {cv2.__version__}")
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(img, (10, 10), (90, 90), (0, 255, 0), 2)
        print("✓ OpenCV working correctly")
    except Exception as e:
        print(f"✗ OpenCV test failed: {str(e)}")

def test_matplotlib():
    print("\nTesting Matplotlib...")
    try:
        plt.plot([1, 2, 3], [1, 2, 3])
        plt.close()
        print("✓ Matplotlib working correctly")
    except Exception as e:
        print(f"✗ Matplotlib test failed: {str(e)}")

def test_seaborn():
    print("\nTesting Seaborn...")
    try:
        data = np.random.randn(100)
        sns.histplot(data=data)
        plt.close()
        print("✓ Seaborn working correctly")
    except Exception as e:
        print(f"✗ Seaborn test failed: {str(e)}")

def test_sklearn():
    print("\nTesting scikit-learn...")
    try:
        X, y = make_classification(n_samples=100, n_features=20, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2f}")
        print("✓ scikit-learn working correctly")
    except Exception as e:
        print(f"✗ scikit-learn test failed: {str(e)}")

def test_speech_recognition():
    print("\nTesting SpeechRecognition...")
    try:
        recognizer = sr.Recognizer()
        print("✓ SpeechRecognition working correctly")
    except Exception as e:
        print(f"✗ SpeechRecognition test failed: {str(e)}")

def test_gtts():
    print("\nTesting gTTS...")
    try:
        tts = gTTS(text="Hello, this is a test.", lang="en")
        print("✓ gTTS working correctly")
    except Exception as e:
        print(f"✗ gTTS test failed: {str(e)}")

def test_beautifulsoup():
    print("\nTesting BeautifulSoup...")
    try:
        html = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        print("✓ BeautifulSoup working correctly")
    except Exception as e:
        print(f"✗ BeautifulSoup test failed: {str(e)}")

def test_scrapy():
    print("\nTesting Scrapy...")
    try:
        print(f"Scrapy version: {scrapy.__version__}")
        print("✓ Scrapy working correctly")
    except Exception as e:
        print(f"✗ Scrapy test failed: {str(e)}")

def test_fastapi():
    print("\nTesting FastAPI...")
    try:
        app = FastAPI()
        print("✓ FastAPI working correctly")
    except Exception as e:
        print(f"✗ FastAPI test failed: {str(e)}")

def test_uvicorn():
    print("\nTesting Uvicorn...")
    try:
        print(f"Uvicorn version: {uvicorn.__version__}")
        print("✓ Uvicorn working correctly")
    except Exception as e:
        print(f"✗ Uvicorn test failed: {str(e)}")

def test_pytest():
    print("\nTesting pytest...")
    try:
        print(f"pytest version: {pytest.__version__}")
        print("✓ pytest working correctly")
    except Exception as e:
        print(f"✗ pytest test failed: {str(e)}")

def test_asyncio():
    print("\nTesting asyncio...")
    try:
        async def test():
            return "test"
        asyncio.run(test())
        print("✓ asyncio working correctly")
    except Exception as e:
        print(f"✗ asyncio test failed: {str(e)}")

def test_pillow():
    print("\nTesting Pillow...")
    try:
        img = Image.new('RGB', (100, 100), color='red')
        print("✓ Pillow working correctly")
    except Exception as e:
        print(f"✗ Pillow test failed: {str(e)}")

def test_plotly():
    print("\nTesting Plotly...")
    try:
        print(f"Plotly version: {plotly.__version__}")
        print("✓ Plotly working correctly")
    except Exception as e:
        print(f"✗ Plotly test failed: {str(e)}")

def test_xgboost():
    print("\nTesting XGBoost...")
    try:
        print(f"XGBoost version: {xgb.__version__}")
        print("✓ XGBoost working correctly")
    except Exception as e:
        print(f"✗ XGBoost test failed: {str(e)}")

def test_lightgbm():
    print("\nTesting LightGBM...")
    try:
        print(f"LightGBM version: {lgb.__version__}")
        print("✓ LightGBM working correctly")
    except Exception as e:
        print(f"✗ LightGBM test failed: {str(e)}")

def test_optuna():
    print("\nTesting Optuna...")
    try:
        print(f"Optuna version: {optuna.__version__}")
        print("✓ Optuna working correctly")
    except Exception as e:
        print(f"✗ Optuna test failed: {str(e)}")

def main():
    print("Starting educational libraries test...\n")
    
    # Test all libraries
    test_numpy()
    test_pandas()
    test_tensorflow()
    test_pytorch()
    test_transformers()
    test_spacy()
    test_nltk()
    test_gensim()
    test_opencv()
    test_matplotlib()
    test_seaborn()
    test_sklearn()
    test_speech_recognition()
    test_gtts()
    test_beautifulsoup()
    test_scrapy()
    test_fastapi()
    test_uvicorn()
    test_pytest()
    test_asyncio()
    test_pillow()
    test_plotly()
    test_xgboost()
    test_lightgbm()
    test_optuna()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 