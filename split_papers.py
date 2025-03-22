def count_words(text):
    return len(text.split())

def write_chunk(chunk_number, content):
    output_file = f'extracted_paper{chunk_number}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created {output_file} with {count_words(content)} words')

# Read the entire file
with open('extracted_papers.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Initialize variables
current_chunk = ""
chunk_number = 1
words_per_chunk = 2500
current_words = 0

# Split the content into lines
lines = content.split('\n')

# Process line by line
for line in lines:
    # Add the line to current chunk
    current_chunk += line + '\n'
    current_words = count_words(current_chunk)
    
    # If we've reached our target word count
    if current_words >= words_per_chunk:
        # If we're in the middle of a paper section (between ===== markers),
        # continue until we find the next section break
        if "=" * 80 not in line:
            continue
            
        # Write the chunk to a file
        write_chunk(chunk_number, current_chunk)
        
        # Reset for next chunk
        current_chunk = ""
        current_words = 0
        chunk_number += 1

# Write the last chunk if there's any content left
if current_chunk.strip():
    write_chunk(chunk_number, current_chunk)

print("\nSplitting complete! Files have been created.") 