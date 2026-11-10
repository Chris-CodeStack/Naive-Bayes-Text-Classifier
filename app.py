import csv
import math
import re
from collections import defaultdict

vocab = set()
prior_probs = {"positive": 0.0, "negative": 0.0}

word_counts = {
    "positive": defaultdict(int),
    "negative": defaultdict(int)
}
total_words = {"positive": 0, "negative": 0}

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def get_word_likelihood(word, label):
    count_w_c = word_counts[label][word]
    N_c = total_words[label]
    V_size = len(vocab)
    
    return (count_w_c + 1) / (N_c + V_size)

def train_model(train_file="data/train.csv"):
    global vocab, prior_probs, word_counts, total_words
    
    vocab.clear()
    word_counts["positive"].clear()
    word_counts["negative"].clear()
    total_words["positive"] = 0
    total_words["negative"] = 0
    
    sentence_counts = {"positive": 0, "negative": 0}
    total_sentences = 0
    
    try:
        with open(train_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row['text']
                label = row['label']
                
                sentence_counts[label] += 1
                total_sentences += 1
                
                tokens = tokenize(text)
                for token in tokens:
                    vocab.add(token)
                    word_counts[label][token] += 1
                    total_words[label] += 1
    except FileNotFoundError:
        print(f"Error: Could not find {train_file}.")
        return

    prior_probs["positive"] = sentence_counts["positive"] / total_sentences
    prior_probs["negative"] = sentence_counts["negative"] / total_sentences
    
    print("\n--- Training Complete ---")
    print(f"Total Sentences: {total_sentences} ({sentence_counts['positive']} Positive, {sentence_counts['negative']} Negative)")
    print(f"Vocabulary Size (|V|): {len(vocab)} unique words")
    print("-------------------------")

def predict(text):
    tokens = tokenize(text)
    
    score_pos = math.log(prior_probs["positive"])
    score_neg = math.log(prior_probs["negative"])
    
    for word in tokens:
        if word in vocab:
            score_pos += math.log(get_word_likelihood(word, "positive"))
            score_neg += math.log(get_word_likelihood(word, "negative"))
            
    if score_pos > score_neg:
        return "positive"
    elif score_neg > score_pos:
        return "negative"
    else:
        if prior_probs["positive"] > prior_probs["negative"]:
            return "positive"
        elif prior_probs["negative"] > prior_probs["positive"]:
            return "negative"
        else:
            return "positive"

def evaluate_model(test_file="data/test.csv"):
    correct_predictions = 0
    total_predictions = 0
    
    cm = {
        "true_positive": 0,
        "false_positive": 0,
        "true_negative": 0,
        "false_negative": 0
    }
    
    try:
        with open(test_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row['text']
                actual_label = row['label']
                
                predicted_label = predict(text)
                total_predictions += 1
                
                if predicted_label == actual_label:
                    correct_predictions += 1
                    if actual_label == "positive":
                        cm["true_positive"] += 1
                    else:
                        cm["true_negative"] += 1
                else:
                    if predicted_label == "positive":
                        cm["false_positive"] += 1
                    else:
                        cm["false_negative"] += 1
                        
    except FileNotFoundError:
        print(f"Error: Could not find {test_file}.")
        return {"accuracy": 0.0, "confusion_matrix": cm}
        
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "confusion_matrix": cm
    }

if __name__ == "__main__":
    train_model()
    
    print("--- Evaluating Model on Test Set ---")
    metrics = evaluate_model()
    print(f"Accuracy: {metrics['accuracy'] * 100:.1f}%")
    print("Confusion Matrix:")
    print(f"  True Positives (TP):  {metrics['confusion_matrix']['true_positive']}")
    print(f"  False Positives (FP): {metrics['confusion_matrix']['false_positive']}")
    print(f"  True Negatives (TN):  {metrics['confusion_matrix']['true_negative']}")
    print(f"  False Negatives (FN): {metrics['confusion_matrix']['false_negative']}")
    print("------------------------------------")
    
    print("\n[Interactive Prediction Mode]")
    print("Type a sentence to classify it. Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\nEnter text: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            if user_input.strip() == "":
                continue
                
            result = predict(user_input)
            print(f">>> Prediction: {result}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break