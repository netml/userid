import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load the mistral model and tokenizer from Hugging Face
tokenizer = AutoTokenizer.from_pretrained("mistral")
model = AutoModelForCausalLM.from_pretrained("mistral")


# Load your tokenized data from tokenized_data.csv
def load_tokenized_data(csv_file):
    df = pd.read_csv(csv_file)
    return df


# Function to process each tokenized row with Mistral
def process_with_mistral(row, model, tokenizer):
    # Join all tokenized fields into a prompt to send to Mistral
    input_data = " ".join(map(str, row))

    # Tokenize input
    inputs = tokenizer(input_data, return_tensors="pt")

    # Generate output using the Mistral model
    with torch.no_grad():
        outputs = model.generate(inputs["input_ids"], max_length=100)

    # Decode the output tokens back to text
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


# Function to iterate over the data and analyze using Mistral
def analyze_data_with_mistral(csv_file):
    df = load_tokenized_data(csv_file)

    # Process each row
    results = []
    for index, row in df.iterrows():
        result = process_with_mistral(row, model, tokenizer)
        print(f"Processed row {index + 1}: {result}")
        results.append(result)

    return results


# Main function
if __name__ == "__main__":
    csv_file = 'tokenized_data.csv'
    results = analyze_data_with_mistral(csv_file)

    # Optionally, save results to a new CSV file
    output_df = pd.DataFrame({'Processed_Text': results})
    output_df.to_csv('mistral_processed_output.csv', index=False)
    print("Processing complete. Results saved to mistral_processed_output.csv")
