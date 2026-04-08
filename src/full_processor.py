import logging
import argparse
import shutil
from pathlib import Path
from collections import defaultdict
from .frame_extractor import FrameExtractor, VideoConfig
from .image_optimizer import ImageOptimizer

class FullProcessor:
    """Combines frame extraction and image optimization with duplicate handling"""
    
    def __init__(self, quality: int = 80, max_dimension: int = 2000):
        self._setup_logging()
        self.quality = quality
        self.max_dimension = max_dimension
        self.optimizer = ImageOptimizer(quality=quality, max_dimension=max_dimension)
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _get_file_groups(self, input_dir: Path):
        """Groups files by their base name (stem)"""
        groups = defaultdict(lambda: {'images': [], 'videos': []})
        
        img_exts = {'.jpg', '.jpeg', '.heic', '.png', '.JPG', '.JPEG', '.HEIC', '.PNG'}
        vid_exts = {'.mp4', '.mov', '.MP4', '.MOV'}
        
        for f in input_dir.iterdir():
            if f.is_file():
                ext = f.suffix
                stem = f.stem
                if ext in img_exts:
                    groups[stem]['images'].append(f)
                elif ext in vid_exts:
                    groups[stem]['videos'].append(f)
        return groups

    def process_directory(self, input_dir: Path) -> None:
        """Process files avoiding duplicates for Live Photos"""
        input_dir = Path(input_dir).resolve()
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # 1. Setup Output Directory
        output_dir = input_dir / "homogenized_output"
        output_dir.mkdir(exist_ok=True)
        
        # 2. Group files by stem
        groups = self._get_file_groups(input_dir)
        self.logger.info(f"Found {len(groups)} unique file stems to evaluate.")

        # 3. Process groups
        temp_dir = input_dir / "temp_extracted_frames"
        
        for stem, group in groups.items():
            # Preference: 
            # 1. If we have a static image (HEIC/JPG), we use that (Higher quality).
            # 2. If we ONLY have a video, we extract the best frame.
            
            if group['images']:
                # Case: Live Photo or Single Photo
                # We process the first image found for this stem (usually only one anyway)
                self.logger.info(f"Processing static image for stem: {stem}")
                img_path = group['images'][0]
                self.optimizer._process_single_file(img_path, output_dir)
                
                if group['videos']:
                    self.logger.info(f"  (Skipping video extraction for {stem} as static image exists)")
            
            elif group['videos']:
                # Case: Video Only
                self.logger.info(f"Extracting frame for video-only stem: {stem}")
                vid_path = group['videos'][0]
                
                temp_frames_dir = temp_dir / stem
                video_config = VideoConfig(input_path=input_dir, output_path=temp_frames_dir)
                extractor = FrameExtractor(video_config)
                
                if extractor.extract_best_frame(vid_path):
                    # Find the extracted file (it will have _best_frame suffix)
                    for extracted in temp_frames_dir.glob("*.jpg"):
                        # Optimize and save to final output
                        # We use the original stem to avoid the "_best_frame" in the final name
                        # But image_optimizer._process_single_file uses the file_path.stem
                        # So we can just move/rename it locally first if we want consistency
                        self.optimizer._process_single_file(extracted, output_dir)
                        
                        # Clean up the suffix in the final folder if desired
                        final_suffix_name = output_dir / f"{extracted.stem}.jpg"
                        clean_name = output_dir / f"{stem}.jpg"
                        if final_suffix_name.exists() and final_suffix_name != clean_name:
                            if clean_name.exists():
                                clean_name.unlink()
                            final_suffix_name.rename(clean_name)
                
                # Cleanup temp frames for this video
                if temp_frames_dir.exists():
                    shutil.rmtree(temp_frames_dir)

        # 4. Final Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        self.logger.info(f"DONE! All homogenized images are in: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Full Image and Video Processor (No Duplicates)")
    parser.add_argument("input_dir", type=Path, help="Input directory")
    parser.add_argument("--quality", type=int, default=80, help="JPEG Quality (0-100)")
    parser.add_argument("--max-size", type=int, default=2000, help="Max dimension in pixels")
    
    args = parser.parse_args()
    
    processor = FullProcessor(quality=args.quality, max_dimension=args.max_size)
    processor.process_directory(args.input_dir)

if __name__ == "__main__":
    main()
