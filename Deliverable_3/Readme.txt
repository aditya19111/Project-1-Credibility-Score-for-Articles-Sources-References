BERT-Enhanced Hybrid Neural Network for Website Rating

**Overview**

This project implements a hybrid neural network model that integrates BERT embeddings with numerical inputs to rate the relevance and safety of websites. The model processes textual data using a pre-trained BERT (bert-base-uncased) transformer and combines its output with a separate fully connected network that processes numerical features such as URL ratings. The two outputs are concatenated and passed through additional layers to generate the final rating.

Features

BERT-based text embeddings for deep semantic understanding.

Numeric feature integration to enrich textual data.

Custom neural network architecture with regularization and dropout.

Optimized with AdamW optimizer and MSE loss for regression tasks.

Uses TensorFlow and Hugging Face Transformers.

Model Architecture

Text Processing:

Input website text is tokenized using BertTokenizer.

Passed through a pre-trained TFBertModel to extract embeddings.

Extracts the [CLS] token representation from BERT.

Fully connected layers (512 -> 256) with ReLU activation and L2 regularization.

Numerical Processing:

Single numeric input representing a URL rating.

Passed through a dense layer (64 neurons) with ReLU activation.

Fusion and Output:

The BERT output and numerical feature are concatenated.

Final dense layer produces a single numerical output representing website relevance and safety.
