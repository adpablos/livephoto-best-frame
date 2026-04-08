from pathlib import Path
import logging
import argparse
from datetime import datetime
from .metadata_handler import MetadataHandler

class PhotoMetadataHomogenizer:
    """Handles homogenization of photo metadata timestamps"""
    
    def __init__(self):
        self._setup_logging()
        self.metadata_handler = MetadataHandler()
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_image(self, image_path: Path) -> None:
        """Process a single image to homogenize its metadata"""
        try:
            # Get original creation time
            original_time = self.metadata_handler.get_creation_time(image_path)
            current_time = datetime.now()
            
            # Update EXIF dates
            self.metadata_handler.update_exif_dates(image_path, original_time)
            
            # Update file timestamps
            self.metadata_handler.update_file_timestamps(
                image_path, original_time, current_time
            )
            
            self.logger.info(
                f"Updated timestamps for {image_path}. "
                f"Creation time: {original_time}, "
                f"Modified time: {current_time}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process {image_path}: {str(e)}")
    
    def process_directory(self, directory: Path) -> None:
        """Process all images in a directory"""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        image_files = list(directory.glob("*.[jJ][pP][gG]"))
        image_files.extend(directory.glob("*.[jJ][pP][eE][gG]"))
        
        if not image_files:
            self.logger.warning("No image files found")
            return
        
        for image_file in image_files:
            self.process_image(image_file)

def main():
    parser = argparse.ArgumentParser(
        description="Homogenize metadata timestamps in photos"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing the photos to process"
    )
    
    args = parser.parse_args()
    
    homogenizer = PhotoMetadataHomogenizer()
    homogenizer.process_directory(args.directory)

if __name__ == "__main__":
    main() 