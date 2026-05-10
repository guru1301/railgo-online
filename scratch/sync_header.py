import os
from bs4 import BeautifulSoup

def main():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    index_path = os.path.join(base_dir, 'index.html')
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index_soup = BeautifulSoup(f, 'html.parser')
    
    # Extract header from index.html
    header = index_soup.find('header', class_='header')
    if not header:
        print("Header not found in index.html!")
        return

    # Extract sidebar script from index.html (just in case they need the menu toggle)
    # The user only asked for the header, but the header has a toggle button.
    # I will ONLY replace the header HTML as requested by the user.

    target_files = [
        'book.html', 'bookings.html', 'confirmation.html',
        'login.html', 'pnr.html', 'signup.html',
        'track-train.html', 'trains.html'
    ]
    
    for filename in target_files:
        file_path = os.path.join(base_dir, filename)
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        old_header = soup.find('header', class_='header')
        if old_header:
            old_header.replace_with(BeautifulSoup(str(header), 'html.parser'))
        elif soup.body:
            soup.body.insert(0, BeautifulSoup(str(header), 'html.parser'))
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
    print("Header sync complete.")

if __name__ == "__main__":
    main()
