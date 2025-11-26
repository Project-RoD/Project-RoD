import csv
import os

# CONFIGURATION
INPUT_FILENAME = "fullformsliste.txt"
OUTPUT_FILENAME = "ValidWords.ts"

def process_word_list():
    print(f"🚀 Starting processing of {INPUT_FILENAME}...")
    
    if not os.path.exists(INPUT_FILENAME):
        print(f"❌ Error: Could not find {INPUT_FILENAME}")
        return

    unique_words = set()
    
    # Norsk Ordbank often uses ISO-8859-1 encoding
    try:
        f = open(INPUT_FILENAME, 'r', encoding='utf-8')
        f.readline()
        f.seek(0)
    except UnicodeDecodeError:
        print("⚠️ UTF-8 failed, switching to ISO-8859-1...")
        f = open(INPUT_FILENAME, 'r', encoding='iso-8859-1')

    with f:
        # Use DictReader to automatically map columns by name (LOEPENR, OPPSLAG, etc.)
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            word = row.get('OPPSLAG')
            
            if not word:
                continue

            # 1. Clean the word
            word = word.strip().upper()

            # 2. Filter Logic
            # Must be exactly 5 letters
            if len(word) != 5:
                continue
            
            # Must be letters only
            # We verify it contains only Norwegian alphabetic characters
            if not word.isalpha():
                continue
            
            # Add to set
            unique_words.add(word)

    # Sort list for neatness
    sorted_words = sorted(list(unique_words))
    
    print(f"✅ Found {len(sorted_words)} unique 5-letter words.")
    
    # Write directly to a TypeScript file for the Frontend
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as out:
        out.write("// Auto-generated from Norsk Ordbank\n")
        out.write("export const VALID_GUESSES = [\n")
        
        # Write chunks to avoid one massive line
        chunk_size = 10
        for i in range(0, len(sorted_words), chunk_size):
            chunk = sorted_words[i:i+chunk_size]
            quoted_chunk = [f'"{w}"' for w in chunk]
            out.write("  " + ", ".join(quoted_chunk) + ",\n")
            
        out.write("];\n")

    print(f"🎉 Done! Created {OUTPUT_FILENAME}")

if __name__ == "__main__":
    process_word_list()