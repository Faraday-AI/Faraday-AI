def test_imports():
    print("\nTesting imports...")
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False

    try:
        import pandas as pd
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False

    try:
        import tensorflow as tf
        # Configure TensorFlow to use Metal backend
        try:
            physical_devices = tf.config.list_physical_devices('GPU')
            if physical_devices:
                for device in physical_devices:
                    tf.config.experimental.set_memory_growth(device, True)
                print("✓ TensorFlow Metal backend configured successfully")
            else:
                print("ℹ️ No Metal GPU devices found")
        except RuntimeError as e:
            print(f"ℹ️ Note: Metal backend configuration: {e}")
        print("✓ TensorFlow imported successfully")
    except ImportError as e:
        print(f"✗ TensorFlow import failed: {e}")
        return False

    try:
        import torch
        print("✓ PyTorch imported successfully")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False

    try:
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LogisticRegression
        print("✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ scikit-learn import failed: {e}")
        return False

    try:
        import matplotlib.pyplot as plt
        print("✓ Matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ Matplotlib import failed: {e}")
        return False

    try:
        import seaborn as sns
        print("✓ Seaborn imported successfully")
    except ImportError as e:
        print(f"✗ Seaborn import failed: {e}")
        return False

    try:
        import nltk
        print("✓ NLTK imported successfully")
    except ImportError as e:
        print(f"✗ NLTK import failed: {e}")
        return False

    try:
        import spacy
        print("✓ spaCy imported successfully")
    except ImportError as e:
        print(f"✗ spaCy import failed: {e}")
        return False

    try:
        from transformers import pipeline
        print("✓ Transformers imported successfully")
    except ImportError as e:
        print(f"✗ Transformers import failed: {e}")
        return False

    return True

def test_numpy():
    print("\nTesting NumPy...")
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    print(f"NumPy version: {np.__version__}")
    print(f"Array: {arr}")
    print("✓ NumPy working correctly")

def test_pandas():
    print("\nTesting Pandas...")
    import pandas as pd
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    print(f"Pandas version: {pd.__version__}")
    print(f"DataFrame:\n{df}")
    print("✓ Pandas working correctly")

def test_tensorflow():
    print("\nTesting TensorFlow...")
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
    # Create a simple model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(1, input_shape=(1,))
    ])
    # Test Metal backend
    try:
        physical_devices = tf.config.list_physical_devices('GPU')
        if physical_devices:
            print(f"✓ Metal GPU available: {physical_devices}")
        else:
            print("ℹ️ No Metal GPU devices found")
    except RuntimeError as e:
        print(f"ℹ️ Note: Metal backend status: {e}")
    print("✓ TensorFlow working correctly")

def test_pytorch():
    print("\nTesting PyTorch...")
    import torch
    print(f"PyTorch version: {torch.__version__}")
    # Create a simple tensor
    x = torch.rand(5, 3)
    print(f"Random tensor:\n{x}")
    print("✓ PyTorch working correctly")

def test_scikit_learn():
    print("\nTesting scikit-learn...")
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    # Generate sample data
    X, y = make_classification(n_samples=100, n_features=20, n_informative=15, n_redundant=5)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"Model accuracy: {score:.2f}")
    print("✓ scikit-learn working correctly")

def test_matplotlib():
    print("\nTesting Matplotlib...")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.title('Test Plot')
    plt.savefig('test_plot.png')
    plt.close()
    print("✓ Matplotlib working correctly")

def test_seaborn():
    print("\nTesting Seaborn...")
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    data = np.random.randn(100, 2)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=data[:, 0], y=data[:, 1])
    plt.savefig('test_seaborn.png')
    plt.close()
    print("✓ Seaborn working correctly")

def test_nltk():
    print("\nTesting NLTK...")
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    text = "This is a test sentence."
    tokens = nltk.word_tokenize(text)
    print(f"Tokenized text: {tokens}")
    print("✓ NLTK working correctly")

def test_spacy():
    print("\nTesting spaCy...")
    import spacy
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
    doc = nlp("This is a test sentence.")
    print(f"Named entities: {[(ent.text, ent.label_) for ent in doc.ents]}")
    print("✓ spaCy working correctly")

def test_transformers():
    print("\nTesting Transformers...")
    from transformers import pipeline
    try:
        classifier = pipeline("sentiment-analysis")
        result = classifier("I love this test!")
        print(f"Sentiment analysis result: {result}")
        print("✓ Transformers working correctly")
    except Exception as e:
        print(f"Error testing Transformers: {e}")

if __name__ == "__main__":
    print("Starting ML libraries test...")
    
    # First test all imports
    if not test_imports():
        print("\nSome imports failed. Please check the error messages above.")
        exit(1)
    
    print("\nAll imports successful. Running functionality tests...")
    
    # Then test functionality
    test_numpy()
    test_pandas()
    test_tensorflow()
    test_pytorch()
    test_scikit_learn()
    test_matplotlib()
    test_seaborn()
    test_nltk()
    test_spacy()
    test_transformers()
    
    print("\nAll tests completed!") 