# Load term lists  
def load_terms(file_path):  
    with open(file_path, "r") as f:  
        return [line.strip() for line in f if line.strip()]  

concrete_terms = load_terms("data/metadata/technical_terms/concrete_terms.txt")  
vague_terms = load_terms("data/metadata/technical_terms/vague_terms.txt")  

# Load AI sentences  
with open("data/interim/ai_sentences.txt", "r") as f:  
    ai_sentences = [line.strip() for line in f if line.strip()]  

# Score sentences  
scored_sentences = []  
for sentence in ai_sentences:  
    # Count concrete terms  
    concrete_count = sum(1 for term in concrete_terms if term.lower() in sentence.lower())  
    # Count vague terms  
    vague_count = sum(1 for term in vague_terms if term.lower() in sentence.lower())  
    # Calculate score  
    total = concrete_count + vague_count  
    score = concrete_count / total if total > 0 else 0  
    scored_sentences.append(f"{sentence} | Score: {score:.2f} (Concrete: {concrete_count}, Vague: {vague_count})")  

# Save results  
with open("data/processed/scored_sentences.txt", "w") as f:  
    f.write("\n".join(scored_sentences))  