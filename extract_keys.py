import json
import os
from glob import glob

def extract_metadata_keys():
    topics = set()
    concepts = set()
    
    question_files = glob("data/questions_*.json")
    
    for file_path in question_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                
                if isinstance(data, dict) and "meta" in data and data["meta"] and "topic" in data["meta"]:
                    if data["meta"]["topic"]:
                        topics.add(data["meta"]["topic"])
                
                questions = []
                if isinstance(data, list):
                    questions = data
                elif isinstance(data, dict) and "questions" in data:
                    questions = data["questions"]

                for q in questions:
                    if "topic" in q and q["topic"]:
                        topics.add(q["topic"])
                    if "concept" in q and q["concept"]:
                        concepts.add(q["concept"])
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON file: {file_path}")
                continue

    print("--- Topics ---")
    for topic in sorted(list(topics)):
        print(topic)
        
    print("\n--- Concepts ---")
    for concept in sorted(list(concepts)):
        print(concept)

extract_metadata_keys()
