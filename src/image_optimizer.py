import logging
import argparse
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener
from .metadata_handler import MetadataHandler

# Register HEIF opener with Pillow
register_heif_opener()

class ImageOptimizer:
    """Handles image optimization and format conversion (HEIC -> JPG)"""
    
    def __init__(self, quality: int = 85, max_dimension: int = 4000):
        self.quality = quality
        self.max_dimension = max_dimension
        self._setup_logging()
        self.metadata_handler = MetadataHandler()
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _should_resize(self, img: Image.Image) -> bool:
        """Check if image needs resizing"""
        return max(img.size) > self.max_dimension
    
    def _resize_image(self, img: Image.Image) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        ratio = self.max_dimension / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)
    
    def process_directory(self, input_dir: Path) -> None:
        """Process all images in the directory"""
        if not input_dir.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")
        
        # Create output directory
        output_dir = input_dir / "optimized_photos"
        output_dir.mkdir(exist_ok=True)
        
        # Supported extensions
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.heic', '*.HEIC', '*.JPG', '*.JPEG', '*.PNG']
        files = []
        for ext in extensions:
            files.extend(input_dir.glob(ext))
            
        if not files:
            self.logger.warning("No image files found to process")
            return
            
        self.logger.info(f"Found {len(files)} files to process")
        
        for file_path in files:
            self._process_single_file(file_path, output_dir)
            
    def _process_single_file(self, file_path: Path, output_dir: Path) -> None:
        """Process a single image file"""
        try:
            # Determine output filename (always jpg)
            output_filename = output_dir / f"{file_path.stem}.jpg"
            
            # Skip if already exists (optional, could add force flag)
            # if output_filename.exists():
            #     return

            with Image.open(file_path) as img:
                # Convert to RGB (handles RGBA pngs and weird HEIC modes)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if needed
                if self._should_resize(img):
                    img = self._resize_image(img)
                
                # Save as optimized JPEG
                img.save(
                    output_filename, 
                    "JPEG", 
                    quality=self.quality, 
                    optimize=True
                )
            
            # Copy original metadata (Most importantly creation date)
            self._copy_metadata(file_path, output_filename)
            
            self.logger.info(f"Processed: {file_path.name} -> {output_filename.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to process {file_path}: {str(e)}")

    def _copy_metadata(self, source: Path, dest: Path) -> None:
        """Copy metadata from source to destination using MetadataHandler"""
        try:
            # Get creation time
            creation_time = self.metadata_handler.get_creation_time(source)
            
            # Update EXIF and file timestamps
            self.metadata_handler.update_exif_dates(dest, creation_time)
            self.metadata_handler.update_file_timestamps(dest, creation_time)
            
        except Exception as e:
            self.logger.warning(f"Metadata copy failed for {source}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Optimize images for printing")
    parser.add_argument("input_dir", type=Path, help="Input directory")
    parser.add_argument("--quality", type=int, default=80, help="JPEG Quality (0-100)")
    parser.add_argument("--max-size", type=int, default=3000, help="Max dimension in pixels")
    
    args = parser.parse_args()
    
    optimizer = ImageOptimizer(quality=args.quality, max_dimension=args.max_size)
    optimizer.process_directory(args.input_dir)

if __name__ == "__main__":
    main()
