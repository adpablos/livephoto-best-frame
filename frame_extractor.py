import cv2
import os
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import argparse

@dataclass
class VideoConfig:
    """Configuration class for video processing parameters"""
    input_path: Path
    output_path: Optional[Path] = None  # Now optional
    output_format: str = "jpg"

    def __post_init__(self):
        """Set default output path if none provided"""
        if self.output_path is None:
            self.output_path = self.input_path / "extracted_frames"

class FrameExtractor:
    """Handles the extraction of frames from video files"""
    
    def __init__(self, config: VideoConfig):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging settings"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist"""
        self.config.output_path.mkdir(parents=True, exist_ok=True)
    
    def extract_best_frame(self, video_path: Path) -> Optional[bool]:
        """
        Extract the best frame from a video file based on a sharpness metric.
        
        Args:
            video_path: Path to the video file.
            
        Returns:
            bool: True if successful, False if failed, None if video couldn't be opened.
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                self.logger.error(f"Could not open video file: {video_path}")
                return None
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if frame_count == 0:
                self.logger.warning(f"No frames found in video file: {video_path}")
                return False
            
            best_sharpness = -1.0
            best_frame = None
            best_frame_index = 0
            
            current_index = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert frame to grayscale for Laplacian
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Compute the Laplacian (sharpness measure)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                if laplacian_var > best_sharpness:
                    best_sharpness = laplacian_var
                    best_frame = frame.copy()
                    best_frame_index = current_index
                
                current_index += 1
            
            if best_frame is None:
                # Si no hemos podido recuperar ningún frame
                self.logger.error(f"No valid frame extracted for: {video_path}")
                return False
            
            # Generamos la ruta de salida
            output_filename = self._generate_output_filename(video_path)
            cv2.imwrite(str(output_filename), best_frame)
            self.logger.info(
                f"Successfully saved best frame (index={best_frame_index}, sharpness={best_sharpness:.2f}) "
                f"to: {output_filename}"
            )
            return True
        
        except Exception as e:
            self.logger.error(f"Error processing {video_path}: {str(e)}")
            return False
        finally:
            cap.release()
    
    def _generate_output_filename(self, video_path: Path) -> Path:
        """Generate output filename for the extracted frame"""
        return self.config.output_path / f"{video_path.stem}_best_frame.{self.config.output_format}"
    
    def process_directory(self) -> None:
        """Process all video files in the input directory"""
        if not self.config.input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {self.config.input_path}")
        
        # Buscamos archivos MP4 en mayúsculas o minúsculas
        video_files = list(self.config.input_path.glob("*.[mM][pP]4"))
        
        if not video_files:
            self.logger.warning("No MP4 files found in input directory")
            return
        
        # Creamos el directorio de salida solo si hay archivos que procesar
        self._ensure_output_directory()
        
        for video_file in video_files:
            self.extract_best_frame(video_file)

def parse_arguments() -> VideoConfig:
    """Parse command line arguments and return VideoConfig"""
    parser = argparse.ArgumentParser(
        description="Extract central frames from videos in a directory",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_path",
        type=Path,
        help="Directory containing the video files"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory for frames (default: input_path/extracted_frames)",
        default=None
    )
    
    parser.add_argument(
        "-f", "--format",
        help="Output image format",
        default="jpg",
        choices=["jpg", "png"]
    )
    
    args = parser.parse_args()
    
    return VideoConfig(
        input_path=args.input_path,
        output_path=args.output,
        output_format=args.format
    )

def main():
    """Main entry point of the script"""
    try:
        config = parse_arguments()
        extractor = FrameExtractor(config)
        extractor.process_directory()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
