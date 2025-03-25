import os
import re
import shutil
from datetime import datetime
import argparse

# Configuration
#OBSIDIAN_VAULT_PATH = r'C:\Users\oprio\Documents\git_obsidian\__main\notes'
#JEKYLL_POSTS_PATH = r'C:\Users\oprio\Documents\_website\_posts'
OBSIDIAN_VAULT_PATH="/mnt/c/Users/oprio/Documents/git_obsidian/__main/_notes"
JEKYLL_POSTS_PATH="/mnt/c/Users/oprio/Documents/_website/_posts"
def parse_simple_frontmatter(frontmatter_text):
    """Parse YAML frontmatter without using the yaml module."""
    result = {}
    lines = frontmatter_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Look for key-value pairs
        if ':' in line:
            key, value = [x.strip() for x in line.split(':', 1)]
            
            # Handle boolean values
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            # Handle null/None values
            elif value.lower() == 'null' or not value:
                value = None
            
            result[key] = value
    
    return result

def extract_frontmatter(content):
    """Extract and parse frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    
    try:
        return parse_simple_frontmatter(match.group(1))
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
        return None

def format_date_for_jekyll(date_string):
    """Format date as YYYY-MM-DD for Jekyll filename."""
    try:
        # Try parsing the date string
        if isinstance(date_string, str):
            # Try common date formats
            for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y'):
                try:
                    date = datetime.strptime(date_string, fmt)
                    return date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        # If we couldn't parse the string, use today's date
        return datetime.now().strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')

def slugify(title):
    """Convert title to URL-friendly slug."""
    # Remove special characters
    slug = re.sub(r'[^\w\s-]', '', str(title).lower())
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug

def process_file(file_path):
    """Process a markdown file and copy to Jekyll if publish is true."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = extract_frontmatter(content)
        
        # Skip if no frontmatter
        if not frontmatter:
            print(f"Skipping {os.path.basename(file_path)} (no frontmatter found)")
            return False
            
        # Check if publish is true
        # Since we're parsing manually, we need to handle different formats
        publish_value = frontmatter.get('publish')
        if publish_value is not True and str(publish_value).lower() != 'true':
            print(f"Skipping {os.path.basename(file_path)} (publish is not true)")
            return False
        
        # Get the title and date for the filename
        title = frontmatter.get('title') or os.path.basename(file_path).replace('.md', '')
        
        # Get the date, with fallbacks
        date = None
        for date_field in ['last_tended', 'planted']:
            if date_field in frontmatter and frontmatter[date_field]:
                date = frontmatter[date_field]
                break
                
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Format filename for Jekyll
        date_prefix = format_date_for_jekyll(date)
        slug = slugify(title)
        jekyll_filename = f"{date_prefix}-{slug}.md"
        
        # Copy the file to Jekyll _posts directory
        dest_path = os.path.join(JEKYLL_POSTS_PATH, jekyll_filename)
        shutil.copyfile(file_path, dest_path)
        
        print(f"Published: {os.path.basename(file_path)} → {jekyll_filename}")
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def process_single_file(file_path):
    """Process a specific markdown file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    return process_file(file_path)

def process_all_files():
    """Process all markdown files in the Obsidian vault."""
    published_count = 0
    
    for root, _, files in os.walk(OBSIDIAN_VAULT_PATH):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                if process_file(file_path):
                    published_count += 1
    
    print(f"Published {published_count} files to Jekyll")
    return published_count > 0

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description='Publish Obsidian notes to Jekyll.')
    parser.add_argument('--file', help='Path to a specific markdown file to process')
    args = parser.parse_args()
    
    # Ensure Jekyll _posts directory exists
    os.makedirs(JEKYLL_POSTS_PATH, exist_ok=True)
    
    if args.file:
        # Process a single file
        process_single_file(args.file)
    else:
        # Process all files
        process_all_files()