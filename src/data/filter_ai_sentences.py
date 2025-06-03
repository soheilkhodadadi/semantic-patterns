# Step 1: Define AI keywords (like creating a search list)  
AI_KEYWORDS = [  
    "AI", "artificial intelligence",  
    "machine learning", "deep learning",  
    "neural network", "NLP"  
]  

# Step 2: Open the disclosure file  
with open("data/external/sample_disclosure.txt", "r") as f:  
    sentences = [line.strip() for line in f if line.strip()]  

# Step 3: Filter sentences containing AI keywords  
ai_sentences = []  
for sentence in sentences:  
    if any(keyword.lower() in sentence.lower() for keyword in AI_KEYWORDS):  
        ai_sentences.append(sentence)  

# Step 4: Save filtered sentences  
with open("data/interim/ai_sentences.txt", "w") as f:  
    f.write("\n".join(ai_sentences))  

print(f"Found {len(ai_sentences)} AI-related sentences.")  