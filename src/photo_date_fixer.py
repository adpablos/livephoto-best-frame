from pathlib import Path
import logging
from datetime import datetime
import argparse
from .metadata_handler import MetadataHandler
from PIL import Image
import subprocess

class PhotoDateFixer:
    """Interactive command-line tool to fix photo dates"""
    
    def __init__(self):
        self._setup_logging()
        self.metadata_handler = MetadataHandler()
    
    def _setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_photos(self, directory: Path):
        """Process all photos in a directory"""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Get all jpg/jpeg files
        photos = list(directory.glob("*.[jJ][pP][gG]"))
        photos.extend(directory.glob("*.[jJ][pP][eE][gG]"))
        
        if not photos:
            self.logger.warning("No photos found in directory")
            return
        
        self.logger.info(f"Found {len(photos)} photos to process")
        
        for photo in photos:
            self._process_single_photo(photo)
    
    def _process_single_photo(self, photo_path: Path):
        """Process a single photo interactively"""
        image = None
        try:
            # Show photo info
            print("\n" + "="*50)
            print(f"Processing: {photo_path.name}")
            print(f"Current creation time: {self.metadata_handler.get_creation_time(photo_path)}")
            
            # Open image in default viewer
            image = Image.open(photo_path)
            image.show()
            
            while True:  # Loop until valid input or skip/quit
                # Show options
                print("\nEnter date (YYYY-MM-DD HH:MM) or:")
                print("'s' to skip this photo")
                print("'q' to quit program")
                
                choice = input("\nYour input: ").strip().lower()
                
                if choice == 's':
                    self.logger.info(f"Skipped {photo_path.name}")
                    break
                elif choice == 'q':
                    print("\nExiting program...")
                    if image:
                        image.close()
                    exit(0)
                else:
                    try:
                        new_datetime = datetime.strptime(choice, "%Y-%m-%d %H:%M")
                        self.metadata_handler.update_exif_dates(photo_path, new_datetime)
                        self.metadata_handler.update_file_timestamps(
                            photo_path,
                            new_datetime,
                            datetime.now()
                        )
                        self.logger.info(f"Updated {photo_path.name} to {new_datetime}")
                        break  # Exit loop after successful update
                    except ValueError:
                        print("\nInvalid date format. Please use YYYY-MM-DD HH:MM")
                        continue  # Ask for input again
                
        except Exception as e:
            self.logger.error(f"Error processing {photo_path.name}: {str(e)}")
        finally:
            # Ensure image is closed in all cases
            if image:
                image.close()
                # For macOS, try to close Preview
                subprocess.run(['osascript', '-e', 'tell application "Preview" to quit'])

def main():
    parser = argparse.ArgumentParser(
        description="Fix photo dates interactively"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing photos to process"
    )
    
    args = parser.parse_args()
    
    fixer = PhotoDateFixer()
    fixer.process_photos(args.directory)

if __name__ == "__main__":
    main() 