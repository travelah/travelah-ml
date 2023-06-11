# Travelah (machine-learning Side)

## Intent Classification
This intent classification model is designed to classify user queries related to travel recommendations in Bali. It is capable of categorizing queries into three main intents: **small_talk**, **faq**, and **recommender** intent. This model is particularly useful for building chatbot systems or natural language processing (NLP) applications that assist users in finding information and recommendations about traveling in Bali.
### Model used:
* A Lite BERT(AlBERT) for embedding layer
* CNN, MaxPooling1D, and Dense for classifier layer

## Named Entity Recognition
Training a custom NER model that can identify entities such as **attractions_preferences**, **hotels_preferences**, **food_preferences**, and **region** that are relevant to travel in Bali.
### Model used:
* spaCy NER


